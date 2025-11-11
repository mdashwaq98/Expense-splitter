"""
WSGI entry point for PythonAnywhere deployment
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/expense-splitter-python'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DATABASE_URL'] = 'mysql://username:password@username.mysql.pythonanywhere-services.com/username$expensesplitter'
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'

# Import Flask app
from app import app as application

