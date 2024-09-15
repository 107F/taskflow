# helpers.py
from flask import redirect, render_template, session
from functools import wraps
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from math import ceil
import logging
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
DATABASE_URL = "sqlite:///taskflow.db"
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables from the database into SQLAlchemy Table objects
tasks_table = Table('tasks', metadata, autoload_with=engine)
pos_table = Table('pos', metadata, autoload_with=engine)
rec_table = Table('rec', metadata, autoload_with=engine)
blockers_table = Table('blockers', metadata, autoload_with=engine)
users_table = Table('users', metadata, autoload_with=engine)

# Configure session maker
SessionLocal = sessionmaker(bind=engine)

def get_paginated_tasks(base_query, page, per_page):
    """
    Helper function to paginate tasks based on the provided query.
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
    """
    return render_template("apology.html", top=code, bottom=message), code
