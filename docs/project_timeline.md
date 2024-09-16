# Kanban Board Task Management System - Estimated Timeline

## Project Timeline Overview

This timeline provides an estimated schedule for the development of the Kanban Board Task Management System. Given that this project is a solo effort undertaken as a side project alongside a full-time job, the outlined schedule is provisional and subject to change. The timeline is designed to be flexible and will be adjusted based on sprint reviews and revisions as part of the Agile development process.

### Estimated Timeline:

#### 1. Planning and Setup (2-3 days)
- **Objective:** Establish the project's foundation through thorough planning and environment setup.
  - **Finalize Database Schema:** Design and finalize the SQL database schema based on the structure of the initial data set from the spreadsheet.
  - **Setup Project Environment:** Configure the Flask project environment in Visual Studio Code, including the installation of required dependencies (Flask, SQLAlchemy).
  - **Initial Flask Setup:** Implement a basic Flask application structure with routes and templates to lay the groundwork for future development.

#### 2. Data Migration (2-3 days)
- **Objective:** Transition existing data from a spreadsheet to a structured SQL database.
  - **Data Cleaning:** Ensure the spreadsheet data is clean, consistent, and ready for migration to prevent data integrity issues.
  - **Migration Script:** Develop a Python script to read the Excel file and populate the SQL database using SQLAlchemy.
  - **Test Migration:** Execute the migration process and verify the integrity and accuracy of the transferred records.

#### 3. Core Functionality Development (7-10 days)
- **Objective:** Implement core task management features, including CRUD operations and task filtering.
  - **Task Management:** 
    - Develop features for creating, viewing, updating, and deleting tasks.
    - Perform thorough testing of CRUD operations to ensure data consistency and reliability.
  - **Querying and Filtering:**
    - Build the user interface for filtering tasks based on various criteria such as status, dates, and location.
    - Implement backend logic to handle queries and dynamically filter tasks.
    - Test the filtering functionality under various scenarios to ensure accuracy.

#### 4. Kanban Board Development (5-7 days)
- **Objective:** Create an interactive Kanban board for task visualization and management.
  - **Kanban Board Interface:**
    - Develop the Kanban board interface, incorporating columns for different task statuses.
    - Integrate filtering options with the Kanban board to allow dynamic updates.
  - **UI/UX Refinement:**
    - Enhance the user interface for improved usability and aesthetics, using CSS for styling.
    - Test the Kanban board for responsiveness and usability across different devices.

#### 5. Testing and Refinement (4-6 days)
- **Objective:** Conduct comprehensive testing and refinement of the application.
  - **Bug Fixing:** Identify and resolve any issues or bugs uncovered during testing.
  - **Peer Review:** If possible, gather feedback from a peer or mentor to identify potential areas for improvement.
  - **Final Testing:** Perform end-to-end testing to ensure all features function correctly and the application is stable and reliable.

#### 6. Documentation and Submission (3-4 days)
- **Objective:** Finalize documentation and prepare for project submission.
  - **README and Documentation:** Write detailed documentation, including a comprehensive README file with setup instructions, features, and usage guidelines.
  - **Video Demo:** Record a video demonstration of the project's features and functionality as required.
  - **Final Review and Submission:** Conduct a final review of all project components and submit the project following the CS50 guidelines.

### Total Estimated Time: 23-33 days (3-4 weeks)

### Considerations Affecting the Timeline:
- **Time Allocation:** Progress will vary depending on the time available to dedicate to the project alongside other commitments.
- **Learning Curve:** New concepts in Flask, SQLAlchemy, or Kanban board implementation may require additional time for learning and experimentation.
- **Complexity and Scope Adjustments:** Unforeseen challenges, particularly in data migration or feature implementation, may extend the timeline.
- **Testing and Debugging:** The depth of testing and the number of bugs encountered may impact the overall schedule.

### Notes on the Timeline
This timeline is a provisional estimate designed to guide the development process. Given that this is a solo project being developed as a side project, the schedule is inherently flexible. Adjustments will be made based on the progress observed during each sprint, with a focus on delivering a functional and polished product.

---

This estimated timeline aligns with Agile development principles, providing a structured yet adaptable approach to managing the project schedule.
