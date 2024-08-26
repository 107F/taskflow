from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, select, func, and_, or_
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

# Configure logging to overwrite the log file at each run
logging.basicConfig(
    filename='app.log',  # Log file name
    level=logging.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s %(levelname)s:%(message)s',  # Log message format
    filemode='w'  # 'w' mode overwrites the log file at each run
)

# Create a logger object
logger = logging.getLogger(__name__)

@app.route("/")
@login_required
def index():
    """Redirect to the tasks page as the homepage."""
    return redirect("/tasks")

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user by collecting username and password inputs.
    Handles form validation, password hashing, and user registration in the database.
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
            logger.error(f"Error during registration: {e}")  # Logging error
            return apology("username already exists", 400)

        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log the user in by checking username and password.
    Clears any existing user session and sets a new session on successful login.
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
    """
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")

@app.route("/tasks")
@login_required
def tasks():
    """
    Display all tasks to the logged-in user, along with filtering options.
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
            rec_table.c.rec_certified,
            blockers_table.c.blocker_desc,
            blockers_table.c.blocker_responsible
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .outerjoin(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id)
        )

        # Execute query and fetch all tasks
        tasks = conn.execute(query).fetchall()

        # Fetch POS data for dropdown filters
        pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

        # Format tasks for rendering in the template
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                "task_id": task.task_id if task.task_id is not None else "n/a",
                "task_desc": task.task_desc if task.task_desc is not None else "n/a",
                "task_status": task.task_status if task.task_status is not None else "n/a",
                "task_priority": task.task_priority if task.task_priority is not None else "n/a",
                "task_start_date": task.task_start_date.strftime('%Y-%m-%d') if task.task_start_date else "n/a",
                "task_due_date": task.task_due_date.strftime('%Y-%m-%d') if task.task_due_date else "n/a",
                "task_notes": task.task_notes if task.task_notes is not None else "n/a",
                "pos_id": task.pos_id if task.pos_id is not None else "n/a",
                "pos_name": task.pos_name if task.pos_name is not None else "n/a",
                "rec_date": task.rec_date.strftime('%Y-%m-%d') if task.rec_date else "n/a",
                "rec_certified": "Yes" if task.rec_certified is True else "No" if task.rec_certified is False else "n/a",
                "blocker_desc": task.blocker_desc if task.blocker_desc is not None else "n/a",
                "blocker_responsible": task.blocker_responsible if task.blocker_responsible is not None else "n/a"
            })

    logger.debug("Formatted tasks for display: %s", formatted_tasks)
    return render_template("tasks.html", tasks=formatted_tasks, pos_data=pos_data, date=date)


@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """Filter tasks based on user input and return JSON data."""
    data = request.get_json()
    app.logger.debug(f"Received data from client: {data}")  # Improved logging for received data

    # Extract filter criteria from received data
    search_query = data.get("search_query", "").strip()
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    statuses = data.get("statuses", [])
    priorities = data.get("priorities", [])

    app.logger.debug(f"Parsed filter criteria - Search Query: {search_query}, POS ID: {pos_id}, POS Name: {pos_name}, "
                     f"Start Date: {start_date}, End Date: {end_date}, Statuses: {statuses}, Priorities: {priorities}")

    with engine.connect() as conn:
        # Base query to select tasks and join with related tables
        query = select(
            tasks_table.c.task_id,
            tasks_table.c.task_desc,
            tasks_table.c.task_status,
            tasks_table.c.task_priority,
            tasks_table.c.task_start_date,
            tasks_table.c.task_due_date,
            func.coalesce(tasks_table.c.task_notes, 'n/a').label('task_notes'),
            pos_table.c.pos_id,
            func.coalesce(pos_table.c.pos_name, 'n/a').label('pos_name'),
            func.coalesce(rec_table.c.rec_date, 'n/a').label('rec_date'),
            rec_table.c.rec_certified,
            func.coalesce(blockers_table.c.blocker_desc, 'n/a').label('blocker_desc'),
            func.coalesce(blockers_table.c.blocker_responsible, 'n/a').label('blocker_responsible')
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .outerjoin(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id)
        )

        # List to hold query conditions
        conditions = []

        # Apply filters if provided
        if search_query:
            search_condition = or_(
                tasks_table.c.task_desc.ilike(f"%{search_query}%"),
                tasks_table.c.task_notes.ilike(f"%{search_query}%"),
                pos_table.c.pos_name.ilike(f"%{search_query}%")
            )
            conditions.append(search_condition)
            app.logger.debug(f"Applying search query filter: {search_query}")

        if pos_id:
            conditions.append(pos_table.c.pos_id == pos_id)
            app.logger.debug(f"Applying POS ID filter: {pos_id}")

        if pos_name:
            conditions.append(pos_table.c.pos_name.ilike(f"%{pos_name}%"))
            app.logger.debug(f"Applying POS Name filter: {pos_name}")

        if statuses:
            conditions.append(tasks_table.c.task_status.in_(statuses))
            app.logger.debug(f"Applying status filter: {statuses}")

        if priorities:
            conditions.append(tasks_table.c.task_priority.in_(priorities))
            app.logger.debug(f"Applying priority filter: {priorities}")

        if start_date:
            conditions.append(rec_table.c.rec_date >= start_date)
            app.logger.debug(f"Applying start date filter: {start_date}")

        if end_date:
            conditions.append(rec_table.c.rec_date <= end_date)
            app.logger.debug(f"Applying end date filter: {end_date}")

        # Apply conditions to the query
        if conditions:
            query = query.where(and_(*conditions))

        app.logger.debug(f"Executing query with conditions: {str(query)}")  # Log the complete SQL query

        # Execute query and fetch tasks
        tasks = conn.execute(query).fetchall()
        app.logger.debug(f"Fetched tasks: {tasks}")  # Log fetched tasks

    # Format tasks for JSON response
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            "task_id": task[0] if task[0] is not None else "n/a",
            "task_desc": task[1] if task[1] else "n/a",
            "task_status": task[2] if task[2] else "n/a",
            "task_priority": task[3] if task[3] else "n/a",
            "task_start_date": task[4].strftime('%Y-%m-%d') if task[4] else "n/a",
            "task_due_date": task[5].strftime('%Y-%m-%d') if task[5] else "n/a",
            "task_notes": task[6] if task[6] else "n/a",
            "pos_id": task[7] if task[7] else "n/a",
            "pos_name": task[8] if task[8] else "n/a",
            "rec_date": task[9].strftime('%Y-%m-%d') if task[9] != 'n/a' else "n/a",
            "rec_certified": "Yes" if task[10] else "No" if task[10] is not None else "n/a",
            "blocker_desc": task[11] if task[11] is not None else "n/a",
            "blocker_responsible": task[12] if task[12] is not None else "n/a"
        })

    app.logger.debug(f"Returning tasks list to client: {tasks_list}")  # Log the final tasks list sent to the client
    return jsonify(tasks=tasks_list)

def errorhandler(e):
    """
    Handle errors by returning a custom error message.
    """
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
