# Final Project

This is my final project for the course CS50 by Harvard on EdX 2024. It addresses a real-world problem: converting an Excel spreadsheet into a more robust SQL database, which serves as the backbone for a web-based application. The development of the app follows an Agile methodology with incremental updates, simulating a collaborative teamwork environment.

## Development Roadmap

1. **Version Control Setup**: Initialized Git for local version control and connected the repository to GitHub for remote management and collaboration.

2. **Database Design and Migration**: Designed a structured SQL database schema using SQLAlchemy Core and migrated data from a CSV file to the SQL database.

3. **User Authentication Module**: Developed a secure user authentication system, including user registration, login, and session management, to ensure that only registered users can access and manage tasks.

4. **UI/UX Development for Task Management**: Created a main template `tasks.html` with embedded partial templates:
   - **Task List Template**: Displays all tasks in a table format fetched from the database.
   - **Sidebar Filter Template**: Provides dynamic filtering options for tasks based on various criteria.

5. **Advanced Filtering Functionality**:
   - **Text-Based Search**: Implemented functionality to filter tasks based on a text query in task descriptions, notes, or POS names.
   - **POS-Based Filtering**: Enabled filtering by specific POS identifiers or names.
   - **Date Range Filtering**: Added functionality to filter tasks within a specified date range for reconciliation.
   - **Status and Priority Filters**: Developed filters for task status (Backlog, To Do, In Progress, Done) and priority levels (None, Low, Medium, High).

6. **Task Creation Feature**: Implemented a form-based task creation process, allowing users to submit new tasks that are validated, inserted into the database, and immediately rendered on the task management page.

7. **Codebase Restructuring**: Refactored the project structure to enhance maintainability and scalability by organizing files into two main directories:
   - **`core/` Directory**: Contains core application components for the Flask web app:
     - `app.py` and `helpers.py` (core logic and utilities)
     - `templates/` (HTML templates for rendering views)
     - `static/` (static assets such as CSS, JavaScript, and images)
     - `flask_session/` (session data storage)
     - `taskflow.db` (primary SQL database)
     - `app.log` (application log file for debugging)
     - `__pycache__/` (Python bytecode cache)
   - **`helpers/` Directory**: Contains non-core scripts and resources:
     - Database management and migration scripts (`db_foreignkeys_update.py`, `db_notnull_update.py`, `db_setup.py`)
     - Legacy and backup database files (`taskflow - Copy.db`, `taskflowold.db`)
     - Development documentation and resources (`structure.txt`, `kb.csv`, and contents of `del_dev_HELPERS/`)

   **Restructuring Rationale**:
   - **Improved Codebase Organization**: Clearly separates core application logic from auxiliary scripts, enhancing code readability.
   - **Enhanced Maintainability**: Facilitates easier updates and debugging by organizing files logically.
   - **Scalability**: Prepares the codebase for future growth and additional features by modularizing components.

## Agile Development Practices

- **Modular Architecture**: Emphasized a modular code structure with reusable components to facilitate scalability and ease of maintenance.
- **Dynamic Task Management**: Integrated dynamic filtering and task management features to provide a more interactive user experience.
- **Continuous Integration**: Regularly committed changes to GitHub, leveraging version control to manage incremental updates and collaboration.

---

This README provides a comprehensive overview of the project, highlighting key development steps and architectural decisions to ensure a robust and scalable web application.
