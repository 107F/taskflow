# final
This is my final project for the course CS50 by Harvard on EdX 2024 

# steps
1. set up git/github repositories
2. database configuration - converted csv file, implemented schema in Sqlalchemy core, and migrated data to final database
3. Implemented user authentication with secure registration, login, and session management, ensuring that only registered users can access and manage tasks within the application.
4. Filters Implemented for tasks.html
        Search by Text: Filter tasks based on a search query in the task description, notes, or POS name.
        POS ID & POS Name: Filter tasks by specific POS identifiers or names.
        Reconciliation Date Range: Filter tasks within a specified start and end date range.
        Task Status: Filter tasks by status (Backlog, To Do, In Progress, Done).
        Task Priority: Filter tasks by priority level (None, Low, Medium, High).
    Development Process
        Modular code structure with reusable components.
        Dynamic filtering and task management implemented for improved user experience.
5. Moved all task filters to a reusable sidebar template to maintain a clean and consistent layout across pages.
6. Refactored the DOM by moving most of the code from `tasks.html` to a partial template for easier maintenance and reuse across different pages.