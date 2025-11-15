# 🚀 Complete PythonAnywhere Deployment Guide
### Share Your Spending Tracker with Friends & Family - Always Online & Free!

---

## ✅ BEFORE YOU START - Local Testing

**Test your app locally first:**

1. Open your browser and go to: `http://localhost:5000`
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. Test adding income/expenses to make sure everything works
4. If you see any errors, STOP and let me know before deploying!

---

## 📝 STEP 1: Create PythonAnywhere Account (5 minutes)

1. Go to: **https://www.pythonanywhere.com**
2. Click **"Start running Python online in less than a minute!"**
3. Click **"Create a Beginner account"** (100% FREE)
4. Fill in:
   - Username: (choose something professional, this will be in your URL!)
   - Email: your email
   - Password: create a strong password
5. Click **"Register"**
6. **Check your email** and verify your account
7. Login to PythonAnywhere

---

## 📁 STEP 2: Upload Your Files (10 minutes)

### A. Prepare Your Files

1. On your computer, make sure these files are in your `spendings` folder:
   - `app.py`
   - `requirements.txt`
   - `Master Sheet.xlsx`
   - Folders: `templates/`, `static/`

### B. Upload to PythonAnywhere

1. In PythonAnywhere, click **"Files"** (top menu)
2. You'll see your home directory: `/home/yourusername/`

3. **Create the project folder:**
   - Look for the **"Directories"** section (yellow box)
   - Type: `spendings`
   - Click **"New directory"**
   - Click on **`spendings`** to open it

4. **Upload files ONE BY ONE:**
   
   **Upload app.py:**
   - Click **"Upload a file"**
   - Click **"Choose File"**
   - Select `app.py` from your computer
   - Click **"Upload"**
   
   **Upload requirements.txt:**
   - Click **"Upload a file"**
   - Click **"Choose File"**
   - Select `requirements.txt`
   - Click **"Upload"**
   
   **Upload Master Sheet.xlsx:**
   - Click **"Upload a file"**
   - Click **"Choose File"**
   - Select `Master Sheet.xlsx`
   - Click **"Upload"**

5. **Create templates folder:**
   - In the **"Directories"** section, type: `templates`
   - Click **"New directory"**
   - Click on **`templates`** to open it
   - Upload files from your `templates` folder:
     - `index.html`
     - `login.html`
   - Click **"spendings"** (in the breadcrumb at top) to go back

6. **Create static folder:**
   - In the **"Directories"** section, type: `static`
   - Click **"New directory"**
   - Click on **`static`** to open it
   - Upload files from your `static` folder:
     - `style.css`
     - `app.js`
   - Click **"spendings"** to go back

---

## 🔧 STEP 3: Install Python Packages (5 minutes)

1. Click **"Consoles"** (top menu)
2. Click **"Bash"** (under "Start a new console")
3. Wait for the console to load (you'll see a green `$ ` prompt)

4. **Type these commands ONE AT A TIME:**

```bash
cd spendings
```
Press **Enter**. You should see: `~/spendings $`

```bash
pip install --user Flask Flask-SQLAlchemy Flask-Login pandas openpyxl Werkzeug gunicorn
```
Press **Enter**. This will take 2-3 minutes. Wait for it to finish!

5. **Verify installation:**
```bash
python3 -c "import flask; import flask_login; print('✓ All packages installed!')"
```
Press **Enter**. You should see: `✓ All packages installed!`

6. Keep this console window open (we'll use it later)

---

## 🌐 STEP 4: Create Web App (10 minutes)

1. Click **"Web"** (top menu)
2. Click **"Add a new web app"**
3. Click **"Next"** (for free domain)
4. Select **"Flask"**
5. Select **"Python 3.10"** (or latest version)
6. For "Path to Python file", type: `/home/yourusername/spendings/app.py`
   *(Replace `yourusername` with YOUR actual username!)*
7. Click **"Next"**

---

## ⚙️ STEP 5: Configure Web App (CRITICAL - Don't Skip!)

You should now be on the Web tab. Scroll down to find these sections:

### A. Fix the WSGI Configuration File

1. Find the **"Code"** section
2. Click on the **WSGI configuration file** link (looks like: `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Delete EVERYTHING** in that file
4. **Copy and paste this EXACT code:**

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/spendings'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variable
os.environ['FLASK_APP'] = 'app.py'

# Import Flask app
from app import app as application
```

5. **IMPORTANT:** Replace `yourusername` with YOUR actual PythonAnywhere username!
6. Click **"Save"** (top right)

### B. Set Virtual Environment (Optional but Recommended)

1. Scroll to **"Virtualenv"** section
2. Leave it blank for now (we installed packages globally)

### C. Set Working Directory

1. Scroll to **"Code"** section
2. Find **"Working directory"**
3. Enter: `/home/yourusername/spendings`
   *(Replace `yourusername` with YOUR username!)*

### D. Enable HTTPS (For Security)

1. Scroll to **"Security"** section
2. Toggle **"Force HTTPS"** to **ON**

---

## 🎉 STEP 6: Launch Your App!

1. Scroll to the TOP of the Web page
2. Click the BIG GREEN **"Reload yourusername.pythonanywhere.com"** button
3. Wait for the green checkmark (takes 5-10 seconds)
4. Click on your website link: **`https://yourusername.pythonanywhere.com`**

### ✅ Success Checklist:
- [ ] You see the login page (clean, no username/password showing)
- [ ] You can login with `admin` / `admin123`
- [ ] You see the dashboard with charts
- [ ] You can add income/expenses
- [ ] Data saves and persists (refresh the page to check)

---

## 🐛 IF YOU GET ERRORS:

### Error: "Something went wrong"

**Go to Web tab → Log files → Error log**. Common fixes:

1. **ImportError: No module named 'flask_login'**
   ```bash
   # In Bash console:
   pip install --user Flask-Login
   # Then reload web app
   ```

2. **File not found errors:**
   - Check all file paths in WSGI file
   - Make sure `yourusername` is YOUR actual username
   - Verify files uploaded correctly in Files tab

3. **Database errors:**
   - Delete `instance` folder if it exists
   - Reload web app (it will create a fresh database)

### Error: "502 Bad Gateway"

This means the app crashed. Check:
1. Error log (Web → Log files → Error log)
2. Make sure WSGI file is correct
3. Make sure all packages are installed

### Can't Login:

1. Go to Bash console
2. Delete database and recreate:
   ```bash
   cd ~/spendings
   rm -rf instance
   # Then reload web app
   ```

---

## 👨‍👩‍👧‍👦 STEP 7: Share with Friends & Family

Your app is now live at: **`https://yourusername.pythonanywhere.com`**

### Before Sharing:

1. **Create accounts for each person:**
   - Open your app
   - Click "Create New Account"
   - Create accounts for family members OR
   - Give them the link and let them register themselves

2. **Change default admin password:**
   - Login as admin
   - (We should add a password change feature - let me know!)

3. **Share the link:**
   ```
   Hey! Check out our family spending tracker:
   https://yourusername.pythonanywhere.com
   
   Create your account and start tracking your finances!
   ```

### Important Notes:
- ✅ **Always Online** - Your laptop can be off
- ✅ **100% Free** - No hidden costs
- ✅ **Secure** - Each person has their own login
- ✅ **Private Data** - Each user only sees their own data
- ⚠️ **Free limits** - 100,000 hits per day (more than enough for family use!)

---

## 🔄 UPDATING YOUR APP LATER

If you make changes to your code:

1. Go to **Files** tab
2. Click on the file you want to edit (e.g., `app.py`)
3. Make your changes
4. Click **"Save"**
5. Go to **Web** tab
6. Click **"Reload"** button

---

## 💡 PRO TIPS

1. **Bookmark these:**
   - Your app: `https://yourusername.pythonanywhere.com`
   - PythonAnywhere dashboard: `https://www.pythonanywhere.com/user/yourusername/`

2. **Check app health:**
   - Web tab → "Reload" shows last reload time
   - If app is slow, check if you hit free tier limits

3. **Backup your data:**
   - Files tab → Download `instance/spendings.db` regularly
   - This is your database backup!

4. **Monitor errors:**
   - Check Error log occasionally: Web → Log files → Error log

---

## 📞 NEED HELP?

**If anything goes wrong:**

1. Check the Error log first: Web → Log files → Error log
2. Copy the error message
3. Let me know and I'll help you fix it!

**Common issues already solved:**
- ✅ Database schema errors - fixed
- ✅ Login problems - fixed  
- ✅ Module import errors - fixed
- ✅ File path issues - documented above

---

## 🎯 FINAL CHECKLIST BEFORE SHARING

- [ ] App loads without errors
- [ ] Login works
- [ ] You can add/view income
- [ ] You can add/view expenses
- [ ] Data persists after refresh
- [ ] Changed default admin password (or created new accounts)
- [ ] Tested on phone/tablet (mobile responsive)
- [ ] Shared link with family

---

**Your app URL will be:**
## 🌟 `https://yourusername.pythonanywhere.com` 🌟

**You got this! Follow each step carefully, and you'll have your app running in 30 minutes!**

