import sqlite3
import csv
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Boolean, ForeignKey, CheckConstraint, exc

# Paths for the databases
csv_file_path = 'kb.csv'
taskflow_db_path = 'sqlite:///taskflow.db'   # Final taskflow database

# Step 1: Convert CSV to Temporary SQLite Database using sqlite3

# Create a temporary SQLite database
temp_db = ':memory:'  # Using an in-memory SQLite database

# Connect to the temporary SQLite database
conn = sqlite3.connect(temp_db)
c = conn.cursor()

# Create temp_tasks table in the temporary SQLite database
c.execute('''
CREATE TABLE IF NOT EXISTS temp_tasks (
    pos_id INTEGER,
    reconciliation_date TEXT,
    reconciliation_certified TEXT,
    task_description TEXT,
    task_status TEXT,
    task_priority TEXT,
    task_start_date TEXT,
    task_due_date TEXT,
    task_notes TEXT
)
''')

# Function to convert CSV dates from DD-MMM format to YYYY-MM-DD format
def convert_date(date_str):
    return datetime.strptime(date_str, '%d-%b').replace(year=2024).strftime('%Y-%m-%d')

# Read and insert CSV data into the temp_tasks table
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        c.execute('''
        INSERT INTO temp_tasks (pos_id, reconciliation_date, reconciliation_certified, task_description, task_status, task_priority, task_start_date, task_due_date, task_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(row['pos_id']),
            convert_date(row['reconciliation_date']),
            row['reconciliation_certified'].lower(),
            row['task_description'],
            row['task_status'],
            row['task_priority'],
            convert_date(row['task_start_date']),
            convert_date(row['task_due_date']),
            row['task_notes']
        ))

# Commit the data to the temp database
conn.commit()

# Step 2: Create the Final `taskflow` Database and Populate it Using SQLAlchemy Core

# Create SQLAlchemy engine and metadata for the taskflow database
engine = create_engine(taskflow_db_path, echo=True)
metadata = MetaData()

# Define the POS table schema
pos_table = Table('pos', metadata,
    Column('pos_id', Integer, primary_key=True),
    Column('pos_name', String, unique=True, nullable=False)
)

# Define the Tasks table schema
tasks_table = Table('tasks', metadata,
    Column('task_id', Integer, primary_key=True, autoincrement=True),
    Column('pos_id', Integer, ForeignKey('pos.pos_id'), nullable=False),
    Column('reconciliation_date', Date, nullable=False),
    Column('reconciliation_certified', Boolean, nullable=False),
    Column('task_description', String, nullable=False),
    Column('task_status', String, CheckConstraint("task_status IN ('Backlog', 'To Do', 'In Progress', 'Done')"), nullable=False),
    Column('task_priority', String, CheckConstraint("task_priority IN ('None', 'Low', 'Medium', 'High')"), nullable=False),
    Column('task_start_date', Date, nullable=False),
    Column('task_due_date', Date, nullable=False),
    Column('task_notes', String)
)

# Create the tables in the taskflow database
metadata.create_all(engine)

# Insert POS data into the taskflow database
pos_data = [
    {'pos_id': 1, 'pos_name': "Bagnore"},
    {'pos_id': 2, 'pos_name': "Vivo d'Orcia"},
    {'pos_id': 7, 'pos_name': "Bagnolo"},
    {'pos_id': 9, 'pos_name': "Castiglione d'Orcia"},
    {'pos_id': 13, 'pos_name': "Castell'Azzara"},
    {'pos_id': 14, 'pos_name': "Abbadia San Salvatore"},
    {'pos_id': 17, 'pos_name': "Arcidosso"},
    {'pos_id': 18, 'pos_name': "Pienza"},
    {'pos_id': 20, 'pos_name': "Pitigliano"},
    {'pos_id': 27, 'pos_name': "Castelnuovo Berardenga"},
    {'pos_id': 29, 'pos_name': "Canino"},
    {'pos_id': 30, 'pos_name': "Grotte di Castro"},
    {'pos_id': 31, 'pos_name': "Bolsena"},
    {'pos_id': 32, 'pos_name': "Montalto di Castro"},
    {'pos_id': 33, 'pos_name': "Manciano"},
    {'pos_id': 35, 'pos_name': "Grotte Santo Stefano"},
    {'pos_id': 36, 'pos_name': "Castelnuovo Val di Cecina"},
    {'pos_id': 37, 'pos_name': "Pomarance"},
    {'pos_id': 38, 'pos_name': "Larderello"},
    {'pos_id': 39, 'pos_name': "Peccioli"},
    {'pos_id': 40, 'pos_name': "Montaione"},
    {'pos_id': 41, 'pos_name': "Santa Fiora"},
    {'pos_id': 42, 'pos_name': "Castel del Piano"},
    {'pos_id': 43, 'pos_name': "Piancastagnaio"},
    {'pos_id': 44, 'pos_name': "Paganico"},
    {'pos_id': 45, 'pos_name': "Monticiano"},
    {'pos_id': 46, 'pos_name': "Capranica"},
    {'pos_id': 48, 'pos_name': "Seggiano"},
    {'pos_id': 49, 'pos_name': "Sede"}
]

with engine.connect() as conn:
    conn.execute(pos_table.insert(), pos_data)

# Transfer data from the temporary SQLite database to the final taskflow database
temp_cursor = c.execute('SELECT * FROM temp_tasks')
task_rows = temp_cursor.fetchall()

# Inserting data into the final database using SQLAlchemy Core
with engine.connect() as conn:
    try:
        for row in task_rows:
            conn.execute(tasks_table.insert().values(
                pos_id=row[0],
                reconciliation_date=datetime.strptime(row[1], '%Y-%m-%d').date(),
                reconciliation_certified=row[2] == 'true',
                task_description=row[3],
                task_status=row[4],
                task_priority=row[5],
                task_start_date=datetime.strptime(row[6], '%Y-%m-%d').date(),
                task_due_date=datetime.strptime(row[7], '%Y-%m-%d').date(),
                task_notes=row[8]
            ))
        conn.commit()
    except exc.SQLAlchemyError as e:
        print(f"Error occurred: {e}")
        conn.rollback()

print("Database created and populated successfully.")
