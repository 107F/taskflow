# Deployment Guide

## Purpose

This Deployment Guide provides a detailed, step-by-step process to deploy the **Task Management System** to a production environment on a local machine. It is tailored for developers and IT professionals transitioning the application from development to production. By following this guide, you ensure an efficient deployment that aligns with industry best practices and Agile principles.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
   - [Software Requirements](#software-requirements)
   - [Environment Setup](#environment-setup)
2. [Deployment Instructions](#deployment-instructions)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Set Up a Virtual Environment](#step-2-set-up-a-virtual-environment)
   - [Step 3: Install Dependencies](#step-3-install-dependencies)
   - [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
   - [Step 5: Update Database Path](#step-5-update-database-path)
   - [Step 6: Launch the Application with Gunicorn](#step-6-launch-the-application-with-gunicorn)
   - [Step 7: Configure Nginx for Reverse Proxy](#step-7-configure-nginx-for-reverse-proxy)
   - [Step 8: Create a Shell Script for Fast Launch](#step-8-create-a-shell-script-for-fast-launch)
3. [Production Configuration Details](#production-configuration-details)
   - [Database Setup](#database-setup)
   - [Environment Variables](#environment-variables)
   - [Logging Configuration](#logging-configuration)
   - [Security Considerations](#security-considerations)
4. [Post-Deployment Testing and Verification](#post-deployment-testing-and-verification)
   - [Functional Testing](#functional-testing)
   - [Database Verification](#database-verification)
   - [Performance Testing](#performance-testing)
   - [Security Testing](#security-testing)
5. [Conclusion](#conclusion)

---

## Prerequisites

### Software Requirements

Ensure the following software is installed on the local machine:

1. **Python 3.10 or higher**: Required for running the Flask application.
2. **pip (Python Package Installer)**: Used for installing dependencies.
3. **Git**: Necessary for cloning the project repository.
4. **SQLite**: Acts as the database engine for the application.
5. **Virtual Environment Tool**: Python’s `venv` module will be used to create an isolated environment.
6. **Gunicorn**: Installed globally to serve the application in production.
7. **Nginx**: Installed to act as a reverse proxy server for Gunicorn.

### Environment Setup

- **Operating System**: Deployment is performed on WSL (Windows Subsystem for Linux) running Ubuntu.
- **User Permissions**: Administrator privileges to install and configure required software.
- **Network Access**: Required for downloading dependencies and setting up the server.

---

## Deployment Instructions

### Step 1: Clone the Repository

- Open the WSL terminal and navigate to the desired directory where the project will be stored.
- Use Git to clone the repository from the provided GitHub URL.
- Change to the newly created project directory.

### Step 2: Set Up a Virtual Environment

- Create a virtual environment using Python’s `venv` module within the project directory.
- Activate the virtual environment to isolate the project's dependencies.

### Step 3: Install Dependencies

- With the virtual environment activated, install the required packages from the `requirements.txt` file.
- Verify that all necessary dependencies are installed correctly.

### Step 4: Configure Environment Variables

- Create a `.env` file in the project's root directory to securely store environment variables.
- Set the necessary environment variables, including `FLASK_ENV`, `SECRET_KEY`, and `DATABASE_URL`.
- Ensure the `.env` file is secured and not included in version control by adding it to `.gitignore`.

### Step 5: Update Database Path

- Update the `DATABASE_URL` in the `.env` file to use an absolute path for the SQLite database.
- Verify that the application references the correct location of the `taskflow.db` file.

### Step 6: Launch the Application with Gunicorn

- Activate the virtual environment.
- Use Gunicorn to serve the Flask application, binding it to the desired IP and port.
- Verify that the application is running by accessing the specified URL in a web browser.

### Step 7: Configure Nginx for Reverse Proxy

- Install Nginx on WSL to act as a reverse proxy for the application.
- Edit the Nginx configuration file to forward requests to Gunicorn and serve static files.
- Restart Nginx to apply the configuration and verify that it is correctly forwarding requests.

### Step 8: Create a Shell Script for Fast Launch

- Create a shell script in the project directory to automate the startup process.
- The script should activate the virtual environment, launch Gunicorn, and handle any necessary setup.
- Mark the script as executable and test it to ensure it runs the application without requiring manual input.
- For convenience, create a desktop shortcut to this script, allowing for a quick launch of the application on system startup.

---

## Production Configuration Details

### Database Setup

- **Engine**: SQLite is used for local production.
- **File Location**: `taskflow.db` is located in the `core` directory with an absolute path specified.
- **Backup**: Implement a manual backup strategy for `taskflow.db`.

### Environment Variables

- **FLASK_ENV**: Set to `production` to disable debugging and enable production settings.
- **SECRET_KEY**: A securely generated key for session management.
- **DATABASE_URL**: Points to the absolute path of the local SQLite database file.

### Logging Configuration

- **Log File**: Application logs are stored in `core/app.log`.
- **Logging Level**: Configured to capture errors and warnings.

### Security Considerations

- **Session Security**: Ensure `SECRET_KEY` is kept secure.
- **Input Validation**: Validate all user inputs to prevent security vulnerabilities.
- **Access Control**: Verify that sensitive routes are protected and require authentication.

---

## Post-Deployment Testing and Verification

### Functional Testing

- Test user registration, login, and session management to ensure secure access control.
- Verify task creation, modification, deletion, and Kanban board functionality.
- Test data filtering and search features for accuracy.

### Database Verification

- Inspect `taskflow.db` using SQLite commands to verify data integrity.
- Confirm that CRUD operations reflect correctly in the database.

### Performance Testing

- Perform load testing to evaluate application response times and stability under concurrent access.
- Monitor system resource utilization to ensure optimal performance.

### Security Testing

- Test input validation for security robustness against SQL injection and XSS attacks.
- Verify session management and access control to ensure security compliance.

---

## Conclusion

This Deployment Guide provides a detailed and structured approach to deploying the Task Management System to a local production environment. It covers setting up the environment, configuring necessary services like Gunicorn and Nginx, and includes creating a shell script for faster application startup. Following this guide ensures a secure and efficient deployment process, aligned with industry best practices.

---

**Document Version**: 1.4

**Last Updated**: 17/09/2024
