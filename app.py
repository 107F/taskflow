import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

# Root route
@app.route("/")
@login_required
def index():
    """Redirect to tasks page"""
    return redirect("/tasks")

# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation password matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Hash the user's password
        hash_pw = generate_password_hash(request.form.get("password"))

        # Insert the new user into the database
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                         (request.form.get("username"), hash_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            return apology("username already exists", 400)
        finally:
            conn.close()

        # Redirect user to login page
        return redirect("/login")

    else:
        return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users WHERE username = ?",
                            (request.form.get("username"),)).fetchall()
        conn.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to tasks page
        return redirect("/tasks")

    else:
        return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/login")

# Tasks route
@app.route("/tasks")
@login_required
def tasks():
    """Show all tasks"""
    conn = get_db_connection()
    tasks = conn.execute("""
        SELECT tasks.*, pos.pos_name 
        FROM tasks 
        JOIN pos ON tasks.pos_id = pos.pos_id
    """).fetchall()
    pos_data = conn.execute("SELECT * FROM pos").fetchall()
    conn.close()
    return render_template("tasks.html", tasks=tasks, pos_data=pos_data)

# Route to filter tasks based on POS ID, POS Name, and search query
@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """Filter tasks based on POS ID, POS Name, and search query"""
    data = request.get_json()
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name")
    search_query = data.get("search_query")

    conn = get_db_connection()
    
    query = """
        SELECT tasks.*, pos.pos_name 
        FROM tasks 
        JOIN pos ON tasks.pos_id = pos.pos_id 
        WHERE 1=1
    """
    params = []

    if pos_id:
        query += " AND tasks.pos_id = ?"
        params.append(pos_id)
    
    if pos_name:
        query += " AND pos.pos_name = ?"
        params.append(pos_name)
    
    if search_query:
        query += " AND (tasks.description LIKE ? OR tasks.notes LIKE ?)"
        params.append(f'%{search_query}%')
        params.append(f'%{search_query}%')

    tasks = conn.execute(query, params).fetchall()
    conn.close()

    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks=tasks_list)

# Kanban route
@app.route("/kanban")
@login_required
def kanban():
    """Show Kanban board"""
    conn = get_db_connection()
    tasks = conn.execute("""
        SELECT tasks.*, pos.pos_name 
        FROM tasks 
        JOIN pos ON tasks.pos_id = pos.pos_id
    """).fetchall()
    conn.close()
    return render_template("kanban.html", tasks=tasks)

# Create task route
@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new task"""
    conn = get_db_connection()
    pos_data = conn.execute("SELECT * FROM pos").fetchall()
    conn.close()

    if request.method == "POST":
        pos_id = request.form.get("pos_id")
        reconciliation_date = request.form.get("reconciliation_date")
        certified = request.form.get("certified").lower() == 'true'
        description = request.form.get("description")
        status = request.form.get("status")
        priority = request.form.get("priority")
        start_date = request.form.get("start_date")
        due_date = request.form.get("due_date")
        notes = request.form.get("notes")

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO tasks (pos_id, reconciliation_date, certified, description, status, priority, start_date, due_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pos_id, reconciliation_date, certified, description, status, priority, start_date, due_date, notes))
        conn.commit()
        conn.close()
        return redirect("/tasks")
    else:
        return render_template("create.html", pos_data=pos_data)

# Route to get a task by task_id
@app.route("/get_task/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    """Fetch a specific task by task_id"""
    conn = get_db_connection()
    task = conn.execute("""
        SELECT tasks.*, pos.pos_name 
        FROM tasks 
        JOIN pos ON tasks.pos_id = pos.pos_id 
        WHERE tasks.task_id = ?
    """, (task_id,)).fetchone()
    conn.close()

    if task:
        return jsonify(task=dict(task))
    else:
        return jsonify(task=None)

# Modify task route
@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    """Modify an existing task"""
    conn = get_db_connection()
    
    # Handle GET request to render the modify page
    if request.method == "GET":
        pos_data = conn.execute("SELECT * FROM pos").fetchall()
        tasks = conn.execute("""
            SELECT tasks.*, pos.pos_name 
            FROM tasks 
            JOIN pos ON tasks.pos_id = pos.pos_id
        """).fetchall()
        conn.close()
        return render_template("modify.html", pos_data=pos_data, tasks=tasks)

    # Handle POST request to modify the task
    elif request.method == "POST":
        task_id = request.form.get("task_id")

        # Build the update query dynamically based on the fields provided
        update_fields = []
        update_values = []

        if request.form.get("pos_id"):
            update_fields.append("pos_id = ?")
            update_values.append(request.form.get("pos_id"))

        if request.form.get("reconciliation_date"):
            update_fields.append("reconciliation_date = ?")
            update_values.append(request.form.get("reconciliation_date"))

        if request.form.get("certified"):
            update_fields.append("certified = ?")
            update_values.append(request.form.get("certified").lower() == 'true')

        if request.form.get("description"):
            update_fields.append("description = ?")
            update_values.append(request.form.get("description"))

        if request.form.get("status"):
            update_fields.append("status = ?")
            update_values.append(request.form.get("status"))

        if request.form.get("priority"):
            update_fields.append("priority = ?")
            update_values.append(request.form.get("priority"))

        if request.form.get("start_date"):
            update_fields.append("start_date = ?")
            update_values.append(request.form.get("start_date"))

        if request.form.get("due_date"):
            update_fields.append("due_date = ?")
            update_values.append(request.form.get("due_date"))

        if request.form.get("notes"):
            update_fields.append("notes = ?")
            update_values.append(request.form.get("notes"))

        # If any fields are provided, proceed with the update
        if update_fields:
            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE task_id = ?"
            update_values.append(task_id)

            conn.execute(update_query, update_values)
            conn.commit()

        conn.close()

        # Return a JSON response to indicate success
        return jsonify({"success": True})


# Apology route for displaying error messages
def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
