# 🔧 Troubleshooting Guide
## Quick Fixes for Common Errors

---

## 🚨 Error: "Something went wrong" on website

### Cause:
The app crashed or there's a database issue.

### Fix:
1. Go to PythonAnywhere → **Web** tab
2. Scroll down to **"Log files"**
3. Click **"Error log"**
4. Copy the last error message
5. Try these fixes based on the error:

**If error says: `no such column: user_id` or similar database error:**
```bash
# In Bash console:
cd ~/spendings
rm -rf instance
```
Then go to Web tab → Click **"Reload"** button

**If error says: `No module named 'flask_login'`:**
```bash
# In Bash console:
pip install --user Flask-Login Flask-SQLAlchemy pandas openpyxl Werkzeug
```
Then go to Web tab → Click **"Reload"** button

---

## 🚨 Error: "502 Bad Gateway"

### Cause:
Your app failed to start.

### Fix:
1. Check the **Error log** (Web → Log files → Error log)
2. Most common causes:
   - **Wrong path in WSGI file** - Make sure you replaced `yourusername` with YOUR actual username
   - **Missing packages** - Run: `pip install --user -r requirements.txt` in Bash console
   - **Syntax error in code** - Check if you edited any files

---

## 🚨 Error: Can't Login / "Invalid credentials"

### Cause:
Database was created but default user wasn't added.

### Fix:
```bash
# In Bash console:
cd ~/spendings
rm -rf instance
```
Then go to Web tab → Click **"Reload"** button

The app will automatically create the default admin user when it starts.

---

## 🚨 Error: New users can't register

### Cause:
Database schema issue.

### Fix:
Same as above - delete database and reload:
```bash
cd ~/spendings
rm -rf instance
```
Then reload the web app.

---

## 🚨 Error: Files not found / 404 errors

### Cause:
Files not uploaded correctly or paths are wrong.

### Fix:
1. Go to **Files** tab
2. Navigate to `/home/yourusername/spendings/`
3. Make sure these exist:
   ```
   /home/yourusername/spendings/
   ├── app.py
   ├── requirements.txt
   ├── Master Sheet.xlsx
   ├── templates/
   │   ├── index.html
   │   └── login.html
   └── static/
       ├── style.css
       └── app.js
   ```
4. If anything is missing, upload it again

---

## 🚨 Error: ImportError / ModuleNotFoundError

### Cause:
Python packages not installed.

### Fix:
```bash
# In Bash console:
cd ~/spendings
pip install --user Flask==3.0.0 Flask-SQLAlchemy==3.1.1 Flask-Login==0.6.3 Werkzeug==3.0.1 pandas==2.1.4 openpyxl==3.1.2
```

Wait for installation to complete, then:
- Go to Web tab
- Click **"Reload"** button

---

## 🚨 Error: Static files not loading (no CSS/styling)

### Cause:
Static file paths incorrect.

### Fix:
1. Go to **Web** tab
2. Scroll to **"Static files"** section
3. Add mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/spendings/static/`
4. Click **"Reload"** button

---

## 🚨 App is slow or timing out

### Cause:
Free tier limitations or app needs optimization.

### Fix:
1. Check if you hit daily limit: Web tab → shows CPU usage
2. If over limit, wait for next day (resets at midnight UTC)
3. For better performance, consider upgrading PythonAnywhere account

---

## 🚨 Can't create folders on PythonAnywhere

### Solution 1: Using Files Tab
1. Click **"Files"** tab
2. Navigate to where you want the folder
3. Look for **"Directories"** section (yellow box)
4. Type folder name in the text box
5. Click **"New directory"** button

### Solution 2: Using Bash Console
1. Click **"Consoles"** tab
2. Click **"Bash"**
3. Type commands:
```bash
cd ~/spendings
mkdir templates
mkdir static
```

---

## 🚨 Can't upload files

### Cause:
File size limit or browser issue.

### Fix:
1. Make sure file is under 1GB
2. Try a different browser
3. Or use Bash console + wget:
```bash
cd ~/spendings
# Upload files using the Files tab interface instead
```

---

## 🚨 Data not saving / disappearing

### Cause:
Database not configured correctly.

### Fix:
1. Make sure `instance` folder is NOT in your `.gitignore`
2. Check if database file exists:
```bash
# In Bash console:
cd ~/spendings
ls -la instance/
```

Should show: `spendings.db`

If missing:
```bash
rm -rf instance
```
Then reload web app.

---

## 🚨 Error after editing code

### Cause:
Syntax error or breaking change.

### Fix:
1. Check **Error log** for specific error
2. Revert your changes:
   - Go to Files tab
   - Click on the file you edited
   - Copy backup code (from your local computer)
   - Paste it back
   - Save
3. Reload web app

---

## 🚨 "Permission denied" errors

### Cause:
Trying to write to wrong directory.

### Fix:
Make sure you're in your home directory:
```bash
cd ~
cd spendings
```

All your files should be in: `/home/yourusername/spendings/`

---

## 🚨 Want to start fresh / Reset everything

### Nuclear Option (erases all data):
```bash
# In Bash console:
cd ~
rm -rf spendings
```

Then:
1. Create `spendings` folder again
2. Upload all files
3. Install packages
4. Configure WSGI file
5. Reload web app

---

## 📝 How to Check Error Logs

**Always check error logs when something goes wrong:**

1. Go to PythonAnywhere dashboard
2. Click **"Web"** tab
3. Scroll down to **"Log files"** section
4. Click **"Error log"** link
5. Look at the LAST error (bottom of page)
6. Copy the full error message
7. Use fixes above based on the error

---

## ✅ Prevention Checklist

**To avoid errors in the first place:**

- [ ] Run `python test_before_deploy.py` before deploying
- [ ] Double-check all file uploads
- [ ] Replace `yourusername` in WSGI file with YOUR actual username
- [ ] Install ALL packages before reloading web app
- [ ] Test locally first (`http://localhost:5000`)
- [ ] Keep backups of your database file

---

## 🆘 Still Stuck?

If none of these fixes work:

1. Copy the full error from Error log
2. Note what you were trying to do
3. Note which step in deployment guide you're on
4. Ask for help with those 3 pieces of information

**Most errors are one of the above - follow the fixes carefully!**

---

## 🎯 Quick Commands Reference

```bash
# Navigate to project
cd ~/spendings

# Install packages
pip install --user -r requirements.txt

# Delete database (fixes most data errors)
rm -rf instance

# Check if files exist
ls -la

# Check Python version
python --version

# Test imports
python -c "import flask; import flask_login; print('OK')"
```

---

## 🔄 After Every Code Change

1. Edit file on PythonAnywhere (Files tab)
2. Click **"Save"**
3. Go to **Web** tab
4. Click **"Reload"** button (big green button)
5. Test your app
6. If error → Check Error log

---

**Remember: 99% of errors are fixed by:**
1. Checking the Error log
2. Deleting `instance` folder and reloading
3. Reinstalling packages
4. Double-checking file paths in WSGI file

**You got this!** 💪

