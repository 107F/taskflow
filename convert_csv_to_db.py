import sqlite3
import csv
from datetime import datetime

# Define the paths
csv_file_path = 'kb.csv'  # Use the relative path since it's in the same directory
db_file_path = 'tasks.db'  # The database will be created in the same directory

# Connect to SQLite database (or create it)
conn = sqlite3.connect(db_file_path)
c = conn.cursor()

# Create the Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00
)
''')

# Create the POS table
c.execute('''
CREATE TABLE IF NOT EXISTS pos (
    pos_id INTEGER PRIMARY KEY,
    pos_name TEXT UNIQUE
)
''')

# Create the Tasks table
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pos_id INTEGER,
    reconciliation_date DATE,
    certified BOOLEAN,
    description TEXT,
    status TEXT,
    priority TEXT,
    start_date DATE,
    due_date DATE,
    notes TEXT,
    FOREIGN KEY (pos_id) REFERENCES pos (pos_id)
)
''')

# Insert POS data
pos_data = [
    (1, "Bagnore"),
    (2, "Vivo d'Orcia"),
    (7, "Bagnolo"),
    (9, "Castiglione d'Orcia"),
    (13, "Castell'Azzara"),
    (14, "Abbadia San Salvatore"),
    (17, "Arcidosso"),
    (18, "Pienza"),
    (20, "Pitigliano"),
    (27, "Castelnuovo Berardenga"),
    (29, "Canino"),
    (30, "Grotte di Castro"),
    (31, "Bolsena"),
    (32, "Montalto di Castro"),
    (33, "Manciano"),
    (35, "Grotte Santo Stefano"),
    (36, "Castelnuovo Val di Cecina"),
    (37, "Pomarance"),
    (38, "Larderello"),
    (39, "Peccioli"),
    (40, "Montaione"),
    (41, "Santa Fiora"),
    (42, "Castel del Piano"),
    (43, "Piancastagnaio"),
    (44, "Paganico"),
    (45, "Monticiano"),
    (46, "Capranica"),
    (48, "Seggiano"),
    (49, "Sede")
]

c.executemany('INSERT OR IGNORE INTO pos (pos_id, pos_name) VALUES (?, ?)', pos_data)

# Function to convert CSV dates from DD-MMM format to YYYY-MM-DD format
def convert_date(date_str):
    return datetime.strptime(date_str, '%d-%b').replace(year=2024).strftime('%Y-%m-%d')

# Read and insert CSV data into the tasks table
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        c.execute('''
        INSERT INTO tasks (pos_id, reconciliation_date, certified, description, status, priority, start_date, due_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(row['pos_id']),  # Match the CSV column name
            convert_date(row['reconciliation_date']),
            row['certified'].lower() == 'true',
            row['description'],
            row['status'],
            row['priority'],
            convert_date(row['start_date']),
            convert_date(row['due_date']),
            row['notes']
        ))

# Commit and close the connection
conn.commit()
conn.close()
