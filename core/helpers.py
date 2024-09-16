"""
helpers.py

Developed by Stefania Galatolo, assisted by ChatGPT 4o, because let's be honest, coding is always better with a little AI magic.
Stefania's coding journey was made more exciting with ChatGPT's witty banter and occasional dad jokes. Together, they tackled the 
task management app, making sure no task was left unhandled (or uncommented). 

This file serves as the utility hub for the task management application. It includes helper functions for interacting with the 
SQLite database, handling pagination, fetching POS data, formatting tasks for display, and managing user sessions. 

Key Components:
- Database Setup: Establishes a connection to the SQLite database and reflects its schema.
- Helper Functions: Includes utility functions for pagination, POS data retrieval, and task formatting.
- Decorators and Error Handling: Contains decorators for route protection and rendering apology messages.

Dependencies:
- Flask: Used for web framework capabilities, including session management and rendering templates.
- SQLAlchemy: Provides ORM capabilities to interact with the SQLite database.
- Logging: Facilitates error logging for debugging and monitoring purposes.
"""

from flask import redirect, render_template, session
from functools import wraps
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import sessionmaker
from datetime import date
from math import ceil
import logging
import os
import traceback

# Configure logging to overwrite the log file at each run
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s',
    filemode='w'
)

# Create a logger object
logger = logging.getLogger(__name__)

# Set up SQLAlchemy to connect to the SQLite database
# Using SQLAlchemy to establish a connection with the database, 
# making it possible to query and manipulate data using ORM methods.

# Create an absolute path for the database
base_dir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(base_dir, 'taskflow.db')
DATABASE_URL = f"sqlite:///{database_path}"

try:
    engine = create_engine(DATABASE_URL, echo=False)
    metadata = MetaData()
    metadata.reflect(bind=engine)
except Exception as e:
    logger.error(f"Error establishing database connection: {traceback.format_exc()}")

# Load tables from the database into SQLAlchemy Table objects
# Reflects the database schema into Table objects, making it easier 
# to query and manage the data in those tables.

try:
    tasks_table = Table('tasks', metadata, autoload_with=engine)
    pos_table = Table('pos', metadata, autoload_with=engine)
    rec_table = Table('rec', metadata, autoload_with=engine)
    blockers_table = Table('blockers', metadata, autoload_with=engine)
    users_table = Table('users', metadata, autoload_with=engine)
except Exception as e:
    logger.error(f"Error reflecting database tables: {traceback.format_exc()}")

# Configure session maker
# Establishes a session factory for interacting with the database, 
# ensuring queries are executed in the context of a session.
SessionLocal = sessionmaker(bind=engine)

def get_paginated_tasks(base_query, page, per_page):
    """
    Helper function to paginate tasks based on the provided query.

    This function takes a base SQLAlchemy query, applies pagination, 
    and returns a subset of results based on the current page and the 
    number of items per page.

    Parameters:
    - base_query (SQLAlchemy Select): The base query to paginate.
    - page (int): The current page number.
    - per_page (int): The number of items to display per page.

    Returns:
    - tasks (List): A list of paginated tasks.
    - total_records (int): The total number of records.
    - total_pages (int): The total number of pages.

    Note: This function logs an error message if pagination fails and returns empty values.
    """
    try:
        total_records_query = select(func.count()).select_from(base_query.alias())
        total_records = engine.connect().execute(total_records_query).scalar()
        total_pages = ceil(total_records / per_page)
        paginated_query = base_query.limit(per_page).offset((page - 1) * per_page)
        tasks = engine.connect().execute(paginated_query).fetchall()
        return tasks, total_records, total_pages
    except Exception as e:
        logger.error(f"Error during pagination: {traceback.format_exc()}")
        return [], 0, 0

def fetch_pos_data():
    """
    Helper function to fetch POS data for dropdowns.

    Retrieves POS (Point of Sale) data from the database to populate 
    dropdown menus in the UI, aiding in task filtering and creation.

    Returns:
    - pos_data (List): A list of tuples containing POS IDs and names.

    Note: Logs an error if fetching POS data fails and returns an empty list.
    """
    try:
        with engine.connect() as conn:
            pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()
        return pos_data
    except Exception as e:
        logger.error(f"Error fetching POS data: {traceback.format_exc()}")
        return []

def format_task(task):
    """
    Helper function to format task data for rendering.

    Formats a task object into a dictionary with all relevant fields 
    properly formatted for display purposes, such as converting dates 
    into readable strings.

    Parameters:
    - task (SQLAlchemy RowProxy): The task record to format.

    Returns:
    - formatted_task (dict): A dictionary containing the formatted task data.
    
    Keys include:
    - task_id, task_desc, task_status, task_priority, task_start_date, 
      task_due_date, task_notes, pos_id, pos_name, rec_date, rec_certified, 
      blocker_desc, blocker_responsible.
    """
    task_start_date = task.task_start_date.strftime('%Y-%m-%d') if isinstance(task.task_start_date, date) else "n/a"
    task_due_date = task.task_due_date.strftime('%Y-%m-%d') if isinstance(task.task_due_date, date) else "n/a"
    rec_date = task.rec_date.strftime('%Y-%m-%d') if isinstance(task.rec_date, date) else "n/a"

    return {
        "task_id": task.task_id if task.task_id is not None else "n/a",
        "task_desc": task.task_desc if task.task_desc is not None else "n/a",
        "task_status": task.task_status if task.task_status is not None else "n/a",
        "task_priority": task.task_priority if task.task_priority is not None else "n/a",
        "task_start_date": task_start_date,
        "task_due_date": task_due_date,
        "task_notes": task.task_notes if task.task_notes is not None else "n/a",
        "pos_id": task.pos_id if task.pos_id is not None else "n/a",
        "pos_name": task.pos_name if task.pos_name is not None else "n/a",
        "rec_date": rec_date,
        "rec_certified": "Yes" if task.rec_certified is True else "No" if task.rec_certified is False else "n/a",
        "blocker_desc": task.blocker_desc if task.blocker_desc is not None else "n/a",
        "blocker_responsible": task.blocker_responsible if task.blocker_responsible is not None else "n/a"
    }

def login_required(f):
    """
    Decorate routes to require login.

    A decorator function that wraps around route functions to enforce 
    user authentication. If a user is not logged in, they are redirected 
    to the login page.

    Parameters:
    - f (function): The route function to be decorated.

    Returns:
    - decorated_function (function): The wrapped function with authentication check.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """
    Render message as an apology to the user.

    Renders an apology message to the user using the 'apology.html' 
    template. Typically used to display error messages in a user-friendly 
    manner.

    Parameters:
    - message (str): The error message to display.
    - code (int): The HTTP status code to return (default is 400).

    Returns:
    - tuple (Response, int): The rendered template and HTTP status code.
    """
    return render_template("apology.html", top=code, bottom=message), code
