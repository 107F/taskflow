from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, select, func, and_, or_, desc
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions
from helpers import apology, login_required
from datetime import date, datetime
import logging
import traceback

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
engine = create_engine(DATABASE_URL, echo=False)  # Disable SQLAlchemy echo to avoid printing SQL to console
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
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s',
    filemode='w'
)

# Create a logger object
logger = logging.getLogger(__name__)

# Disable default Flask logging to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Configure session maker
SessionLocal = sessionmaker(bind=engine)

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
    """Display all tasks."""
    with engine.connect() as conn:
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
        ).order_by(desc(tasks_table.c.task_id))

        tasks = conn.execute(query).fetchall()
        pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                "task_id": task.task_id if task.task_id is not None else "n/a",
                "task_desc": task.task_desc if task.task_desc is not None else "n/a",
                "task_status": task.task_status if task.task_status is not None else "n/a",
                "task_priority": task.task_priority if task.task_priority is not None else "n/a",
                "task_start_date": task.task_start_date.strftime('%Y-%m-%d') if isinstance(task.task_start_date, date) else "n/a",
                "task_due_date": task.task_due_date.strftime('%Y-%m-%d') if isinstance(task.task_due_date, date) else "n/a",
                "task_notes": task.task_notes if task.task_notes is not None else "n/a",
                "pos_id": task.pos_id if task.pos_id is not None else "n/a",
                "pos_name": task.pos_name if task.pos_name is not None else "n/a",
                "rec_date": task.rec_date.strftime('%Y-%m-%d') if isinstance(task.rec_date, date) else "n/a",
                "rec_certified": "Yes" if task.rec_certified is True else "No" if task.rec_certified is False else "n/a",
                "blocker_desc": task.blocker_desc if task.blocker_desc is not None else "n/a",
                "blocker_responsible": task.blocker_responsible if task.blocker_responsible is not None else "n/a"
            })

    logger.debug("Formatted tasks for display: %s", formatted_tasks)
    return render_template("tasks.html", tasks=formatted_tasks, pos_data=pos_data, date=date)

@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """Filter tasks based on given criteria."""
    data = request.get_json()

    # Ensure data is not None before accessing keys
    if data is None:
        logger.error("No data received in request")
        return jsonify({"error": "No data received"}), 400

    search_query = data.get("search_query", "").strip() if data.get("search_query") else ""
    pos_id = data.get("pos_id") if data.get("pos_id") else None
    pos_name = data.get("pos_name", "").strip() if data.get("pos_name") else ""
    start_date = data.get("start_date") if data.get("start_date") else None
    end_date = data.get("end_date") if data.get("end_date") else None
    statuses = data.get("statuses", []) if data.get("statuses") else []
    priorities = data.get("priorities", []) if data.get("priorities") else []

    logger.debug(f"Received data from client: {data}")
    logger.debug(f"Parsed filter criteria - Search Query: {search_query}, POS ID: {pos_id}, POS Name: {pos_name}, Start Date: {start_date}, End Date: {end_date}, Statuses: {statuses}, Priorities: {priorities}")

    with engine.connect() as conn:
        query = select(
            tasks_table.c.task_id,
            tasks_table.c.task_desc,
            tasks_table.c.task_status,
            tasks_table.c.task_priority,
            tasks_table.c.task_start_date,
            tasks_table.c.task_due_date,
            coalesce(tasks_table.c.task_notes, 'n/a').label('task_notes'),
            pos_table.c.pos_id,
            coalesce(pos_table.c.pos_name, 'n/a').label('pos_name'),
            rec_table.c.rec_date,
            rec_table.c.rec_certified,
            coalesce(blockers_table.c.blocker_desc, 'n/a').label('blocker_desc'),
            coalesce(blockers_table.c.blocker_responsible, 'n/a').label('blocker_responsible')
        ).select_from(
            tasks_table.join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .outerjoin(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .outerjoin(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id)
        )

        conditions = []

        # Apply search query filter
        if search_query:
            conditions.append(or_(
                func.lower(tasks_table.c.task_desc).like(f"%{search_query.lower()}%"),
                func.lower(tasks_table.c.task_notes).like(f"%{search_query.lower()}%"),
                func.lower(pos_table.c.pos_name).like(f"%{search_query.lower()}%")
            ))

        # Apply pos_id filter
        if pos_id:
            conditions.append(pos_table.c.pos_id == pos_id)

        # Apply pos_name filter
        if pos_name:
            conditions.append(pos_table.c.pos_name.ilike(f"%{pos_name}%"))

        # Apply status filter
        if statuses:
            conditions.append(tasks_table.c.task_status.in_(statuses))

        # Apply priority filter
        if priorities:
            conditions.append(tasks_table.c.task_priority.in_(priorities))

        # Apply start_date filter
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                conditions.append(tasks_table.c.task_start_date >= start_date)
            except ValueError:
                logger.error(f"Invalid start date format: {start_date}")
                start_date = None  # Reset to None if parsing fails

        # Apply end_date filter
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                conditions.append(tasks_table.c.task_due_date <= end_date)
            except ValueError:
                logger.error(f"Invalid end date format: {end_date}")
                end_date = None  # Reset to None if parsing fails

        # Combine conditions if any
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(tasks_table.c.task_id))

        logger.debug(f"Executing query with conditions: {str(query)}")

        tasks = conn.execute(query).fetchall()
        logger.debug(f"Fetched tasks: {tasks}")

    # Format the tasks to send back to the client
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            "task_id": task[0] if task[0] is not None else "n/a",
            "task_desc": task[1] if task[1] else "n/a",
            "task_status": task[2] if task[2] else "n/a",
            "task_priority": task[3] if task[3] else "n/a",
            "task_start_date": task[4].strftime('%Y-%m-%d') if isinstance(task[4], date) else "n/a",
            "task_due_date": task[5].strftime('%Y-%m-%d') if isinstance(task[5], date) else "n/a",
            "task_notes": task[6] if task[6] else "n/a",
            "pos_id": task[7] if task[7] else "n/a",
            "pos_name": task[8] if task[8] else "n/a",
            "rec_date": task[9].strftime('%Y-%m-%d') if isinstance(task[9], date) else "n/a",
            "rec_certified": "Yes" if task[10] else "No" if task[10] is not None else "n/a",
            "blocker_desc": task[11] if task[11] is not None else "n/a",
            "blocker_responsible": task[12] if task[12] is not None else "n/a"
        })

    logger.debug(f"Returning tasks list to client: {tasks_list}")
    return jsonify(tasks=tasks_list)

@app.route("/create", methods=["GET", "POST"])
@login_required
def create_task():
    """
    Handle the creation of a new task or display the create task page with existing tasks.
    """
    if request.method == "POST":
        # Get form data
        pos_id = request.form.get("pos_id")

        # Optional fields
        reconciliation_date = request.form.get("reconciliation_date") or None
        certified = request.form.get("certified") or None
        description = request.form.get("description") or None
        status = request.form.get("status") or None
        priority = request.form.get("priority") or None
        start_date = request.form.get("start_date") or None
        due_date = request.form.get("due_date") or None
        notes = request.form.get("notes") or None
        blocker_desc = request.form.get("blocker_desc") or None
        blocker_responsible = request.form.get("blocker_responsible") or None

        # Convert date strings to Python date objects if present
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            if reconciliation_date:
                reconciliation_date = datetime.strptime(reconciliation_date, '%Y-%m-%d').date()
        except ValueError as e:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect("/create")

        # Validate required fields
        if not pos_id:
            flash("POS ID is required.")
            return redirect("/create")

        try:
            with engine.connect() as conn:
                # Insert the new task into the tasks table
                task_insert = tasks_table.insert().values(
                    pos_id=pos_id,
                    task_desc=description,
                    task_status=status,
                    task_priority=priority,
                    task_start_date=start_date,
                    task_due_date=due_date,
                    task_notes=notes
                )
                result = conn.execute(task_insert)
                task_id = result.inserted_primary_key[0]  # Get the inserted task ID

                # Insert the related blocker information if provided
                blocker_id = None
                if blocker_desc or blocker_responsible:
                    blocker_insert = blockers_table.insert().values(
                        blocker_desc=blocker_desc,
                        blocker_responsible=blocker_responsible,
                        task_id=task_id,  # Link with the new task
                        pos_id=pos_id
                    )
                    blocker_result = conn.execute(blocker_insert)
                    blocker_id = blocker_result.inserted_primary_key[0]  # Get the inserted blocker ID

                # Insert reconciliation information into rec_table if needed
                rec_id = None
                if reconciliation_date or certified is not None:
                    rec_insert = rec_table.insert().values(
                        rec_date=reconciliation_date,
                        rec_certified=(certified == 'true') if certified else None,
                        task_id=task_id,  # Link with the new task
                        pos_id=pos_id,
                        blocker_id=blocker_id  # Link with the new blocker if created
                    )
                    rec_result = conn.execute(rec_insert)
                    rec_id = rec_result.inserted_primary_key[0]  # Get the inserted rec ID

                # Update the task record with blocker_id and rec_id if they were created
                conn.execute(
                    tasks_table.update()
                    .where(tasks_table.c.task_id == task_id)
                    .values(blocker_id=blocker_id, rec_id=rec_id)
                )

                conn.commit()
            flash("Task created successfully!")
        except Exception as e:
            logger.error(f"Error creating task: {traceback.format_exc()}")
            flash("An error occurred while creating the task.")
            return redirect("/create")

        return redirect("/tasks")
    else:
        # Fetch POS data for the form dropdown
        with engine.connect() as conn:
            pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

            # Fetch tasks similarly to the `/tasks` route to display them on the create page
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
            ).order_by(desc(tasks_table.c.task_id))

            tasks = conn.execute(query).fetchall()

            # Format tasks for rendering in template
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "task_id": task.task_id if task.task_id is not None else "n/a",
                    "task_desc": task.task_desc if task.task_desc is not None else "n/a",
                    "task_status": task.task_status if task.task_status is not None else "n/a",
                    "task_priority": task.task_priority if task.task_priority is not None else "n/a",
                    "task_start_date": task.task_start_date.strftime('%Y-%m-%d') if isinstance(task.task_start_date, date) else "n/a",
                    "task_due_date": task.task_due_date.strftime('%Y-%m-%d') if isinstance(task.task_due_date, date) else "n/a",
                    "task_notes": task.task_notes if task.task_notes is not None else "n/a",
                    "pos_id": task.pos_id if task.pos_id is not None else "n/a",
                    "pos_name": task.pos_name if task.pos_name is not None else "n/a",
                    "rec_date": task.rec_date.strftime('%Y-%m-%d') if isinstance(task.rec_date, date) else "n/a",
                    "rec_certified": "Yes" if task.rec_certified is True else "No" if task.rec_certified is False else "n/a",
                    "blocker_desc": task.blocker_desc if task.blocker_desc is not None else "n/a",
                    "blocker_responsible": task.blocker_responsible if task.blocker_responsible is not None else "n/a"
                })

        # Render the create.html with tasks and POS data
        return render_template("create.html", pos_data=pos_data, tasks=formatted_tasks, date=date)

@app.route("/api/get_task/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    """
    Fetch the task details for a given task_id and return them as JSON.
    """
    try:
        with engine.connect() as conn:
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
            ).where(tasks_table.c.task_id == task_id)

            task = conn.execute(query).fetchone()

            if task:
                # Format the task details for JSON response
                task_data = {
                    "task_id": task.task_id,
                    "task_desc": task.task_desc or "n/a",
                    "task_status": task.task_status or "n/a",
                    "task_priority": task.task_priority or "n/a",
                    "task_start_date": task.task_start_date.strftime('%Y-%m-%d') if task.task_start_date else "n/a",
                    "task_due_date": task.task_due_date.strftime('%Y-%m-%d') if task.task_due_date else "n/a",
                    "task_notes": task.task_notes or "n/a",
                    "pos_id": task.pos_id,
                    "pos_name": task.pos_name,
                    "rec_date": task.rec_date.strftime('%Y-%m-%d') if task.rec_date else "n/a",
                    "rec_certified": "Yes" if task.rec_certified else "No" if task.rec_certified is not None else "n/a",
                    "blocker_desc": task.blocker_desc or "n/a",
                    "blocker_responsible": task.blocker_responsible or "n/a"
                }
                return jsonify({"success": True, "task": task_data})
            else:
                return jsonify({"success": False, "message": "Task not found."})

    except Exception as e:
        logger.error(f"Error fetching task: {traceback.format_exc()}")
        return jsonify({"success": False, "message": "An error occurred while fetching the task."}), 500


@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify_task():
    """
    Handle the modification of an existing task or display the modify task page with existing tasks.
    """
    if request.method == "POST":
        # Get form data
        task_id = request.form.get("task_id")
        pos_id = request.form.get("pos_id")

        # Optional fields
        reconciliation_date = request.form.get("reconciliation_date") or None
        certified = request.form.get("certified") or None
        description = request.form.get("description") or None
        status = request.form.get("status") or None
        priority = request.form.get("priority") or None
        start_date = request.form.get("start_date") or None
        due_date = request.form.get("due_date") or None
        notes = request.form.get("notes") or None
        blocker_desc = request.form.get("blocker_desc") or None
        blocker_responsible = request.form.get("blocker_responsible") or None

        # Convert date strings to Python date objects if present
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            if reconciliation_date:
                reconciliation_date = datetime.strptime(reconciliation_date, '%Y-%m-%d').date()
        except ValueError as e:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect("/modify")

        # Validate required fields
        if not task_id or not pos_id:
            flash("Task ID and POS ID are required.")
            return redirect("/modify")

        try:
            with engine.connect() as conn:
                # Update the task in the tasks table
                task_update = tasks_table.update().where(tasks_table.c.task_id == task_id).values(
                    pos_id=pos_id,
                    task_desc=description,
                    task_status=status,
                    task_priority=priority,
                    task_start_date=start_date,
                    task_due_date=due_date,
                    task_notes=notes
                )
                conn.execute(task_update)

                # Update the related blocker information if provided
                if blocker_desc or blocker_responsible:
                    # Check if blocker already exists for this task
                    blocker_exists = conn.execute(
                        select(blockers_table.c.blocker_id).where(blockers_table.c.task_id == task_id)
                    ).fetchone()

                    if blocker_exists:
                        # Update existing blocker
                        conn.execute(
                            blockers_table.update().where(blockers_table.c.task_id == task_id).values(
                                blocker_desc=blocker_desc,
                                blocker_responsible=blocker_responsible
                            )
                        )
                    else:
                        # Insert new blocker if it doesn't exist
                        conn.execute(
                            blockers_table.insert().values(
                                blocker_desc=blocker_desc,
                                blocker_responsible=blocker_responsible,
                                task_id=task_id,
                                pos_id=pos_id
                            )
                        )

                # Update reconciliation information if needed
                if reconciliation_date or certified is not None:
                    # Check if reconciliation already exists for this task
                    rec_exists = conn.execute(
                        select(rec_table.c.rec_id).where(rec_table.c.task_id == task_id)
                    ).fetchone()

                    if rec_exists:
                        # Update existing reconciliation
                        conn.execute(
                            rec_table.update().where(rec_table.c.task_id == task_id).values(
                                rec_date=reconciliation_date,
                                rec_certified=(certified == 'true') if certified else None
                            )
                        )
                    else:
                        # Insert new reconciliation if it doesn't exist
                        conn.execute(
                            rec_table.insert().values(
                                rec_date=reconciliation_date,
                                rec_certified=(certified == 'true') if certified else None,
                                task_id=task_id,
                                pos_id=pos_id
                            )
                        )

                conn.commit()
            flash("Task modified successfully!")  # Only display success if everything works
            return redirect("/modify")

        except Exception as e:
            logger.error(f"Error modifying task: {traceback.format_exc()}")
            flash("An error occurred while modifying the task.")
            return redirect("/modify")

    else:
        # Fetch POS data for the form dropdown
        with engine.connect() as conn:
            pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

            # Fetch tasks similarly to the `/tasks` route to display them on the modify page
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
            ).order_by(desc(tasks_table.c.task_id))

            tasks = conn.execute(query).fetchall()

            # Format tasks for rendering in template
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "task_id": task.task_id if task.task_id is not None else "n/a",
                    "task_desc": task.task_desc if task.task_desc is not None else "n/a",
                    "task_status": task.task_status if task.task_status is not None else "n/a",
                    "task_priority": task.task_priority if task.task_priority is not None else "n/a",
                    "task_start_date": task.task_start_date.strftime('%Y-%m-%d') if isinstance(task.task_start_date, date) else "n/a",
                    "task_due_date": task.task_due_date.strftime('%Y-%m-%d') if isinstance(task.task_due_date, date) else "n/a",
                    "task_notes": task.task_notes if task.task_notes is not None else "n/a",
                    "pos_id": task.pos_id if task.pos_id is not None else "n/a",
                    "pos_name": task.pos_name if task.pos_name is not None else "n/a",
                    "rec_date": task.rec_date.strftime('%Y-%m-%d') if isinstance(task.rec_date, date) else "n/a",
                    "rec_certified": "Yes" if task.rec_certified is True else "No" if task.rec_certified is False else "n/a",
                    "blocker_desc": task.blocker_desc if task.blocker_desc is not None else "n/a",
                    "blocker_responsible": task.blocker_responsible if task.blocker_responsible is not None else "n/a"
                })

        # Render the modify.html with tasks and POS data
        return render_template("modify.html", pos_data=pos_data, tasks=formatted_tasks, date=date)



def errorhandler(e):
    """Handle errors by returning a custom error message."""
    logger.error(f"Error occurred: {e}")  # Log the error
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=False)  # Set debug to False to avoid detailed traceback in terminal
