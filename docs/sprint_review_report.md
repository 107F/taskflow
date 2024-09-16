# Kanban Board Task Management System - Project Development Overview

This project was developed as the final assignment for the CS50 course by Harvard on EdX 2024. It addresses a real-world need for a more robust and scalable task management system by converting a static Excel spreadsheet into a SQL database, which serves as the foundation for a web-based Kanban board application. The development process adhered to Agile methodology, enabling iterative development and continuous feedback. 

## Requirements and Objectives

- **Project Goal:** To create a Kanban board task management system tailored for a grocery and consumer goods retailer with 28 points of sale.
- **Core Functionalities:**
  - Implement a Kanban board for visualizing and managing tasks.
  - Provide user authentication and secure access to the task management system.
  - Enable CRUD operations and advanced filtering options for tasks.
- **Scope:** Develop a web-based solution using Python, Flask, SQLAlchemy, HTML, CSS, and JavaScript.

## Product Backlog

The initial product backlog was created to outline all features and tasks required to meet the project objectives. It was prioritized based on the core functionalities needed for the Kanban board system, including:

1. **User Authentication:** Secure login, registration, and session management.
2. **Task Management:** CRUD operations for task creation, updating, and deletion.
3. **Kanban Board:** Implementation of a dynamic Kanban board with drag-and-drop functionality.
4. **Filtering and Search:** Advanced filtering options for tasks by POS, status, and priority.
5. **Pagination:** Server-side pagination for efficient task display.

## Sprint Breakdown and Development

### Sprint 0: Project Planning & Requirements Gathering (Week 1)
- **Objective:** Define project scope, gather requirements, and establish the initial product backlog.
- **Tasks:**
  - Identified stakeholders and outlined the system requirements.
  - Defined project objectives and created initial user stories (e.g., user authentication, task management).
  - Prioritized user stories and populated the product backlog.
  - Estimated effort and defined a preliminary timeline for each feature.

### Sprint 1: Environment Setup & User Authentication (Week 1-2)
- **Objective:** Set up the development environment and implement basic user authentication.
- **User Stories Addressed:**
  - As a user, I want to securely log in and register to access my tasks.
- **Tasks:**
  - Set up Git repository and integrated with GitHub for version control.
  - Configured Flask project structure and established the development environment.
  - Designed the SQLAlchemy schema for user accounts, including secure password hashing and session management.
  - Developed and tested user registration, login, and logout functionalities.
  - Created front-end templates for user authentication interfaces.

### Sprint 2: Core Task Management Implementation (Week 2-3)
- **Objective:** Develop the foundational task management features.
- **User Stories Addressed:**
  - As a user, I need to create, edit, and delete tasks to manage my workflow.
- **Tasks:**
  - Designed the database schema for tasks, including fields for task attributes (e.g., title, status, priority).
  - Developed Flask routes for task display and management.
  - Implemented a form-based task creation process with validation and input sanitization.
  - Stored task data in the SQL database and rendered tasks using Jinja2 templates on the front-end.

### Sprint 3: Kanban Board Development (Week 3)
- **Objective:** Implement an interactive Kanban board for task visualization and management.
- **User Stories Addressed:**
  - As a user, I want to visualize tasks on a Kanban board and move them between columns.
- **Tasks:**
  - Researched JavaScript libraries and selected one for implementing the drag-and-drop Kanban board.
  - Developed the Kanban board page, integrating it with the task management system.
  - Implemented drag-and-drop functionality to allow tasks to be moved between columns.
  - Integrated AJAX calls to update task status in the database in real-time.
  - Enhanced the user interface for a seamless user experience.

### Sprint 4: Advanced Features & Filtering Implementation (Week 3-4)
- **Objective:** Enhance task management with advanced features such as filtering, search, and pagination.
- **User Stories Addressed:**
  - As a user, I want to filter and search tasks by various criteria (e.g., POS, status).
  - As a user, I need to view tasks in a paginated format for better navigation.
- **Tasks:**
  - Developed advanced filtering mechanisms including text-based search, POS-based filtering, and date range filtering.
  - Implemented server-side pagination using SQLAlchemy’s `LIMIT` and `OFFSET` clauses.
  - Created front-end controls for dynamic pagination, enabling smooth navigation through tasks.
  - Tested and refined filtering and pagination functionalities to ensure consistency and performance.

### Sprint 5: Testing, Debugging, & Refactoring (Week 4)
- **Objective:** Ensure application stability through testing, debugging, and code refactoring.
- **User Stories Addressed:**
  - As a user, I want a reliable system that performs consistently across different use cases.
- **Tasks:**
  - Conducted unit and integration testing for core functionalities, including authentication, task management, and Kanban board interactions.
  - Identified and resolved bugs, focusing on data flow and user interaction issues.
  - Refactored `app.py` to move reusable functions to `helpers.py`, enhancing code maintainability.
  - Improved error handling and consolidated exception logging for better debugging.

### Sprint 6: Deployment & Presentation Preparation (Week 4)
- **Objective:** Deploy the application to a production environment and prepare for the final presentation.
- **Tasks:**
  - Set up a production environment using Gunicorn and Nginx.
  - Migrated the database schema and data to the production server.
  - Conducted a final round of testing on the live environment to ensure functionality.
  - Prepared the final presentation to demonstrate the application, highlighting key features and user stories.

## Agile Development Practices and Methodology

Throughout the project, Agile principles and practices were employed to ensure efficient progress and adaptability:
- **Incremental Delivery:** Each sprint delivered a functional increment, providing a shippable product increment by the end of each sprint.
- **Continuous Feedback and Iteration:** Regular reviews and testing were conducted at the end of each sprint, allowing for continuous feedback and iteration.
- **Backlog Refinement:** The product backlog was continually refined based on the outcomes of each sprint and stakeholder feedback.
- **Test-Driven Development (TDD):** Emphasized writing tests for key functionalities before implementation to ensure code reliability and quality.
- **Modular Architecture:** The codebase was structured into reusable components to facilitate scalability and ease of maintenance.

## Conclusion

This project utilized Agile methodology to develop a robust, scalable, and user-friendly Kanban board task management system. The iterative process allowed for continuous improvement and adaptation, ensuring the final product met the requirements and provided a solid foundation for future enhancements.
