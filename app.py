"""
This Flask application provides a task management system with various filters
and views for tasks. Users can register, log in, filter tasks by various criteria 
(including POS ID, POS name, reconciliation date range, task status, and priority), 
and view tasks in a table or Kanban board format. The application utilizes SQLAlchemy 
for database interactions and handles user sessions securely with Flask-Session.

Main features:
- User registration and login/logout functionality.
- Task filtering by search query, POS ID, POS name, reconciliation date, status, and priority.
- Task management with a Kanban board view.
- Data fetching and filtering via AJAX with a RESTful approach.
"""

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, select, and_, or_
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions
from helpers import apology, login_required
from datetime import date
import logging

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

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')

@app.route("/")
@login_required
def index():
    """
    Redirect to the tasks page as the homepage.

    Returns:
        redirect: A redirection to the tasks page.
    """
    return redirect("/tasks")

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user by collecting username and password inputs.
    Handles form validation, password hashing, and user registration in the database.

    Returns:
        redirect: On successful registration, redirects to the login page.
        render_template: Renders the registration form on GET request or on validation error.
        apology: Displays an error message if validation fails or username already exists.
    """
    if request.method == "POST":
        # Validate form inputs
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Hash the user's password
        hash_pw = generate_password_hash(request.form.get("password"))

        # Insert new user into the database
        try:
            with engine.connect() as conn:
                conn.execute(users_table.insert().values(username=request.form.get("username"), password_hash=hash_pw))
                conn.commit()
            flash("Registration successful! Please log in.")
        except Exception as e:
            logging.error(f"Error during registration: {e}")  # Logging error
            return apology("username already exists", 400)

        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log the user in by checking username and password.
    Clears any existing user session and sets a new session on successful login.

    Returns:
        redirect: Redirects to tasks page on successful login.
        render_template: Renders the login form on GET request or on login error.
        flash: Displays a flash message on error.
    """
    # Clear any existing user session
    session.clear()

    if request.method == "POST":
        # Ensure username and password are provided
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")
        if not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query database for username
        with engine.connect() as conn:
            query = select(users_table.c.user_id, users_table.c.username, users_table.c.password_hash).where(users_table.c.username == request.form.get("username"))
            rows = conn.execute(query).fetchall()

        # Validate username and password
        if len(rows) != 1:
            flash("Username does not exist. Please register.")
            return redirect("/register")
        elif not check_password_hash(rows[0][2], request.form.get("password")):
            flash("Incorrect password. Please try again.")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        flash("Logged in successfully!")
        return redirect("/tasks")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Log the user out by clearing the session data.
    
    Returns:
        redirect: Redirects to the login page after logout.
    """
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")

@app.route("/tasks")
@login_required
def tasks():
    """
    Display all tasks to the logged-in user, along with filtering options.

    Returns:
        render_template: Renders the tasks page with all tasks and POS data.
    """
    with engine.connect() as conn:
        # Query to select all tasks with related data from joined tables
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
            rec_table.c.rec_certified
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
        )
        
        # Execute query and fetch all tasks
        tasks = conn.execute(query).fetchall()

        # Fetch POS data for dropdown filters
        pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

    logging.debug("Fetched tasks for display: %s", tasks)  # Logging fetched tasks
    return render_template("tasks.html", tasks=tasks, pos_data=pos_data, date=date)

@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """
    Filter tasks based on user-selected criteria from the client-side and return as JSON data.

    Returns:
        jsonify: A JSON object containing the filtered list of tasks.
    """
    data = request.get_json()
    logging.debug("Received data from client: %s", data)  # Logging received data

    # Extract filter criteria from received data
    search_query = data.get("search_query", "").strip()
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    statuses = data.get("statuses", [])
    priorities = data.get("priorities", [])

    logging.debug("Parsed filter criteria - Search Query: %s, POS ID: %s, POS Name: %s, Start Date: %s, End Date: %s, Statuses: %s, Priorities: %s",
                  search_query, pos_id, pos_name, start_date, end_date, statuses, priorities)

    with engine.connect() as conn:
        # Base query to select tasks and join with related tables
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
            rec_table.c.rec_certified
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
        )

        # List to hold query conditions based on user filters
        conditions = []

        # Apply filters to the query
        if statuses:
            logging.debug("Applying status filter: %s", statuses)
            conditions.append(tasks_table.c.task_status.in_(statuses))
        
        if priorities:
            logging.debug("Applying priority filter: %s", priorities)
            conditions.append(tasks_table.c.task_priority.in_(priorities))
        
        if search_query:
            logging.debug("Applying search query filter: %s", search_query)
            search_condition = or_(
                tasks_table.c.task_desc.ilike(f"%{search_query}%"),
                tasks_table.c.task_notes.ilike(f"%{search_query}%"),
                pos_table.c.pos_name.ilike(f"%{search_query}%")
            )
            conditions.append(search_condition)

        if pos_id:
            logging.debug("Applying POS ID filter: %s", pos_id)
            conditions.append(pos_table.c.pos_id == pos_id)

        if pos_name:
            logging.debug("Applying POS Name filter: %s", pos_name)
            conditions.append(pos_table.c.pos_name.ilike(f"%{pos_name}%"))

        if start_date:
            logging.debug("Applying start date filter: %s", start_date)
            conditions.append(rec_table.c.rec_date >= start_date)
        if end_date:
            logging.debug("Applying end date filter: %s", end_date)
            conditions.append(rec_table.c.rec_date <= end_date)

        # Combine all conditions with 'AND' if there are any
        if conditions:
            query = query.where(and_(*conditions))

        logging.debug("Executing query with conditions: %s", str(query))  # Logging SQL query

        # Execute query and fetch filtered tasks
        tasks = conn.execute(query).fetchall()
        logging.debug("Fetched tasks: %s", tasks)  # Logging fetched tasks

    # Format tasks for JSON response
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            "task_id": task[0],
            "task_desc": task[1],
            "task_status": task[2],
            "task_priority": task[3],
            "task_start_date": task[4].strftime('%Y-%m-%d') if task[4] else None,
            "task_due_date": task[5].strftime('%Y-%m-%d') if task[5] else None,
            "task_notes": task[6] if task[6] else "",
            "pos_id": task[7],
            "pos_name": task[8],
            "rec_date": task[9].strftime('%Y-%m-%d') if task[9] else None,
            "rec_certified": task[10]
        })

    logging.debug("Returning tasks list to client: %s", tasks_list)  # Logging final tasks list
    return jsonify(tasks=tasks_list)

@app.route("/kanban")
@login_required
def kanban():
    """
    Render the Kanban board view with tasks categorized by status.

    Returns:
        render_template: Renders the Kanban view template with tasks data.
    """
    with engine.connect() as conn:
        # Query to select tasks and join with related tables
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
            .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .outerjoin(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id)
        )
        tasks = conn.execute(query).fetchall()
        logging.debug("Fetched tasks for Kanban view: %s", tasks)  # Logging tasks data

    return render_template("kanban.html", tasks=tasks)

@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    """
    Modify tasks based on user input. Provides form to modify task details or handles update requests.

    Returns:
        render_template: Renders the modify tasks page with current task data on GET request.
        jsonify: Returns a success JSON response after modifying a task on POST request.
    """
    with engine.connect() as conn:
        if request.method == "GET":
            # Fetch tasks and related data for modification
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
                .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
                .outerjoin(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id)
            )
            tasks = conn.execute(query).fetchall()
            pos_data = conn.execute(select([pos_table])).fetchall()
            logging.debug("Fetched tasks and POS data for modification: %s, %s", tasks, pos_data)  # Logging fetched data
            return render_template("modify.html", tasks=tasks, pos_data=pos_data)

        elif request.method == "POST":
            # Update tasks based on user inputs
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

            if update_fields:
                query = tasks_table.update().where(tasks_table.c.task_id == task_id).values(update_fields)
                logging.debug("Executing task update query: %s", query)  # Logging update query
                conn.execute(query)

            flash("Task updated successfully!")
            return redirect("/tasks")

def errorhandler(e):
    """
    Handle errors by returning a custom error message.

    Args:
        e: The error object.

    Returns:
        apology: A custom error page with the error name and code.
    """
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
