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

# Set up SQLAlchemy
DATABASE_URL = "sqlite:///taskflow.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables
tasks_table = Table('tasks', metadata, autoload_with=engine)
pos_table = Table('pos', metadata, autoload_with=engine)
rec_table = Table('rec', metadata, autoload_with=engine)
blockers_table = Table('blockers', metadata, autoload_with=engine)

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
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        hash_pw = generate_password_hash(request.form.get("password"))

        try:
            with engine.connect() as conn:
                conn.execute(
                    users_table.insert().values(username=request.form.get("username"), password_hash=hash_pw)
                )
        except Exception as e:
            return apology("username already exists", 400)

        return redirect("/login")

    else:
        return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        with engine.connect() as conn:
            query = select([users_table]).where(users_table.c.username == request.form.get("username"))
            rows = conn.execute(query).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        session["user_id"] = rows[0]["user_id"]
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

    return render_template("tasks.html", tasks=tasks)

# Route to filter tasks based on POS ID, POS Name, and search query
@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    """Filter tasks based on POS ID, POS Name, and search query"""
    data = request.get_json()
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name")
    search_query = data.get("search_query")

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
            blockers_table.c.blocker_responsible,
            blockers_table.c.blocker_resolved,
            blockers_table.c.blocker_res_date
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id)
            .join(blockers_table, tasks_table.c.blocker_id == blockers_table.c.blocker_id, isouter=True)
        )

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

    tasks_list = [dict(task) for task in tasks]
    return jsonify(tasks=tasks_list)

# Kanban route
@app.route("/kanban")
@login_required
def kanban():
    """Show Kanban board"""
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

    return render_template("kanban.html", tasks=tasks)

# Modify task route
@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    """Modify an existing task"""
    with engine.connect() as conn:
        if request.method == "GET":
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
                conn.execute(query)

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
