# Final Project

This is my final project for the course CS50 by Harvard on EdX 2024. It addresses a real-world problem by converting a static Excel spreadsheet into a more robust and scalable SQL database, which serves as the backbone for a web-based task management application. The development of this app adheres to an Agile methodology, allowing for incremental updates that simulate a collaborative teamwork environment. Each feature has been carefully designed to improve the overall user experience and ensure maintainability.

## Development Roadmap

1. **Version Control Setup**: At the start of the project, a Git repository was initialized for local version control. The repository was connected to GitHub, enabling remote management and fostering a collaborative environment. This step allowed versioning and incremental commits, ensuring that code changes could be tracked effectively, and any issues could be rolled back if necessary.

2. **Database Design and Migration**: A structured SQL database schema was designed using SQLAlchemy Core, providing the app with a robust data layer. The schema was carefully thought out to accommodate the complex relationships between tasks, POS information, reconciliation data, and blockers. The migration process involved converting a CSV file into this schema, leveraging SQLAlchemy’s ORM capabilities. This allowed for seamless querying and manipulation of data as well as laying a foundation for scalable data storage.

3. **User Authentication Module**: A secure user authentication system was built to ensure that only authorized users can access and manage tasks. This system includes user registration, login, and session management. Passwords are securely hashed, and session cookies are used to persist user data across requests. This helps maintain a safe and user-specific environment where task data is protected from unauthorized access.

4. **UI/UX Development for Task Management**: The primary user interface was developed using HTML and JavaScript to enable seamless task management. The main `tasks.html` template dynamically renders all tasks in the system. Additionally, embedded partial templates such as the **Task List Template** and **Sidebar Filter Template** ensure that the user can easily navigate and interact with their tasks:
   - **Task List Template**: Displays tasks in a structured table format, fetched directly from the database, making it easy to view task details at a glance.
   - **Sidebar Filter Template**: Provides users with dynamic filtering options that allow them to refine the task list based on various criteria like POS, status, and priority, improving task visibility.

5. **Advanced Filtering Functionality**: The app incorporates several advanced filtering mechanisms to improve the user experience:
   - **Text-Based Search**: Users can filter tasks based on a text query. This search functionality combs through task descriptions, notes, or POS names, providing fast and relevant results.
   - **POS-Based Filtering**: The app enables users to filter tasks by specific POS identifiers or names, which dynamically adjusts the available tasks on the page.
   - **Date Range Filtering**: Users can specify a start and end date to filter tasks within a particular timeframe. This feature is crucial for users tracking tasks related to reconciliation or other date-sensitive activities.
   - **Status and Priority Filters**: The task list can be filtered by status (Backlog, To Do, In Progress, Done) and priority (None, Low, Medium, High). This allows users to easily focus on the most pressing tasks or those in specific stages of completion.

6. **Task Creation Feature**: A form-based task creation process was implemented, allowing users to create new tasks that are validated before being inserted into the database. This feature is highly interactive, ensuring that new tasks are immediately rendered on the task management page, providing users with real-time feedback and the ability to manage tasks right after creation.

7. **Codebase Restructuring**: To maintain code quality and enhance future scalability, the project was refactored into two main directories:
   - **`core/` Directory**: This directory contains all the critical components of the Flask web application:
     - `app.py` and `helpers.py`: Core logic and utility functions that power the application.
     - `templates/`: HTML templates for rendering views, such as task management and Kanban views.
     - `static/`: Static assets like CSS and JavaScript files that provide the front-end functionality.
     - `taskflow.db`: The SQL database where task and user information is stored.
     - `app.log`: The log file that records application activities, errors, and debugging information.
     - `__pycache__/`: Compiled Python bytecode files to improve performance.
   - **`helpers/` Directory**: Contains auxiliary scripts and resources that assist with database management and documentation. Scripts such as `db_foreignkeys_update.py`, `db_notnull_update.py`, and `db_setup.py` are essential for migrating and updating the database schema.

   **Restructuring Rationale**:
   - **Improved Codebase Organization**: The separation of core logic from auxiliary scripts improves code readability and maintainability, ensuring that the project is easy to navigate.
   - **Enhanced Maintainability**: The modular structure allows for easier updates and debugging, enabling the project to scale smoothly as new features are added.
   - **Scalability**: This refactor ensures that the project can accommodate additional features or changes without sacrificing performance or increasing complexity.

8. **Modify Task Feature**: This feature allows users to modify existing tasks in the database through a form-based interface. 
   - **Form-Based Modification**: Users can update task details such as the POS name, task status, priority, and reconciliation information. 
   - **Partial Updates**: The app only updates fields that have been changed by the user, keeping unmodified fields intact. 
   - **Error Handling**: The app logs any errors that occur during the modification process and provides real-time feedback to the user.
   - **Real-Time Feedback**: Once a task is modified, the page updates with the new information without requiring a full reload, ensuring a smooth user experience.

9. **Kanban Task Management System**: A highly interactive **Kanban board** was implemented to provide users with a visual and intuitive way to manage tasks. This board helps users track the progress of tasks through different stages, ensuring efficient task flow and management.
   
   - **Drag-and-Drop Interface**: Tasks can be easily moved between four columns: **Backlog**, **To Do**, **In Progress**, and **Done**. Users can drag a task card from one column to another, allowing for real-time task reassignment based on current progress. This feature is built using `Sortable.js`, which provides a smooth drag-and-drop experience, making task management both flexible and efficient.
   
   - **Real-Time Status Synchronization**: When a task is moved to a different column, its status is updated instantly in the user interface. Additionally, an asynchronous request is sent to the server to persist the updated status in the database, ensuring that the backend remains in sync with the front-end changes. This immediate feedback loop ensures that users can manage tasks without unnecessary page reloads.
   
   - **Responsive Task Rendering**: Tasks are fetched from the database and rendered in their appropriate columns based on their current status. Each task card contains vital information, such as the task description, priority level, and due date, making it easy for users to understand the task at a glance. The task cards are styled to ensure clarity and readability, even when multiple tasks are displayed.
   
   - **Integrated Filtering and Search**: The Kanban board works in conjunction with the app’s advanced filtering features. Users can filter tasks by POS ID, POS name, status, and priority. The board dynamically adjusts to display only the tasks that match the active filters, enabling focused task management.
   
   - **Error Handling and Rollback**: If an error occurs during a status update (for instance, due to network issues or database constraints), the app automatically reverts the task to its original column and status, maintaining consistency in the UI. This rollback mechanism minimizes disruptions for users, ensuring that task data remains accurate.
   
   - **Mobile-Responsive Design**: The Kanban board is fully responsive, providing an optimized experience across all devices, including desktops, tablets, and mobile phones. The layout and drag-and-drop functionality adapt seamlessly to different screen sizes, ensuring that users can manage tasks from any device without loss of functionality.

## Agile Development Practices

Throughout the project, Agile development practices were employed to ensure efficient progress and continuous improvement:
- **Modular Architecture**: Emphasized a modular code structure with reusable components to facilitate scalability and ease of maintenance.
- **Dynamic Task Management**: Integrated dynamic filtering and task management features to provide a more interactive and user-friendly experience.
- **Continuous Integration**: Regularly committed changes to GitHub, leveraging version control to manage incremental updates and foster collaboration.

---

This README provides a comprehensive overview of the project, highlighting key development steps and architectural decisions that ensure a robust, scalable, and user-friendly web application for task management.
