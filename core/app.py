"""
File: app.py
Developer: Stefania Galatolo
Assisted by: ChatGPT 4.0

Description:
This is the main application file for the Task Management Tool, developed as the final project for CS50 by Harvard on EdX 2024. 
The app manages tasks in a grocery store's accounts payable system, leveraging Python, Flask, and SQLAlchemy to provide an intuitive 
user interface with features like task creation, modification, and a Kanban board for visual task management.

This file includes:
- App configuration and setup
- User authentication (registration, login, logout)
- Task management routes (create, modify, filter)
- Kanban board rendering and task updates
- Error handling and logging
- API endpoints for task and POS data retrieval

Correlations:
- Utilizes helper functions and constants from helpers.py for modularity and reusability.
- Interacts with the database via SQLAlchemy Core.
- Integrates with templates in the 'templates' directory for UI rendering.
- Implements RESTful API principles for client-server interactions.
"""

import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import select, and_, or_, desc, func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions
from core.helpers import (
    apology, 
    login_required, 
    get_paginated_tasks, 
    fetch_pos_data, 
    format_task, 
    engine, 
    tasks_table, 
    pos_table, 
    rec_table, 
    blockers_table, 
    users_table
)
from datetime import date, datetime
import logging
import traceback

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('6e2f996247e3efcee66f23ffd99b7322383a130a7cc345b03b848ddc54e52412')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create a logger object
logger = logging.getLogger(__name__)

# Disable default Flask logging to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Set a constant for the number of records per page
RECORDS_PER_PAGE = 15

@app.route("/")
@login_required
def index():
    """
    Redirect to the kanban page as the homepage.

    This route serves as the default landing page after login. 
    It redirects users to the Kanban board, which provides an overview of all tasks.

    Returns:
        - redirect to the '/kanban' route.
    """
    return redirect("/kanban")

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user by collecting username and password inputs.
    Handles form validation, password hashing, and user registration in the database.

    Methods:
        GET: Renders the registration form.
        POST: Processes the registration data, validates it, and inserts a new user into the database.

    Returns:
        - On GET: Render the registration page.
        - On POST success: Redirect to the login page.
        - On POST failure: Render an apology or show an error message.
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
            logger.error(f"Error during registration: {e}")
            return apology("username already exists", 400)

        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log the user in by checking username and password.
    Clears any existing user session and sets a new session on successful login.

    Methods:
        GET: Renders the login form.
        POST: Authenticates the user against the database and starts a new session.

    Returns:
        - On GET: Render the login page.
        - On POST success: Redirect to the kanban page.
        - On POST failure: Show an error message and prompt the user to try again.
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
        return redirect("/kanban")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Log the user out by clearing the session data.

    Returns:
        - Redirect to the login page after clearing the session.
    """
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")

@app.route("/tasks")
@login_required
def tasks():
    """
    Display all tasks with pagination.

    This route fetches tasks from the database and renders them on the 'tasks.html' page.
    Utilizes helper functions to format tasks and fetch POS data.

    Query Parameters:
        page (int): Page number for pagination. Defaults to 1.

    Returns:
        - Render the 'tasks.html' template with task data, POS data, and pagination info.
    """
    page = request.args.get('page', 1, type=int)

    base_query = select(
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

    try:
        # Fetch paginated tasks
        tasks, total_records, total_pages = get_paginated_tasks(base_query, page, RECORDS_PER_PAGE)

        if not tasks:
            logger.warning("No tasks returned from the database.")

        # Format tasks for rendering
        formatted_tasks = [format_task(task) for task in tasks]

        # Fetch POS data for the dropdowns
        pos_data = fetch_pos_data()

        logger.debug(f"Formatted tasks for rendering: {formatted_tasks}")
        return render_template("tasks.html", tasks=formatted_tasks, pos_data=pos_data, page=page, total_pages=total_pages, date=date)

    except Exception as e:
        logger.error(f"Error displaying tasks: {traceback.format_exc()}")
        flash("An error occurred while loading tasks.")
        return redirect("/")

@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """
    Filter tasks based on given criteria with pagination.

    This route processes filtering options submitted via a JSON request. It constructs a SQLAlchemy 
    query with dynamic filters and returns a paginated list of tasks matching the criteria.

    Request JSON:
        - search_query (str): Text to search in task descriptions, notes, or POS names.
        - pos_id (int): POS ID to filter by.
        - pos_name (str): POS Name to filter by.
        - start_date (str): Start date to filter tasks from.
        - end_date (str): End date to filter tasks until.
        - statuses (list): List of task statuses to filter by.
        - priorities (list): List of task priorities to filter by.
        - page (int): Page number for pagination.

    Returns:
        - JSON response with tasks, current page, and total pages.
    """
    data = request.get_json()
    page = data.get('page', 1)

    if data is None:
        logger.error("No data received in request")
        return jsonify({"error": "No data received"}), 400

    search_query = data.get("search_query", "").strip()
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name", "").strip()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    statuses = data.get("statuses", [])
    priorities = data.get("priorities", [])

    logger.debug(f"Received data from client: {data}")

    base_query = select(
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

    # Apply filters if provided
    if pos_id:
        conditions.append(pos_table.c.pos_id == pos_id)
    if pos_name:
        conditions.append(pos_table.c.pos_name.ilike(f"%{pos_name}%"))
    if statuses:
        conditions.append(tasks_table.c.task_status.in_(statuses))
    if priorities:
        conditions.append(tasks_table.c.task_priority.in_(priorities))
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            conditions.append(tasks_table.c.task_start_date >= start_date)
        except ValueError:
            logger.error(f"Invalid start date format: {start_date}")
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            conditions.append(tasks_table.c.task_due_date <= end_date)
        except ValueError:
            logger.error(f"Invalid end date format: {end_date}")

    # Combine conditions if any
    if conditions:
        base_query = base_query.where(and_(*conditions))

    base_query = base_query.order_by(desc(tasks_table.c.task_id))

    logger.debug(f"Executing query with conditions: {str(base_query)}")

    try:
        # Fetch paginated tasks
        tasks, total_records, total_pages = get_paginated_tasks(base_query, page, RECORDS_PER_PAGE)
        logger.debug(f"Fetched tasks: {tasks}")
    except Exception as e:
        logger.error(f"Error fetching filtered tasks: {traceback.format_exc()}")
        return jsonify({"error": "An error occurred while fetching tasks."}), 500

    # Format the tasks to send back to the client
    tasks_list = [format_task(task) for task in tasks]

    logger.debug(f"Returning tasks list to client: {tasks_list}")
    return jsonify(tasks=tasks_list, page=page, total_pages=total_pages)

@app.route("/create", methods=["GET", "POST"])
@login_required
def create_task():
    """
    Handle the creation of a new task or display the create task page with existing tasks.

    Methods:
        GET: Fetches existing tasks and POS data to display on the task creation page.
        POST: Validates and inserts a new task into the database. Optionally inserts related 
              blocker and reconciliation data.

    Returns:
        - On GET: Render the 'create.html' template with tasks and POS data.
        - On POST success: Redirect to the tasks page.
        - On POST failure: Show an error message and prompt the user to try again.
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
        pos_data = fetch_pos_data()

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

        tasks = engine.connect().execute(query).fetchall()

        # Format tasks for rendering in template
        formatted_tasks = [format_task(task) for task in tasks]

        # Render the create.html with tasks and POS data
        return render_template("create.html", pos_data=pos_data, tasks=formatted_tasks, date=date)

@app.route("/api/get_task/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    """
    Fetch the task details for a given task_id and return them as JSON.

    Args:
        task_id (int): The ID of the task to fetch.

    Returns:
        - JSON response with task details if found.
        - JSON error response if task not found or an error occurs.
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
                task_data = format_task(task)
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

    Methods:
        GET: Fetches existing tasks and POS data to display on the modification page.
        POST: Updates the task information in the database. Optionally updates related 
              blocker and reconciliation data.

    Returns:
        - On GET: Render the 'modify.html' template with tasks and POS data.
        - On POST success: Redirect to the modify page.
        - On POST failure: Show an error message and prompt the user to try again.
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
        pos_data = fetch_pos_data()

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

        tasks = engine.connect().execute(query).fetchall()

        # Format tasks for rendering in template
        formatted_tasks = [format_task(task) for task in tasks]

        # Render the modify.html with tasks and POS data
        return render_template("modify.html", pos_data=pos_data, tasks=formatted_tasks, date=date)

@app.route("/kanban")
@login_required
def kanban():
    """
    Render the Kanban board page with POS data for filters.

    The Kanban board provides a visual overview of tasks, categorized by status.
    Fetches POS data for filtering purposes.

    Returns:
        - Render the 'kanban.html' template with POS data.
    """
    try:
        with engine.connect() as conn:
            pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

        return render_template("kanban.html", pos_data=pos_data, date=datetime.today())
    except Exception as e:
        return jsonify({"error": "Error loading Kanban board"}), 500

@app.route("/api/kanban_tasks", methods=["POST"])
@login_required
def get_kanban_tasks():
    """
    Fetch all tasks for the Kanban board, with filters.

    This route processes filtering options submitted via a JSON request and returns a list 
    of tasks for rendering on the Kanban board.

    Request JSON:
        - search_query (str): Text to search in task descriptions.
        - pos_id (int): POS ID to filter by.
        - pos_name (str): POS Name to filter by.
        - start_date (str): Start date to filter tasks from.
        - end_date (str): End date to filter tasks until.
        - statuses (list): List of task statuses to filter by.
        - priorities (list): List of task priorities to filter by.

    Returns:
        - JSON response with filtered tasks.
    """
    try:
        data = request.get_json()
        search_query = data.get("search_query", "").strip()
        pos_id = data.get("pos_id")
        pos_name = data.get("pos_name", "").strip()
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        statuses = data.get("statuses", [])
        priorities = data.get("priorities", [])

        with engine.connect() as conn:
            query = select(
                tasks_table.c.task_id,
                tasks_table.c.task_desc,
                tasks_table.c.task_status,
                tasks_table.c.task_priority,
                tasks_table.c.task_due_date,
                pos_table.c.pos_id,
                pos_table.c.pos_name
            ).select_from(
                tasks_table.join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            )

            conditions = []
            if search_query:
                conditions.append(tasks_table.c.task_desc.ilike(f"%{search_query}%"))
            if pos_id:
                conditions.append(pos_table.c.pos_id == pos_id)
            if pos_name:
                conditions.append(pos_table.c.pos_name.ilike(f"%{pos_name}%"))
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                conditions.append(tasks_table.c.task_due_date >= start_date)
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                conditions.append(tasks_table.c.task_due_date <= end_date)
            if statuses:
                conditions.append(tasks_table.c.task_status.in_(statuses))
            if priorities:
                conditions.append(tasks_table.c.task_priority.in_(priorities))

            if conditions:
                query = query.where(and_(*conditions))

            tasks = conn.execute(query).fetchall()

        tasks_list = [
            {
                "task_id": task.task_id,
                "task_desc": task.task_desc,
                "task_status": task.task_status,
                "task_priority": task.task_priority,
                "task_due_date": task.task_due_date.strftime('%Y-%m-%d') if task.task_due_date else "n/a",
                "pos_id": task.pos_id,
                "pos_name": task.pos_name
            } for task in tasks
        ]
        return jsonify({"tasks": tasks_list})

    except Exception as e:
        return jsonify({"error": "Failed to fetch tasks."}), 500

@app.route("/api/update_task_status/<int:task_id>", methods=["POST"])
@login_required
def update_task_status(task_id):
    """
    Update the task's status when dragged and dropped on the Kanban board.

    Args:
        task_id (int): The ID of the task to update.

    Request JSON:
        - status (str): The new status of the task.

    Returns:
        - JSON response indicating success or failure.
    """
    logger.debug(f"Received request to update task with ID: {task_id}")

    # Retrieve the new status from the request
    new_status = request.json.get('status')
    logger.debug(f"New status from request for task {task_id}: {new_status}")

    # Check if new_status is valid
    if not new_status:
        logger.error(f"No status provided for task {task_id}")
        return jsonify(success=False, message="No status provided"), 400

    try:
        with engine.connect() as conn:
            logger.debug(f"Executing update query for task {task_id} to set status to {new_status}")

            # Execute the update query
            result = conn.execute(
                tasks_table.update()
                .where(tasks_table.c.task_id == task_id)
                .values(task_status=new_status)
            )

            # Check how many rows were affected
            rows_affected = result.rowcount
            logger.debug(f"Rows affected by the update for task {task_id}: {rows_affected}")

            if rows_affected == 0:
                logger.error(f"Task {task_id} not found in the database. No rows affected.")
                return jsonify(success=False, message="Task not found"), 404

            conn.commit()  # Commit the transaction
            logger.debug(f"Successfully committed the status update for task {task_id} to {new_status}")

        # Log the success response
        response = jsonify(success=True)
        logger.debug(f"Returning success response for task {task_id}: {response.json}")
        return response

    except Exception as e:
        # Log the detailed error traceback
        logger.error(f"Exception occurred while updating task {task_id} status: {e}")
        logger.error(traceback.format_exc())
        return jsonify(success=False, message="Failed to update task status"), 500

@app.route("/api/pos_names", methods=["GET"])
@login_required
def get_pos_names():
    """
    Fetch POS names based on selected POS ID.

    Query Parameters:
        pos_id (int): The ID of the POS to fetch names for.

    Returns:
        - JSON response with POS names if found.
        - JSON error response if POS ID is not provided or an error occurs.
    """
    pos_id = request.args.get("pos_id")
    if pos_id:
        with engine.connect() as conn:
            pos_names = conn.execute(select(pos_table.c.pos_name).where(pos_table.c.pos_id == pos_id)).fetchall()
        pos_names_list = [pos_name[0] for pos_name in pos_names]
        return jsonify(success=True, pos_names=pos_names_list)
    return jsonify(success=False)

@app.route("/api/pos_ids", methods=["GET"])
@login_required
def get_pos_ids():
    """
    Fetch POS IDs based on selected POS Name.

    Query Parameters:
        pos_name (str): The name of the POS to fetch IDs for.

    Returns:
        - JSON response with POS IDs if found.
        - JSON error response if POS name is not provided or an error occurs.
    """
    pos_name = request.args.get("pos_name")
    if pos_name:
        with engine.connect() as conn:
            pos_ids = conn.execute(select(pos_table.c.pos_id).where(pos_table.c.pos_name == pos_name)).fetchall()
        pos_ids_list = [pos_id[0] for pos_id in pos_ids]
        return jsonify(success=True, pos_ids=pos_ids_list)
    return jsonify(success=False)

@app.route("/api/pos_names_and_ids", methods=["GET"])
@login_required
def get_all_pos_names_and_ids():
    """
    Fetch all POS Names and POS IDs for filter reset.

    Returns:
        - JSON response with all distinct POS names and IDs.
        - JSON error response if an error occurs.
    """
    try:
        with engine.connect() as conn:
            pos_names = conn.execute(select(pos_table.c.pos_name).distinct()).fetchall()
            pos_ids = conn.execute(select(pos_table.c.pos_id).distinct()).fetchall()

        pos_names_list = [pos_name[0] for pos_name in pos_names]
        pos_ids_list = [pos_id[0] for pos_id in pos_ids]

        return jsonify(success=True, pos_names=pos_names_list, pos_ids=pos_ids_list)

    except Exception as e:
        return jsonify(success=False, message="Failed to fetch POS Names and IDs."), 500

def errorhandler(e):
    """
    Handle errors by returning a custom error message.

    Args:
        e (Exception): The exception that was raised.

    Returns:
        - Rendered apology template with the error message and code.
    """
    logger.error(f"Error occurred: {e}")
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=False)  # Set debug to False to avoid detailed traceback in terminal
