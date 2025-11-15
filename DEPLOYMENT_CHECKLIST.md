# ✅ Deployment Checklist - Print This!

## 📋 Before You Start

- [ ] Test app locally at `http://localhost:5000`
- [ ] Login works (admin/admin123)
- [ ] Can add income/expenses
- [ ] Run: `python test_before_deploy.py` (all checks pass ✅)

---

## 🌐 PythonAnywhere Setup (30 minutes)

### Account Creation (5 min)
- [ ] Go to pythonanywhere.com
- [ ] Create FREE Beginner account
- [ ] Verify email
- [ ] Login to dashboard

### Upload Files (10 min)
- [ ] Files tab → Create `spendings` folder
- [ ] Upload: `app.py`
- [ ] Upload: `requirements.txt`
- [ ] Upload: `Master Sheet.xlsx`
- [ ] Create folder: `templates`
- [ ] Upload to templates: `index.html`, `login.html`
- [ ] Create folder: `static`
- [ ] Upload to static: `style.css`, `app.js`

### Install Packages (5 min)
- [ ] Consoles tab → Start Bash console
- [ ] Run: `cd spendings`
- [ ] Run: `pip install --user Flask Flask-SQLAlchemy Flask-Login pandas openpyxl Werkzeug`
- [ ] Wait for installation (2-3 minutes)
- [ ] Verify: `python3 -c "import flask; import flask_login; print('OK')"`

### Create Web App (10 min)
- [ ] Web tab → Add new web app
- [ ] Select Flask
- [ ] Select Python 3.10
- [ ] Path: `/home/YOURUSERNAME/spendings/app.py`

### Configure WSGI File (CRITICAL!)
- [ ] Click WSGI configuration file link
- [ ] Delete everything
- [ ] Paste new code (from guide)
- [ ] Change `yourusername` to YOUR username (3 places!)
- [ ] Save file

### Final Settings
- [ ] Set working directory: `/home/YOURUSERNAME/spendings`
- [ ] Enable Force HTTPS: ON
- [ ] Click big green RELOAD button

---

## 🧪 Testing (5 min)

- [ ] Click your app URL: `yourusername.pythonanywhere.com`
- [ ] Login page loads (clean, no errors)
- [ ] Login with: admin / admin123
- [ ] Dashboard shows charts
- [ ] Add test income
- [ ] Add test expense
- [ ] Refresh page - data still there ✅

---

## 👨‍👩‍👧‍👦 Before Sharing

- [ ] Create test account (not admin)
- [ ] Test login with new account
- [ ] Verify each user sees only their data
- [ ] Test on mobile phone
- [ ] Bookmark your app URL

---

## 📢 Share With Family

**Your app URL:**
```
https://YOURUSERNAME.pythonanywhere.com
```

**Share message:**
```
Hey! I created a spending tracker for us:
https://YOURUSERNAME.pythonanywhere.com

Create your account and start tracking expenses!
Each person's data is private and secure.
```

---

## 🆘 If Something Goes Wrong

1. **Check Error Log:**
   - Web tab → Log files → Error log

2. **Most common fixes:**
   ```bash
   # Delete database (fixes 90% of issues):
   cd ~/spendings
   rm -rf instance
   # Then: Web tab → Reload button
   ```

3. **Need help?**
   - Copy error from Error log
   - Check TROUBLESHOOTING.md
   - Ask with specific error message

---

## 🎯 Success Criteria

✅ App loads without errors
✅ Multiple users can register
✅ Each user has private data
✅ Data persists across logins
✅ Works on mobile
✅ Family can access it

---

## 📱 After Deployment

**Monitor your app:**
- Check occasionally: Web tab → Error log
- Backup database: Download `instance/spendings.db`
- Share feedback with family

**App limits (free tier):**
- ✅ 100,000 hits per day (more than enough!)
- ✅ Always online (24/7)
- ✅ No credit card required

---

## 🔄 Need to Update?

1. Files tab → Edit file
2. Save
3. Web tab → Reload
4. Test
5. Done!

---

**Print this checklist and check off items as you go!**

**Estimated time: 30 minutes** ⏱️

**Difficulty: Easy** (just follow the steps!)

**Required:** Nothing but this guide!

---

## 📚 Reference Documents

- **Main Guide:** `PYTHONANYWHERE_STEP_BY_STEP.md`
- **If errors:** `TROUBLESHOOTING.md`
- **Default login:** admin / admin123

---

**You're ready! Let's deploy! 🚀**

