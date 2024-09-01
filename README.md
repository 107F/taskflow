# final
This is my final project for the course CS50 by Harvard on EdX 2024
It solves an actual problem of mine: converting an Excel spreadsheet into a more robust SQL database, backbone for a web-based application.
To develop the app, I applied an Agile methodology of small increments, simulating a team work.

# steps
1. set up git/github repositories
2. database configuration - converted csv file, implemented schema in Sqlalchemy core, and migrated data to final database
3. Implemented user authentication with secure registration, login, and session management, ensuring that only registered users can access and manage tasks within the application.
4. Implemented parent template tasks.html that calls 2 partial templates: one in the body, that renders as a table all the records from the database, and one in the sidebar that dynamically filters those records.
5. Filters Implemented for tasks.html
        Search by Text: Filter tasks based on a search query in the task description, notes, or POS name.
        POS ID & POS Name: Filter tasks by specific POS identifiers or names.
        Reconciliation Date Range: Filter tasks within a specified start and end date range.
        Task Status: Filter tasks by status (Backlog, To Do, In Progress, Done).
        Task Priority: Filter tasks by priority level (None, Low, Medium, High).
    Development Process
        Modular code structure with reusable components.
        Dynamic filtering and task management implemented for improved user experience.