# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.

import sys
import os

# 1. Add your project directory to the sys.path
# Replace 'yourusername' with your actual PythonAnywhere username
project_home = '/home/yourusername/book_exchange'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 2. Import your Flask app
# Our app is named 'app' in 'app.py'
from app import app as application

# Optional: set a custom secret key from environment or statically (if not already set in app.py)
# application.secret_key = 'anything_you_want'
