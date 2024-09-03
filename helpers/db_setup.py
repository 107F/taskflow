import sqlite3
import csv
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Boolean, ForeignKey, CheckConstraint, exc

"""
This script converts a CSV file containing task data into a relational SQLite database. 
It first loads the data into a temporary in-memory SQLite database using the `sqlite3` module,
and then transfers the data to a final SQLite database managed by SQLAlchemy.

Modules:
    - sqlite3: For interacting with SQLite databases.
    - csv: For reading CSV files.
    - datetime: For handling date conversion.
    - sqlalchemy: For database interaction and schema definition.

Steps:
    1. Convert CSV data into a temporary SQLite database.
    2. Create a final SQLite database with a specified schema using SQLAlchemy.
    3. Transfer data from the temporary database to the final database.
"""

# Paths for the databases
csv_file_path = 'kb.csv'  # Path to the CSV file that contains task data
taskflow_db_path = 'sqlite:///taskflow.db'  # Path to the final SQLite database

# Step 1: Convert CSV to Temporary SQLite Database using sqlite3

# Create a temporary SQLite database in memory
temp_db = ':memory:'  # This creates an in-memory SQLite database, which is temporary and faster

# Connect to the temporary SQLite database
conn = sqlite3.connect(temp_db)  # Establishing a connection to the in-memory SQLite database
c = conn.cursor()  # Creating a cursor object to interact with the database

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
# The above SQL command creates a table named `temp_tasks` with columns that correspond to the task data fields.

# Function to convert CSV dates from DD-MMM format to YYYY-MM-DD format
def convert_date(date_str):
    """
    Converts a date string from 'DD-MMM' format to 'YYYY-MM-DD' format.
    The year is set to 2024.

    Args:
        date_str (str): The date string in 'DD-MMM' format.

    Returns:
        str: The date string in 'YYYY-MM-DD' format.
    """
    return datetime.strptime(date_str, '%d-%b').replace(year=2024).strftime('%Y-%m-%d')

# Read and insert CSV data into the temp_tasks table
with open(csv_file_path, newline='') as csvfile:  # Opening the CSV file
    reader = csv.DictReader(csvfile)  # Creating a CSV dictionary reader to read rows as dictionaries
    for row in reader:  # Looping through each row in the CSV file
        c.execute('''
        INSERT INTO temp_tasks (pos_id, reconciliation_date, reconciliation_certified, task_description, task_status, task_priority, task_start_date, task_due_date, task_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(row['pos_id']),  # Convert pos_id to integer
            convert_date(row['reconciliation_date']),  # Convert reconciliation_date to 'YYYY-MM-DD' format
            row['reconciliation_certified'].lower(),  # Convert reconciliation_certified to lowercase string
            row['task_description'],  # Task description as a string
            row['task_status'],  # Task status as a string
            row['task_priority'],  # Task priority as a string
            convert_date(row['task_start_date']),  # Convert task_start_date to 'YYYY-MM-DD' format
            convert_date(row['task_due_date']),  # Convert task_due_date to 'YYYY-MM-DD' format
            row['task_notes']  # Task notes as a string
        ))

# Commit the data to the temp database to make sure all changes are saved
conn.commit()

# Step 2: Create the Final `taskflow` Database and Populate it Using SQLAlchemy Core

# Create SQLAlchemy engine and metadata for the taskflow database
engine = create_engine(taskflow_db_path, echo=True)  # SQLAlchemy engine to connect to the SQLite database
metadata = MetaData()  # Container object to hold schema details

# Define the Users table schema
users_table = Table('users', metadata,
    Column('user_id', Integer, primary_key=True),  # Primary key column
    Column('username', String, nullable=False, unique=True),  # Unique and non-nullable username
    Column('password_hash', String, nullable=False)  # Non-nullable password hash
)

# Define the POS table schema
pos_table = Table('pos', metadata,
    Column('pos_id', Integer, primary_key=True),  # Primary key column
    Column('pos_name', String, unique=True, nullable=False)  # Unique and non-nullable string column for POS names
)

# Define the Tasks table schema
tasks_table = Table('tasks', metadata,
    Column('task_id', Integer, primary_key=True, autoincrement=True),  # Auto-incrementing primary key
    Column('task_desc', String, nullable=False),  # Task description
    Column('task_status', String, CheckConstraint("task_status IN ('Backlog', 'To Do', 'In Progress', 'Done')"), nullable=False),  # Check constraint for task status
    Column('task_priority', String, CheckConstraint("task_priority IN ('None', 'Low', 'Medium', 'High')"), nullable=False),  # Check constraint for task priority
    Column('task_start_date', Date, nullable=False),  # Task start date
    Column('task_due_date', Date, nullable=False),  # Task due date
    Column('task_notes', String),  # Task notes
    Column('pos_id', Integer, ForeignKey('pos.pos_id'), nullable=False),  # Foreign key referencing POS table
    Column('blocker_id', Integer, ForeignKey('blockers.blocker_id')),  # Foreign key referencing blockers table
    Column('rec_id', Integer, ForeignKey('rec.rec_id'))  # Foreign key referencing rec table
)

# Define the Rec table schema
rec_table = Table('rec', metadata,
    Column('rec_id', Integer, primary_key=True, autoincrement=True),  # Auto-incrementing primary key
    Column('rec_date', Date, nullable=False),  # Reconciliation date
    Column('rec_certified', Boolean, nullable=False),  # Reconciliation certified status
    Column('task_id', Integer, ForeignKey('tasks.task_id')),  # Foreign key referencing tasks table
    Column('pos_id', Integer, ForeignKey('pos.pos_id')),  # Foreign key referencing POS table
    Column('blocker_id', Integer, ForeignKey('blockers.blocker_id'))  # Foreign key referencing blockers table
)

# Define the Blockers table schema
blockers_table = Table('blockers', metadata,
    Column('blocker_id', Integer, primary_key=True, autoincrement=True),  # Auto-incrementing primary key
    Column('blocker_desc', String, nullable=False),  # Blocker description
    Column('blocker_responsible', String, nullable=False),  # Blocker responsible person/role
    Column('blocker_resolved', Boolean, nullable=False),  # Blocker resolved status
    Column('blocker_res_date', Date, nullable=False),  # Blocker resolution date
    Column('pos_id', Integer, ForeignKey('pos.pos_id')),  # Foreign key referencing POS table
    Column('rec_id', Integer, ForeignKey('rec.rec_id')),  # Foreign key referencing rec table
    Column('task_id', Integer, ForeignKey('tasks.task_id'))  # Foreign key referencing tasks table
)

# Create the tables in the taskflow database based on the above schema definitions
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

# Insert the POS data into the `pos` table in the final database
try:
    with engine.begin() as conn:  # Use engine.begin() to ensure the transaction is properly managed
        conn.execute(pos_table.insert(), pos_data)  # Executing the insert statement with the pos_data list
    print("POS data inserted successfully.")
except exc.SQLAlchemyError as e:
    print(f"Error inserting POS data: {e}")

# Transfer data from the temporary SQLite database to the final taskflow database
temp_cursor = c.execute('SELECT * FROM temp_tasks')  # Selecting all rows from the temp_tasks table
task_rows = temp_cursor.fetchall()  # Fetching all rows as a list of tuples

# Inserting data into the final database using SQLAlchemy Core
try:
    with engine.begin() as conn:  # Use engine.begin() to ensure the transaction is properly managed
        for row in task_rows:  # Loop through each row of data
            task_id_result = conn.execute(tasks_table.insert().values(
                pos_id=row[0],  # Integer value for POS ID
                task_desc=row[3],  # Task description string
                task_status=row[4],  # Task status string
                task_priority=row[5],  # Task priority string
                task_start_date=datetime.strptime(row[6], '%Y-%m-%d').date(),  # Convert start date string to date
                task_due_date=datetime.strptime(row[7], '%Y-%m-%d').date(),  # Convert due date string to date
                task_notes=row[8]  # Task notes string
            ))
            # Get the last inserted task_id
            task_id = task_id_result.inserted_primary_key[0]

            # Insert into rec table with the generated task_id
            rec_id_result = conn.execute(rec_table.insert().values(
                rec_date=datetime.strptime(row[1], '%Y-%m-%d').date(),
                rec_certified=row[2] == 'true',
                task_id=task_id,
                pos_id=row[0]
            ))

            rec_id = rec_id_result.inserted_primary_key[0]

            # Update the task row to include the rec_id
            conn.execute(tasks_table.update().where(tasks_table.c.task_id == task_id).values(rec_id=rec_id))
            
    print("Tasks and rec tables populated successfully.")
except exc.SQLAlchemyError as e:  # Handling any SQLAlchemy errors
    print(f"Error occurred while populating tasks and rec tables: {e}")

print("Database created and populated successfully.")  # Final confirmation message
