# Final Project

This is my final project for the course CS50 by Harvard on EdX 2024. It solves an actual problem of mine: converting an Excel spreadsheet into a more robust SQL database, which serves as the backbone for a web-based application. The development of the app follows an Agile methodology with small increments, simulating a teamwork environment.

## Steps

1. **Set up Git/GitHub repositories**: Initialized the version control system to manage codebase and track project progress.

2. **Database Configuration**: Converted CSV file to a structured SQL database schema using SQLAlchemy Core and migrated the data to the final database.

3. **User Authentication**: Implemented secure user registration, login, and session management, ensuring that only registered users can access and manage tasks within the application.

4. **Task Management Templates**: Developed a parent template `tasks.html` that includes two partial templates:
   - **Body Template**: Renders a table displaying all task records from the database.
   - **Sidebar Template**: Dynamically filters tasks based on various criteria.

5. **Task Filters for `tasks.html`**:
   - **Search by Text**: Filter tasks based on a search query in the task description, notes, or POS name.
   - **POS ID & POS Name**: Filter tasks by specific POS identifiers or names.
   - **Reconciliation Date Range**: Filter tasks within a specified start and end date range.
   - **Task Status**: Filter tasks by status (Backlog, To Do, In Progress, Done).
   - **Task Priority**: Filter tasks by priority level (None, Low, Medium, High).

6. **Create Task Functionality**: Implemented the Create Task functionality, where users can submit a form to add new tasks, which are validated and inserted into the database, then dynamically rendered with all updated tasks on the main task management page.

## Development Process

- **Modular Code Structure**: Ensured a modular approach with reusable components to enhance maintainability and scalability.
- **Dynamic Filtering and Task Management**: Implemented dynamic filtering and task management features to improve user experience.
