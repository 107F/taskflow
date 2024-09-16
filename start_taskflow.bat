@echo off
REM Change to the directory of your Flask app
cd /d C:\Users\micro\Downloads\taskflow

REM Activate the virtual environment
C:\path\to\your\app\venv\Scripts\activate

REM Run Gunicorn
gunicorn --bind 127.0.0.1:8000 core.app:app
