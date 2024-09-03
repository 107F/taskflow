from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.exc import SQLAlchemyError

# Connect to the SQLite database
db_path = 'sqlite:///taskflow.db'  # Using relative path
engine = create_engine(db_path)
metadata = MetaData()

# Reflect existing tables
metadata.reflect(bind=engine)

# Function to recreate tables with foreign keys using raw SQL commands
def recreate_tables_with_foreign_keys(engine):
    try:
        with engine.connect() as conn:
            # Begin a transaction
            with conn.begin():
                # Disable foreign key checks
                conn.execute(text("PRAGMA foreign_keys=OFF;"))

                # Rename the original tables
                conn.execute(text("ALTER TABLE tasks RENAME TO old_tasks;"))
                conn.execute(text("ALTER TABLE rec RENAME TO old_rec;"))
                conn.execute(text("ALTER TABLE blockers RENAME TO old_blockers;"))

                # Recreate the 'tasks' table with foreign keys
                conn.execute(text("""
                    CREATE TABLE tasks (
                        task_id INTEGER NOT NULL, 
                        task_desc VARCHAR, 
                        task_status VARCHAR, 
                        task_priority VARCHAR, 
                        task_start_date DATE, 
                        task_due_date DATE, 
                        task_notes VARCHAR, 
                        pos_id INTEGER NOT NULL, 
                        blocker_id INTEGER, 
                        rec_id INTEGER, 
                        PRIMARY KEY (task_id), 
                        CHECK (task_status IN ('Backlog', 'To Do', 'In Progress', 'Done')), 
                        CHECK (task_priority IN ('None', 'Low', 'Medium', 'High')),
                        FOREIGN KEY(pos_id) REFERENCES pos (pos_id),
                        FOREIGN KEY(blocker_id) REFERENCES blockers (blocker_id),
                        FOREIGN KEY(rec_id) REFERENCES rec (rec_id)
                    );
                """))

                # Recreate the 'rec' table with foreign keys
                conn.execute(text("""
                    CREATE TABLE rec (
                        rec_id INTEGER NOT NULL, 
                        rec_date DATE, 
                        rec_certified BOOLEAN, 
                        task_id INTEGER, 
                        pos_id INTEGER, 
                        blocker_id INTEGER, 
                        PRIMARY KEY (rec_id),
                        FOREIGN KEY(task_id) REFERENCES tasks (task_id),
                        FOREIGN KEY(pos_id) REFERENCES pos (pos_id),
                        FOREIGN KEY(blocker_id) REFERENCES blockers (blocker_id)
                    );
                """))

                # Recreate the 'blockers' table with foreign keys
                conn.execute(text("""
                    CREATE TABLE blockers (
                        blocker_id INTEGER NOT NULL, 
                        blocker_desc VARCHAR, 
                        blocker_responsible VARCHAR, 
                        blocker_resolved BOOLEAN, 
                        blocker_res_date DATE, 
                        pos_id INTEGER, 
                        rec_id INTEGER, 
                        task_id INTEGER, 
                        PRIMARY KEY (blocker_id),
                        FOREIGN KEY(pos_id) REFERENCES pos (pos_id),
                        FOREIGN KEY(rec_id) REFERENCES rec (rec_id),
                        FOREIGN KEY(task_id) REFERENCES tasks (task_id)
                    );
                """))

                # Copy data from the old tables to the new tables
                conn.execute(text("""
                    INSERT INTO tasks (task_id, task_desc, task_status, task_priority, task_start_date, task_due_date, task_notes, pos_id, blocker_id, rec_id)
                    SELECT task_id, task_desc, task_status, task_priority, task_start_date, task_due_date, task_notes, pos_id, blocker_id, rec_id FROM old_tasks;
                """))

                conn.execute(text("""
                    INSERT INTO rec (rec_id, rec_date, rec_certified, task_id, pos_id, blocker_id)
                    SELECT rec_id, rec_date, rec_certified, task_id, pos_id, blocker_id FROM old_rec;
                """))

                conn.execute(text("""
                    INSERT INTO blockers (blocker_id, blocker_desc, blocker_responsible, blocker_resolved, blocker_res_date, pos_id, rec_id, task_id)
                    SELECT blocker_id, blocker_desc, blocker_responsible, blocker_resolved, blocker_res_date, pos_id, rec_id, task_id FROM old_blockers;
                """))

                # Drop the old tables
                conn.execute(text("DROP TABLE old_tasks;"))
                conn.execute(text("DROP TABLE old_rec;"))
                conn.execute(text("DROP TABLE old_blockers;"))

                # Re-enable foreign key checks
                conn.execute(text("PRAGMA foreign_keys=ON;"))

            print("Foreign keys added successfully, and tables recreated.")
    except SQLAlchemyError as e:
        print(f"Error while recreating tables with foreign keys: {e}")

# Call the function to recreate tables with foreign keys
recreate_tables_with_foreign_keys(engine)
