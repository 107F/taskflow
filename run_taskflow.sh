#!/bin/bash
cd /mnt/c/Users/micro/Downloads/taskflow
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 core.app:app

