# Kanban Board Task Management System - Project Development Overview

This project was developed as the final assignment for the CS50 course by Harvard on EdX 2024. It addresses the need for a robust and scalable task management system by transitioning from a static Excel spreadsheet to a SQL database, serving as the foundation for a web-based Kanban board application. The development process followed Agile methodology, allowing for iterative development and continuous feedback.

## Requirements and Objectives

- **Project Goal:** Develop a Kanban board task management system tailored for a grocery and consumer goods retailer with 28 points of sale.
- **Core Functionalities:**
  - Implement a Kanban board for task visualization and management.
  - Provide user authentication and secure access.
  - Enable CRUD operations and advanced filtering options for tasks.
- **Scope:** Create a web-based solution using Python, Flask, SQLAlchemy, HTML, CSS, and JavaScript.

## Product Backlog

The initial product backlog outlined all features and tasks required to meet project objectives. Prioritized based on core functionalities needed for the Kanban board system:

1. **User Authentication:** Secure login, registration, and session management.
2. **Task Management:** CRUD operations for task creation, updating, and deletion.
3. **Kanban Board:** Dynamic Kanban board with drag-and-drop functionality.
4. **Filtering and Search:** Advanced filtering options for tasks by POS, status, and priority.
5. **Pagination:** Server-side pagination for efficient task display.

## Sprint Breakdown and Development

### Sprint 0: Project Planning & Requirements Gathering (Week 1)
- **Objective:** Define project scope, gather requirements, and establish the product backlog.
- **Tasks:**
  - Identify stakeholders and outline system requirements.
  - Define project objectives and create initial user stories.
  - Prioritize user stories and populate the product backlog.
  - Estimate effort and create a preliminary timeline.

### Sprint 1: Environment Setup & User Authentication (Week 1-2)
- **Objective:** Set up the development environment and implement basic user authentication.
- **User Stories Addressed:** Secure user login and registration.
- **Tasks:**
  - Set up Git repository and integrate with GitHub.
  - Configure Flask project structure and establish the environment.
  - Design the SQLAlchemy schema for user accounts with secure password hashing.
  - Develop and test user registration, login, and logout functionalities.
  - Create front-end templates for user authentication interfaces.

### Sprint 2: Core Task Management Implementation (Week 2-3)
- **Objective:** Develop foundational task management features.
- **User Stories Addressed:** Users can create, edit, and delete tasks.
- **Tasks:**
  - Design the database schema for tasks.
  - Develop Flask routes for task display and management.
  - Implement form-based task creation with validation.
  - Store task data in SQL database and render using Jinja2 templates.

### Sprint 3: Kanban Board Development (Week 3)
- **Objective:** Implement an interactive Kanban board for task visualization.
- **User Stories Addressed:** Users can visualize and move tasks on a Kanban board.
- **Tasks:**
  - Research JavaScript libraries for drag-and-drop functionality.
  - Develop the Kanban board page, integrating it with task management.
  - Implement drag-and-drop functionality with real-time status updates.
  - Enhance the user interface for a seamless experience.

### Sprint 4: Advanced Features & Filtering Implementation (Week 3-4)
- **Objective:** Enhance task management with filtering, search, and pagination.
- **User Stories Addressed:** Users can filter and search tasks; view tasks in a paginated format.
- **Tasks:**
  - Implement advanced filtering mechanisms, including text-based search and POS filtering.
  - Develop server-side pagination using SQLAlchemy.
  - Create front-end controls for dynamic pagination.
  - Test and refine filtering and pagination functionalities.

### Sprint 5: Testing, Debugging, & Refactoring (Week 4)
- **Objective:** Ensure application stability through testing and code refactoring.
- **User Stories Addressed:** Deliver a reliable system.
- **Tasks:**
  - Conduct unit and integration testing for core functionalities.
  - Identify and resolve bugs, focusing on data flow and user interactions.
  - Refactor code for maintainability and move reusable functions to `helpers.py`.
  - Improve error handling and consolidate logging.

### Sprint 6: Deployment (Week 4)
- **Objective:** Deploy the application to a production environment.
- **Tasks:**
  - Set up a production environment on WSL using Gunicorn and Nginx.
  - Configure a virtual environment and install dependencies.
  - Update environment variables, including setting a secure `SECRET_KEY`.
  - Adjust the database path to an absolute path for production use.
  - Create a shell script for faster application startup.
  - Test the application on the live environment to ensure functionality.

### Sprint 7: Presentation Preparation (End of Week 4)
- **Objective:** Prepare for the final presentation of the application.
- **Tasks:**
  - Compile and organize all project documentation, including the deployment guide and user manual.
  - Prepare a demonstration plan highlighting key features and user stories.
  - Rehearse the presentation to ensure smooth delivery, focusing on the system’s functionalities and development process.
  - Create visual aids such as screenshots, diagrams, and flowcharts to support the presentation.

## Agile Development Practices and Methodology

Throughout the project, Agile principles and practices were implemented to ensure efficient progress and adaptability:
- **Incremental Delivery:** Each sprint produced a functional increment, providing a shippable product at the end of each iteration.
- **Continuous Feedback:** Regular reviews and testing were conducted at the end of each sprint to gather feedback.
- **Backlog Refinement:** The product backlog was continuously refined based on sprint outcomes and stakeholder input.
- **Test-Driven Development (TDD):** Emphasized writing tests for key functionalities before implementation to ensure reliability.
- **Modular Architecture:** The codebase was organized into reusable components to facilitate scalability and maintenance.

## Conclusion

The development of the Kanban board task management system followed Agile methodology, resulting in a robust, scalable, and user-friendly application. By breaking down the project into iterative sprints and focusing on continuous improvement, the final product successfully met all requirements and established a strong foundation for future enhancements.
