# Kanban Board Task Management System

#### Video Demo: https://youtu.be/84B34-38W9k

## Description

The **Kanban Board Task Management System** is a web-based application developed by Stefania Galatolo as part of the CS50 course by Harvard on edX 2024. The system is designed to address the challenges faced by a consumer goods retailer with 28 points of sale (POS). Previously, task management relied on static Excel spreadsheets, which introduced limitations in data management, scalability, and collaboration. To address these issues, the system transitions from a spreadsheet-based model to a web-based application using a robust SQL database.

The project leverages Python, Flask, SQLAlchemy, HTML, CSS, and JavaScript to provide a scalable and user-friendly solution for task management, ensuring data persistence and improving efficiency. The development followed Agile methodologies to enable iterative progress and feedback.

## Problem Statement

The retailer previously used an Excel spreadsheet to manage tasks related to its accounts payable processes. This method introduced several limitations:
- **Data Integrity**: Maintaining task data across multiple stores became difficult due to manual updates.
- **Scalability**: As the number of tasks grew, the spreadsheet approach became cumbersome and inefficient.
- **Collaboration**: Real-time collaboration was hindered since Excel does not support dynamic, multi-user task management effectively.
  
To resolve these issues, the system was re-engineered into a web application backed by a SQL database. This allowed the seamless management of tasks, enhanced collaboration, and integration of advanced features like filtering, search, and a Kanban board for visual task management. Additionally, CSV data from the existing spreadsheets was converted into the database to ensure continuity in task tracking.

## Features

- **User Authentication**: Secure user login and registration to manage access to the system.
- **Task Management**: CRUD (Create, Read, Update, Delete) operations for managing tasks, including fields like task description, status, priority, and dates.
- **Kanban Board**: Visual task management using an interactive drag-and-drop interface.
- **Filtering and Search**: Advanced task filtering based on status, priority, and POS (Point of Sale), and search functionality to find tasks by keywords.
- **Pagination**: Server-side pagination for handling large datasets efficiently.
- **CSV to Database Conversion**: Seamless migration of task data from the existing Excel spreadsheets into the SQL database for structured management.

## System Architecture

### High-Level Components

1. **Flask Application (`app.py`)**: Serves as the core controller for the application, managing routes, user interactions, and API endpoints.
2. **Database Layer**: Utilizes SQLAlchemy ORM to interact with the SQLite database (`taskflow.db`), ensuring data persistence for tasks, POS information, users, and other entities.
3. **Helper Functions (`helpers.py`)**: Provides utility functions for database operations, pagination, and session management to promote code reusability.
4. **Frontend (HTML, CSS, JavaScript)**: Renders the UI using Jinja2 templates, includes CSS for styling, and uses JavaScript for interactive components like the drag-and-drop Kanban board.
5. **Documentation**: The `docs` directory contains architecture documentation, product backlog, and the development timeline for reference.

## AI Utilization

In accordance with CS50’s final project guidelines, AI-based software such as **ChatGPT** was used as a tool to amplify productivity. The essence of the work remains original, and AI was employed strictly for assistance with code generation, debugging, and documentation refinement. All use of AI tools has been cited in the comments of the relevant code sections, adhering to the course's policies.

## Key Functionalities

### User Authentication
- Secure user registration and login functionality.
- Passwords are securely hashed and stored.
- Sessions are managed to ensure proper access control.

### Task Management
- Full CRUD operations for task creation, modification, deletion, and viewing.
- Tasks can be filtered and searched based on criteria like status, priority, and dates.
- Data migration from CSV (Excel spreadsheets) to SQL was handled to ensure no disruption of existing task records.

### Kanban Board
- Visualizes tasks in different statuses such as "Backlog," "To Do," "In Progress," and "Done."
- Drag-and-drop functionality enables real-time updates of task statuses.
- AJAX integration ensures dynamic updates without page reloads.

### Task Filtering and Search
- Users can filter tasks based on POS, status, priority, and due dates.
- A search bar allows users to locate tasks quickly based on keywords.
- Efficient task handling, especially when dealing with large datasets, is managed through server-side pagination.

### Directory Structure

- **Project Root**:
  - `README.md`: Provides an overview and setup instructions for the project.
  - `requirements.txt`: Lists Python dependencies required for the project.
  - `run_taskflow`: Shell script for quickly launching the application.
  - `taskflow`: SQLite database file for data persistence.
  
- **Core Directory**:
  - `app.py`: Main Flask application file.
  - `helpers.py`: Contains utility functions for interacting with the database and session management.
  - `static/`: CSS for styling, JavaScript for interactivity, and images.
  - `templates/`: HTML templates for rendering various pages and components.
  - `taskflow.db`: SQLite database for data storage.
  - `flask_session/`: Stores session data.

- **Docs Directory**: Includes architecture documentation, product backlog, and project timeline.

## Development Process

The project followed an Agile methodology, divided into iterative sprints:

1. **Sprint 0**: Planning and requirements gathering.
2. **Sprint 1**: Setting up the environment and implementing user authentication.
3. **Sprint 2**: Developing core task management functionality.
4. **Sprint 3**: Implementing the Kanban board.
5. **Sprint 4**: Adding advanced features such as filtering, search, and pagination.
6. **Sprint 5**: Testing, debugging, and refactoring the codebase.
7. **Sprint 6**: Deploying the application to a local production environment.
8. **Sprint 7**: Preparing for the final presentation and submitting the project.

## Database Schema

The application uses an SQLite database to store all task-related data:

- **Tasks Table**: Contains task details such as description, status, priority, and dates.
- **POS Table**: Stores POS (Point of Sale) information for each task.
- **Users Table**: Manages user credentials and hashed passwords.
- **Blockers Table**: Tracks any blockers related to tasks.
- **Reconciliation Table**: Contains reconciliation data for tasks as needed.

## Deployment

The system is deployed locally using WSL (Windows Subsystem for Linux) running Ubuntu. Deployment steps include:

- Setting up a virtual environment and installing necessary dependencies.
- Configuring the application to run in production using Gunicorn as the WSGI server.
- Using Nginx as a reverse proxy to handle static file serving and forward requests to Gunicorn.

## Future Enhancements

The following features are considered for future development:
- **Task Assignment**: Enable assigning tasks to different users for better delegation and tracking.
- **Notifications**: Implement notifications to alert users of upcoming task deadlines or important updates.
- **Advanced Reporting**: Develop functionality to generate and export reports based on task data.
- **External Tool Integration**: Explore integrating with tools like Google Sheets or email notifications for enhanced functionality.

## Testing

The application underwent extensive testing to ensure reliability and performance:
- **Unit Tests**: Focused on individual components to ensure each part worked as expected.
- **Integration Tests**: Verified interactions between different components, including database operations and frontend/backend communication.
- **End-to-End Tests**: Simulated real-world scenarios, ensuring that user workflows (e.g., task creation, modification, and status updates) performed seamlessly.
- **Performance Testing**: Ensured the system could handle large task loads without significant performance degradation.

## Conclusion

The **Kanban Board Task Management System** addresses the limitations of the previous spreadsheet-based task management approach by providing a scalable, database-driven solution. This project demonstrates a robust understanding of full-stack web development principles and implements features that improve task tracking, collaboration, and overall efficiency. The structured use of Agile methodologies, combined with the integration of modern web technologies, ensures that the system is both functional and adaptable for future enhancements.

## Acknowledgements

Special thanks to the CS50 course by Harvard on edX for providing the foundation and guidance to build this project.
