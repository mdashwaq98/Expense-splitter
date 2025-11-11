# PythonAnywhere Deployment Guide

Complete step-by-step guide to deploy the Expense Splitter app on PythonAnywhere.

## Prerequisites

- PythonAnywhere account (free tier works fine)
- Your application code ready

## Step-by-Step Deployment

### 1. Create PythonAnywhere Account

1. Visit [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Start running Python online in less than a minute!"
3. Choose "Create a Beginner account" (free)
4. Fill in username, email, and password
5. Verify your email

### 2. Upload Your Code

#### Option A: Using Git (Recommended)

1. Go to your PythonAnywhere Dashboard
2. Click on "Consoles" → "Bash"
3. In the bash console, run:

```bash
git clone https://github.com/yourusername/expense-splitter-python.git
cd expense-splitter-python
```

#### Option B: Using File Upload

1. Go to "Files" tab
2. Navigate to `/home/yourusername/`
3. Click "Upload a file"
4. Upload all your project files
5. Or upload a zip and extract it:

```bash
cd /home/yourusername
unzip expense-splitter-python.zip
cd expense-splitter-python
```

### 3. Create Virtual Environment

In the Bash console:

```bash
cd /home/yourusername/expense-splitter-python
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Wait for all packages to install (may take a few minutes).

### 4. Setup MySQL Database

1. Go to "Databases" tab in PythonAnywhere
2. Under "Create a database", enter a database name: `expensesplitter`
3. Click "Create"
4. Note down the database details shown:
   - Host: `yourusername.mysql.pythonanywhere-services.com`
   - Database name: `yourusername$expensesplitter`
   - Username: `yourusername`
   - Password: (the one you set)

### 5. Initialize Database Tables

In Bash console:

```bash
cd /home/yourusername/expense-splitter-python
source venv/bin/activate
python3
```

In Python shell:

```python
import os
os.environ['DATABASE_URL'] = 'mysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$expensesplitter'
os.environ['SECRET_KEY'] = 'temporary-key-for-setup'

from app import app, db
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
exit()
```

### 6. Configure Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Click "Next" for domain
4. Select "Manual configuration"
5. Choose "Python 3.10"
6. Click "Next"

### 7. Configure WSGI File

1. In the "Web" tab, find "Code" section
2. Click on the WSGI configuration file link (something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. Delete all the existing content
4. Replace with this (update YOUR details):

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/expense-splitter-python'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables - IMPORTANT: Change these!
os.environ['DATABASE_URL'] = 'mysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$expensesplitter'
os.environ['SECRET_KEY'] = 'your-super-secret-key-change-this-123456'  # Generate a random one!

# Import Flask app
from app import app as application
```

**IMPORTANT**: Replace:
- `yourusername` with your actual PythonAnywhere username
- `yourpassword` with your MySQL password
- `your-super-secret-key-change-this-123456` with a random secret key

To generate a secure secret key in Python:
```python
import secrets
print(secrets.token_hex(32))
```

5. Click "Save" button at the top

### 8. Configure Virtual Environment

1. In "Web" tab, scroll to "Virtualenv" section
2. Enter the path to your virtualenv:
```
/home/yourusername/expense-splitter-python/venv
```
3. Click the checkmark to save

### 9. Configure Static Files

1. In "Web" tab, scroll to "Static files" section
2. Click "Enter URL" and enter: `/static/`
3. Click "Enter path" and enter: `/home/yourusername/expense-splitter-python/static`
4. Click the checkmark

### 10. Set Working Directory (Optional but Recommended)

1. In "Web" tab, find "Code" section
2. Under "Working directory", enter:
```
/home/yourusername/expense-splitter-python
```

### 11. Reload Your Web App

1. Scroll to the top of the "Web" tab
2. Click the big green "Reload yourusername.pythonanywhere.com" button
3. Wait a few seconds

### 12. Test Your App

1. Click the link at the top of the Web tab: `yourusername.pythonanywhere.com`
2. You should see your Expense Splitter home page!
3. Try signing up for an account
4. Create a group
5. Add an expense

## Checking Error Logs

If something goes wrong:

1. Go to "Web" tab
2. Scroll down to "Log files"
3. Click on "Error log"
4. Look for error messages

Common errors and fixes:

### "ModuleNotFoundError"
- Check that virtual environment path is correct
- Make sure all packages are installed: `pip install -r requirements.txt`

### "OperationalError: (2003, Can't connect to MySQL server)"
- Check DATABASE_URL is correct
- Verify MySQL password is correct
- Make sure database exists

### "Internal Server Error"
- Check error log for details
- Verify WSGI file is configured correctly
- Check that app.py is in the right location

## Updating Your App

When you make changes to your code:

1. Upload new files via Files tab or use git pull
2. If you changed Python files:
   - Go to Web tab
   - Click "Reload"
3. If you only changed templates/static files:
   - May work without reload (try it first)
   - If not, do a reload

## Database Maintenance

### Backup Database

```bash
cd /home/yourusername/expense-splitter-python
mysqldump -h yourusername.mysql.pythonanywhere-services.com -u yourusername -p 'yourusername$expensesplitter' > backup.sql
```

### Reset Database

```bash
cd /home/yourusername/expense-splitter-python
source venv/bin/activate
python3
```

```python
import os
os.environ['DATABASE_URL'] = 'mysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$expensesplitter'
os.environ['SECRET_KEY'] = 'your-secret-key'

from app import app, db
with app.app_context():
    db.drop_all()  # Warning: Deletes all data!
    db.create_all()
exit()
```

## Custom Domain (Paid Feature)

If you want to use your own domain:

1. Upgrade to a paid PythonAnywhere account
2. Go to Web tab
3. Add your custom domain
4. Update DNS records at your domain registrar
5. Add CNAME record pointing to `yourusername.pythonanywhere.com`

## Performance Tips

1. **Free tier limitations**:
   - Your app sleeps after inactivity
   - Limited CPU time per day
   - One web app only

2. **Optimize for free tier**:
   - Use caching where possible
   - Minimize database queries
   - Keep your code efficient

3. **Upgrade when needed**:
   - More CPU time
   - Multiple web apps
   - No sleeping
   - More storage

## Security Checklist

- ✅ Changed SECRET_KEY from default
- ✅ Using strong MySQL password
- ✅ Not committing .env file to git
- ✅ HTTPS enabled (automatic on PythonAnywhere)
- ✅ CSRF protection enabled (Flask-WTF)
- ✅ Password hashing enabled (Flask-Bcrypt)

## Getting Help

- PythonAnywhere Help: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- Forums: [www.pythonanywhere.com/forums](https://www.pythonanywhere.com/forums)
- Contact support through "Send feedback" link

## Troubleshooting Common Issues

### App Not Loading

1. Check WSGI configuration
2. Verify paths are correct
3. Check error log
4. Make sure web app is not "disabled"

### Database Connection Failed

1. Verify MySQL service is running
2. Check credentials in WSGI file
3. Confirm database exists
4. Test connection in console:

```python
import os
os.environ['DATABASE_URL'] = 'your-database-url'
from app import app, db
with app.app_context():
    db.engine.connect()
```

### Static Files Not Loading

1. Check static files mapping
2. Verify file paths
3. Try hard reload in browser (Ctrl+Shift+R)
4. Check file permissions

### Template Not Found

1. Verify templates folder exists
2. Check template names in code match files
3. Ensure working directory is set correctly

## Next Steps

After successful deployment:

1. Share your app URL: `yourusername.pythonanywhere.com`
2. Monitor error logs regularly
3. Keep your code updated
4. Consider upgrading for better performance
5. Add analytics if needed
6. Set up regular backups

Congratulations! Your Expense Splitter app is now live on the internet! 🎉

