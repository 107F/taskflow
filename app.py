"""
app.py

This is the main application file for the TaskFlow project, a task management tool designed for a grocery store's accounts payable department. 
This script uses Flask, SQLAlchemy, and other libraries to create routes for user registration, login, and logout, as well as task management.

Modules imported:
- Flask: A lightweight web framework for Python that handles HTTP requests and responses.
- flash, redirect, render_template, request, session, jsonify: Functions from Flask to manage sessions, render HTML templates, and handle HTTP requests.
- Flask_Session: A Flask extension that provides server-side session management.
- SQLAlchemy: A SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- create_engine, MetaData, Table, select, and_: Functions from SQLAlchemy for connecting to the database and managing SQL queries.
- check_password_hash, generate_password_hash: Functions from Werkzeug for securely handling user passwords.
- default_exceptions: A collection of default exceptions from Werkzeug to handle errors.
- helpers: A custom module containing utility functions like apology and login_required.
"""

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, select, and_
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

# Set up SQLAlchemy to connect to the SQLite database
DATABASE_URL = "sqlite:///taskflow.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables from the database into SQLAlchemy Table objects
tasks_table = Table('tasks', metadata, autoload_with=engine)
pos_table = Table('pos', metadata, autoload_with=engine)
rec_table = Table('rec', metadata, autoload_with=engine)
blockers_table = Table('blockers', metadata, autoload_with=engine)
users_table = Table('users', metadata, autoload_with=engine)

@app.route("/")
@login_required
def index():
    """
    Redirect to tasks page.
    
    This route handles the root URL and redirects logged-in users to the tasks page.
    If the user is not logged in, they will be redirected to the login page by the login_required decorator.
    """
    return redirect("/tasks")

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    
    This route handles user registration by creating a new entry in the 'users' table with a username and a hashed password.
    It also checks for common errors, such as missing username, missing password, and non-matching password confirmation.
    """
    if request.method == "POST":
        # Ensure the user has provided a username
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure the user has provided a password
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure the password matches the confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Hash the user's password
        hash_pw = generate_password_hash(request.form.get("password"))

        try:
            # Insert the new user into the database
            with engine.connect() as conn:
                conn.execute(
                    users_table.insert().values(username=request.form.get("username"), password_hash=hash_pw)
                )
                conn.commit()  # Ensure the transaction is committed

            # Set a flash message on successful registration
            flash("Registration successful! Please log in.")
        except Exception as e:
            # Handle the case where the username already exists
            return apology("username already exists", 400)

        # Redirect the user to the login page after successful registration
        return redirect("/login")

    else:
        # Render the registration form if the request method is GET
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log a user in or redirect to registration if the user does not exist.
    
    This route handles user login by verifying the username and password.
    If the credentials are correct, the user's session is initialized, allowing access to other routes.
    If the credentials are incorrect or the user does not exist, the user is redirected to the registration page.
    """
    # Clear any existing user session data
    session.clear()

    if request.method == "POST":
        # Ensure the user has provided a username
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")

        # Ensure the user has provided a password
        if not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query the database for the user with the provided username
        with engine.connect() as conn:
            query = select(
                users_table.c.user_id, 
                users_table.c.username, 
                users_table.c.password_hash
            ).where(users_table.c.username == request.form.get("username"))
            rows = conn.execute(query).fetchall()

        # Check if the username exists
        if len(rows) != 1:
            flash("Username does not exist. Please register.")
            return redirect("/register")
        
        # Check if the password is correct
        elif not check_password_hash(rows[0][2], request.form.get("password")):
            flash("Incorrect password. Please try again.")
            return redirect("/login")

        # Remember the logged-in user by storing their user ID in the session
        session["user_id"] = rows[0][0]

        # Debug: Verify session is set
        print(f"Logged in user_id: {session['user_id']}")

        # Redirect the user to the tasks page after successful login
        return redirect("/tasks")

    else:
        # Render the login form if the request method is GET
        return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Log a user out.
    
    This route handles logging a user out by clearing their session data, and then redirects them to the login page.
    """
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")

@app.route("/tasks")
@login_required
def tasks():
    """
    Show all tasks.
    
    This route retrieves and displays all tasks from the database, including related POS (Point of Sale) information, 
    task status, priority, and associated blockers.
    """
    with engine.connect() as conn:
        # Construct a query to select relevant task data from multiple tables
        query = select(
            tasks_table.c.task_id,
            tasks_table.c.task_desc,
            tasks_table.c.task_status,
            tasks_table.c.task_priority,
            tasks_table.c.task_start_date,
            tasks_table.c.task_due_date,
            tasks_table.c.task_notes,
            pos_table.c.pos_id,
            pos_table.c.pos_name,
            rec_table.c.rec_date,
            rec_table.c.rec_certified,
            blockers_table.c.blocker_desc,
            blockers_table.c.blocker_responsible,
            blockers_table.c.blocker_resolved,
            blockers_table.c.blocker_res_date
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .join(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id, isouter=True)
        )
        tasks = conn.execute(query).fetchall()

    # Render the tasks page with the retrieved task data
    return render_template("tasks.html", tasks=tasks)

@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """
    Filter tasks based on POS ID, POS Name, and search query.
    
    This route allows the user to filter tasks based on specific criteria such as POS ID, POS Name, 
    and a general search query. The filtered results are returned as JSON data.
    """
    data = request.get_json()
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name")
    search_query = data.get("search_query")

    with engine.connect() as conn:
        # Construct a query to filter tasks based on the provided criteria
        query = select(
            tasks_table.c.task_id,
            tasks_table.c.task_desc,
            tasks_table.c.task_status,
            tasks_table.c.task_priority,
            tasks_table.c.task_start_date,
            tasks_table.c.task_due_date,
            tasks_table.c.task_notes,
            pos_table.c.pos_id,
            pos_table.c.pos_name,
            rec_table.c.rec_date,
            rec_table.c.rec_certified,
            blockers_table.c.blocker_desc,
            blockers_table.c.blocker_responsible,
            blockers_table.c.blocker_resolved,
            blockers_table.c.blocker_res_date
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .join(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id, isouter=True)
        )

        # Add filtering conditions based on the provided criteria
        conditions = []
        if pos_id:
            conditions.append(tasks_table.c.pos_id == pos_id)
        if pos_name:
            conditions.append(pos_table.c.pos_name == pos_name)
        if search_query:
            conditions.append(
                and_(
                    tasks_table.c.task_desc.like(f'%{search_query}%'),
                    tasks_table.c.task_notes.like(f'%{search_query}%')
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        tasks = conn.execute(query).fetchall()

    # Convert the tasks to a list of dictionaries and return as JSON
    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks=tasks_list)

@app.route("/kanban")
@login_required
def kanban():
    """
    Show Kanban board.
    
    This route displays a Kanban board view of the tasks, allowing users to visualize task progress across different stages.
    """
    with engine.connect() as conn:
        # Construct a query to select relevant task data for the Kanban board
        query = select(
            tasks_table.c.task_id,
            tasks_table.c.task_desc,
            tasks_table.c.task_status,
            tasks_table.c.task_priority,
            tasks_table.c.task_start_date,
            tasks_table.c.task_due_date,
            tasks_table.c.task_notes,
            pos_table.c.pos_id,
            pos_table.c.pos_name,
            rec_table.c.rec_date,
            rec_table.c.rec_certified,
            blockers_table.c.blocker_desc,
            blockers_table.c.blocker_responsible,
            blockers_table.c.blocker_resolved,
            blockers_table.c.blocker_res_date
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .join(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id, isouter=True)
        )
        tasks = conn.execute(query).fetchall()

    # Render the Kanban board with the retrieved task data
    return render_template("kanban.html", tasks=tasks)

@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    """
    Modify an existing task.
    
    This route allows users to modify the details of an existing task, including status, priority, 
    associated POS, blockers, and other related information.
    """
    with engine.connect() as conn:
        if request.method == "GET":
            # Retrieve existing task and POS data to populate the modification form
            query = select(
                tasks_table.c.task_id,
                tasks_table.c.task_desc,
                tasks_table.c.task_status,
                tasks_table.c.task_priority,
                tasks_table.c.task_start_date,
                tasks_table.c.task_due_date,
                tasks_table.c.task_notes,
                pos_table.c.pos_id,
                pos_table.c.pos_name,
                rec_table.c.rec_date,
                rec_table.c.rec_certified,
                blockers_table.c.blocker_desc,
                blockers_table.c.blocker_responsible,
                blockers_table.c.blocker_resolved,
                blockers_table.c.blocker_res_date
            ).select_from(
                tasks_table
                .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
                .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
                .join(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id, isouter=True)
            )
            tasks = conn.execute(query).fetchall()
            pos_data = conn.execute(select([pos_table])).fetchall()
            return render_template("modify.html", tasks=tasks, pos_data=pos_data)

        elif request.method == "POST":
            # Update the task based on the form data provided by the user
            task_id = request.form.get("task_id")
            update_fields = {}
            if request.form.get("pos_id"):
                update_fields["pos_id"] = request.form.get("pos_id")
            if request.form.get("rec_date"):
                update_fields["rec_id"] = request.form.get("rec_id")
            if request.form.get("blocker_id"):
                update_fields["blocker_id"] = request.form.get("blocker_id")
            if request.form.get("task_desc"):
                update_fields["task_desc"] = request.form.get("task_desc")
            if request.form.get("task_status"):
                update_fields["task_status"] = request.form.get("task_status")
            if request.form.get("task_priority"):
                update_fields["task_priority"] = request.form.get("task_priority")
            if request.form.get("task_start_date"):
                update_fields["task_start_date"] = request.form.get("task_start_date")
            if request.form.get("task_due_date"):
                update_fields["task_due_date"] = request.form.get("task_due_date")
            if request.form.get("task_notes"):
                update_fields["task_notes"] = request.form.get("task_notes")

            # Execute the update query if there are any fields to update
            if update_fields:
                query = tasks_table.update().where(tasks_table.c.task_id == task_id).values(update_fields)
                conn.execute(query)

            return jsonify({"success": True})

def errorhandler(e):
    """
    Handle error.
    
    This function handles errors that occur during the execution of the application by displaying an apology page.
    """
    return apology(e.name, e.code)

# Register error handlers for all default exceptions
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
