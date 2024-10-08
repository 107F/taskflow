# Test Plan

## Purpose

The purpose of this document is to outline the testing strategy for Taskflow. It includes details on the types of tests conducted, including unit, integration, and end-to-end tests. This plan ensures that all aspects of the application are systematically tested to guarantee reliability and performance before deployment.

## Overview of Testing Strategy and Scope

The testing strategy encompasses three main levels of testing:
1. **Unit Testing**: Focuses on individual components or units of the application to verify that each part functions correctly in isolation.
2. **Integration Testing**: Ensures that different modules or services of the application interact correctly with each other.
3. **End-to-End Testing**: Simulates real-world scenarios to validate the application's functionality from start to finish, including the UI and backend services.

### Scope

The scope of this testing plan covers:
- Core functionalities such as task creation, modification, deletion, and Kanban board interactions.
- User authentication (registration, login, and logout).
- Data validation and error handling.
- Frontend interactivity (JavaScript functions and UI responsiveness).
- Backend logic and database operations.

## Test Cases

### Unit Tests

1. **Task Creation**
   - **Test Case ID**: TC-001
   - **Description**: Verify that a new task can be created with valid inputs.
   - **Steps**: 
     1. Call the task creation function with valid parameters.
     2. Check if the task is added to the database.
   - **Expected Result**: Task is successfully created and stored in the database.
   - **Pass/Fail Criteria**: Pass if task is present in the database with correct details.

2. **Task Modification**
   - **Test Case ID**: TC-002
   - **Description**: Verify that an existing task can be modified with valid inputs.
   - **Steps**:
     1. Select an existing task.
     2. Update task details using the modify function.
     3. Verify the changes in the database.
   - **Expected Result**: Task details are updated in the database.
   - **Pass/Fail Criteria**: Pass if the updated task details are correctly reflected in the database.

3. **User Registration**
   - **Test Case ID**: TC-003
   - **Description**: Ensure that a new user can register with a unique username and valid password.
   - **Steps**:
     1. Call the registration function with unique username and password.
     2. Verify the user is added to the database.
   - **Expected Result**: User is registered and stored in the database with hashed password.
   - **Pass/Fail Criteria**: Pass if the user is successfully added with hashed password.

### Integration Tests

1. **Task List Display**
   - **Test Case ID**: IT-001
   - **Description**: Verify that the task list displays all tasks from the database correctly.
   - **Steps**:
     1. Fetch tasks from the database.
     2. Render tasks in the UI.
   - **Expected Result**: All tasks are displayed in the UI.
   - **Pass/Fail Criteria**: Pass if all tasks are displayed correctly without any errors.

2. **User Login and Access Control**
   - **Test Case ID**: IT-002
   - **Description**: Ensure that the login system works correctly and controls access to authenticated routes.
   - **Steps**:
     1. Attempt to access a restricted route without logging in.
     2. Log in with valid credentials.
     3. Access the restricted route.
   - **Expected Result**: User is redirected to login page if not authenticated, and gains access after successful login.
   - **Pass/Fail Criteria**: Pass if access is correctly controlled based on authentication status.

3. **Task Update via Kanban Board**
   - **Test Case ID**: IT-003
   - **Description**: Verify that tasks can be updated via the drag-and-drop interface on the Kanban board.
   - **Steps**:
     1. Drag a task from one status column to another.
     2. Verify the task status is updated in the database.
   - **Expected Result**: Task status is updated correctly in the database.
   - **Pass/Fail Criteria**: Pass if task status changes reflect in the database.

### End-to-End Tests

1. **Full Task Lifecycle**
   - **Test Case ID**: E2E-001
   - **Description**: Test the complete lifecycle of a task from creation to deletion.
   - **Steps**:
     1. Create a new task.
     2. Modify the task details.
     3. Mark the task as complete.
     4. Delete the task.
   - **Expected Result**: Task is created, modified, completed, and deleted successfully.
   - **Pass/Fail Criteria**: Pass if all steps are executed without errors and database reflects the changes.

2. **User Workflow**
   - **Test Case ID**: E2E-002
   - **Description**: Validate a user's workflow including registration, login, task creation, and logout.
   - **Steps**:
     1. Register a new user.
     2. Log in with the new user credentials.
     3. Create a new task.
     4. Log out.
   - **Expected Result**: User is able to register, log in, create a task, and log out successfully.
   - **Pass/Fail Criteria**: Pass if user workflow is smooth and error-free.

## Testing Tools and Frameworks

- **Unit Testing**: PyTest for testing individual units of code (functions, methods).
- **Integration Testing**: Flask-Testing for testing interactions between components.
- **End-to-End Testing**: Selenium for simulating user interactions in a browser environment.
- **Database Testing**: SQLite in-memory database for isolated database tests.
- **Code Coverage**: Coverage.py to ensure that all critical code paths are tested.

## Criteria for Passing or Failing Tests

- A test **passes** if all assertions in the test case hold true and the application behaves as expected.
- A test **fails** if any assertion fails or an unexpected behavior occurs during test execution.
- **Unit Tests**: All critical functions must pass their respective unit tests.
- **Integration Tests**: Must pass to ensure smooth interaction between different components.
- **End-to-End Tests**: All essential user workflows should complete successfully without errors.

## Test Results and Identified Issues

After running all the planned tests, the following results were observed:

| Test Case ID | Description | Status | Issues |
|--------------|-------------|--------|--------|
| TC-001       | Task Creation | Pass | None |
| TC-002       | Task Modification | Pass | None |
| TC-003       | User Registration | Pass | None |
| IT-001       | Task List Display | Pass | None |
| IT-002       | User Login and Access Control | Pass | None |
| IT-003       | Task Update via Kanban Board | Pass | None |
| E2E-001      | Full Task Lifecycle | Pass | None |
| E2E-002      | User Workflow | Pass | None |

### Identified Issues

- **No issues identified during the testing phase**. All tests passed successfully, indicating that the application functions as expected across all tested scenarios.

## Conclusion

This test plan ensures comprehensive coverage of the Task Management System, from unit to end-to-end testing. By systematically verifying each component and interaction, we can confidently proceed with deployment, knowing that the application meets the expected reliability and performance standards.
