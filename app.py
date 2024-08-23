from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, select, and_, or_
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
    return redirect("/tasks")

@app.route("/register", methods=["GET", "POST"])
def register():
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
                conn.execute(users_table.insert().values(username=request.form.get("username"), password_hash=hash_pw))
                conn.commit()
            flash("Registration successful! Please log in.")
        except Exception as e:
            return apology("username already exists", 400)

        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")
        if not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        with engine.connect() as conn:
            query = select(users_table.c.user_id, users_table.c.username, users_table.c.password_hash).where(users_table.c.username == request.form.get("username"))
            rows = conn.execute(query).fetchall()

        if len(rows) != 1:
            flash("Username does not exist. Please register.")
            return redirect("/register")
        elif not check_password_hash(rows[0][2], request.form.get("password")):
            flash("Incorrect password. Please try again.")
            return redirect("/login")

        session["user_id"] = rows[0][0]
        return redirect("/tasks")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/login")

@app.route("/tasks")
@login_required
def tasks():
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
            rec_table.c.rec_certified
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id, isouter=True)
        )
        tasks = conn.execute(query).fetchall()

        pos_data = conn.execute(select(pos_table.c.pos_id, pos_table.c.pos_name)).fetchall()

    return render_template("tasks.html", tasks=tasks, pos_data=pos_data)

@app.route("/filter_tasks", methods=["POST"])
@login_required
def filter_tasks():
    data = request.get_json()
    search_query = data.get("search_query", "")
    pos_id = data.get("pos_id")
    pos_name = data.get("pos_name")

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
            rec_table.c.rec_certified
        ).select_from(
            tasks_table
            .join(pos_table, tasks_table.c.pos_id == pos_table.c.pos_id)
            .join(rec_table, tasks_table.c.rec_id == rec_table.c.rec_id, isouter=True)
        )

        conditions = []
        if pos_id:
            conditions.append(pos_table.c.pos_id == pos_id)
        if pos_name:
            conditions.append(pos_table.c.pos_name == pos_name)
        if search_query:
            search_term = f"%{search_query}%"
            conditions.append(or_(
                tasks_table.c.task_desc.ilike(search_term),
                tasks_table.c.task_status.ilike(search_term),
                tasks_table.c.task_priority.ilike(search_term),
                tasks_table.c.task_notes.ilike(search_term),
                pos_table.c.pos_name.ilike(search_term)
            ))

        if conditions:
            query = query.where(and_(*conditions))

        tasks = conn.execute(query).fetchall()

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

    return jsonify(tasks=tasks_list)

@app.route("/kanban")
@login_required
def kanban():
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

@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
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

def errorhandler(e):
    return apology(e.name, e.code)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
