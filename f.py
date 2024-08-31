from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Boolean, text
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError

# Connect to the SQLite database
db_path = 'sqlite:///taskflow.db'  # Using relative path
engine = create_engine(db_path)
metadata = MetaData()

# Reflect existing tables
metadata.reflect(bind=engine)

# Backup original tables
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE tasks RENAME TO tasks_backup;"))
        conn.execute(text("ALTER TABLE rec RENAME TO rec_backup;"))
        conn.execute(text("ALTER TABLE blockers RENAME TO blockers_backup;"))
        print("Backup tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error during renaming tables: {e}")
        exit(1)  # Exit if renaming fails

# Define new tables with updated schema (nullable fields)
tasks = Table(
    'tasks', metadata,
    Column('task_id', Integer, primary_key=True, nullable=False),
    Column('task_desc', String),
    Column('task_status', String),
    Column('task_priority', String),
    Column('task_start_date', Date),
    Column('task_due_date', Date),
    Column('task_notes', String),
    Column('pos_id', Integer, nullable=False),
    Column('blocker_id', Integer),
    Column('rec_id', Integer),
    extend_existing=True  # Allow redefinition
)

rec = Table(
    'rec', metadata,
    Column('rec_id', Integer, primary_key=True, nullable=False),
    Column('rec_date', Date),
    Column('rec_certified', Boolean),
    Column('task_id', Integer),
    Column('pos_id', Integer),
    Column('blocker_id', Integer),
    extend_existing=True  # Allow redefinition
)

blockers = Table(
    'blockers', metadata,
    Column('blocker_id', Integer, primary_key=True, nullable=False),
    Column('blocker_desc', String),
    Column('blocker_responsible', String),
    Column('blocker_resolved', Boolean),
    Column('blocker_res_date', Date),
    Column('pos_id', Integer),
    Column('rec_id', Integer),
    Column('task_id', Integer),
    extend_existing=True  # Allow redefinition
)

# Create new tables
metadata.create_all(engine)

# Insert data from backup tables to new tables
with engine.begin() as conn:  # Use begin() to ensure transactions
    try:
        # Copy data from tasks_backup to tasks
        tasks_backup = Table('tasks_backup', metadata, autoload_with=engine)
        select_stmt = select(tasks_backup)
        result = conn.execute(select_stmt)
        for row in result:
            conn.execute(tasks.insert().values(row._mapping))

        # Copy data from rec_backup to rec
        rec_backup = Table('rec_backup', metadata, autoload_with=engine)
        select_stmt = select(rec_backup)
        result = conn.execute(select_stmt)
        for row in result:
            conn.execute(rec.insert().values(row._mapping))

        # Copy data from blockers_backup to blockers
        blockers_backup = Table('blockers_backup', metadata, autoload_with=engine)
        select_stmt = select(blockers_backup)
        result = conn.execute(select_stmt)
        for row in result:
            conn.execute(blockers.insert().values(row._mapping))

        print("Data copied successfully to new tables.")
        
    except SQLAlchemyError as e:
        print(f"Error during data copying: {e}")
        exit(1)  # Exit if data copying fails

# Drop the backup tables
with engine.connect() as conn:
    try:
        # Disable foreign key checks to drop tables safely
        conn.execute(text("PRAGMA foreign_keys=OFF;"))
        
        # Drop the backup tables
        conn.execute(text("DROP TABLE IF EXISTS tasks_backup;"))
        conn.execute(text("DROP TABLE IF EXISTS rec_backup;"))
        conn.execute(text("DROP TABLE IF EXISTS blockers_backup;"))

        # Re-enable foreign key checks
        conn.execute(text("PRAGMA foreign_keys=ON;"))

        print("Backup tables dropped successfully.")
    except SQLAlchemyError as e:
        print(f"Error during dropping backup tables: {e}")

print("Database schema updated successfully.")
