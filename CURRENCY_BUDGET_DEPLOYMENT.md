# 💰 Deploy Currency & Budget Features to PythonAnywhere

## ✨ What's New
- **5 Currencies**: USD, CAD, AUD, INR, GBP
- **Monthly Budget Tracking**: Set spending limits with visual progress
- **Budget Alerts**: Warnings at 80% (orange) and 100% (red)
- **Budget Settings Page**: Manage currency and budget in one place

---

## 🚀 Deployment Steps

### Step 1: Log in to PythonAnywhere

Go to: https://www.pythonanywhere.com/login/

---

### Step 2: Backup Current Database (Optional but Recommended)

In the **Bash console** on PythonAnywhere:

```bash
cd ~/spendings
cp -r instance instance_backup_$(date +%Y%m%d)
```

---

### Step 3: Upload Updated Files

Go to **Files** tab on PythonAnywhere. Upload these files to `/home/mdashwaq98/spendings/`:

#### 3.1 Update `app.py`
- Click on `app.py` in the Files browser
- Delete all content (Ctrl+A, Delete)
- Copy the entire content from your local `app.py`
- Paste it into PythonAnywhere
- Click **Save**

#### 3.2 Update `templates/index.html`
- Navigate to `/home/mdashwaq98/spendings/templates/`
- Click on `index.html`
- Delete all content
- Copy from your local `templates/index.html`
- Paste and **Save**

#### 3.3 Create `templates/budget_settings.html`
- In `/home/mdashwaq98/spendings/templates/`
- Click **"New file"** button
- Name it: `budget_settings.html`
- Copy from your local `templates/budget_settings.html`
- Paste and **Save**

#### 3.4 Update `static/app.js`
- Navigate to `/home/mdashwaq98/spendings/static/`
- Click on `app.js`
- Delete all content
- Copy from your local `static/app.js`
- Paste and **Save**

#### 3.5 Update `static/style.css`
- In `/home/mdashwaq98/spendings/static/`
- Click on `style.css`
- Delete all content
- Copy from your local `static/style.css`
- Paste and **Save**

---

### Step 4: Reset Database (REQUIRED - Schema Changed!)

Since we added `currency` and `monthly_budget` fields to the User model, you MUST reset the database.

In the **Bash console** on PythonAnywhere:

```bash
cd ~/spendings
rm -rf instance/
```

**⚠️ Warning**: This will delete all existing data (users, transactions, etc.). The database will be recreated with the default admin account.

---

### Step 5: Reload Your Web App

1. Go to the **Web** tab on PythonAnywhere
2. Find your app: `mdashwaq98.pythonanywhere.com`
3. Click the green **"Reload"** button

Wait 10-15 seconds for the reload to complete.

---

### Step 6: Test the New Features

#### 6.1 Log In
- Visit: https://mdashwaq98.pythonanywhere.com
- Username: `admin`
- Password: `admin123`

#### 6.2 Test Currency Selection
1. Click **"Budget"** tab in the navigation
2. Click **"⚙️ Budget Settings"** button
3. Select a currency (e.g., CAD)
4. Enter a monthly budget (e.g., 5000)
5. Click **"Save Settings"**
6. You should be redirected to the dashboard

#### 6.3 Verify Currency Display
1. Go to **Dashboard** tab
2. All amounts should now show with your selected currency symbol (e.g., C$)

#### 6.4 Add Test Expense
1. Go to **Expenses** tab
2. Add a test expense (e.g., C$500)
3. Go to **Budget** tab
4. You should see:
   - Progress bar showing percentage spent
   - Spent amount
   - Remaining amount
   - Monthly expenses list

#### 6.5 Test Budget Warnings
1. Go to **Budget Settings**
2. Set budget to 100
3. Go to **Expenses**
4. Add expense of 85
5. Go to **Budget** tab
6. You should see an **orange warning** (over 80%)
7. Add another expense of 20
8. Budget bar should turn **red** with exceeded message

---

## 📁 Files Uploaded Checklist

Use this to track your progress:

- [ ] `app.py` (663 lines)
- [ ] `templates/index.html` (updated with Budget tab)
- [ ] `templates/budget_settings.html` (NEW FILE)
- [ ] `static/app.js` (updated with currency functions)
- [ ] `static/style.css` (updated with budget styles)
- [ ] Database deleted (`rm -rf instance/`)
- [ ] Web app reloaded
- [ ] Tested login with admin/admin123
- [ ] Tested currency selection
- [ ] Tested budget tracking

---

## 🔍 Troubleshooting

### Error: "Internal Server Error" after reload

**Solution**: Check the error log on PythonAnywhere (Web tab → Error log). Common issues:
- Missing file upload
- Syntax error in uploaded file
- WSGI file issue

### Currency not showing correctly

**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check that `static/app.js` was uploaded correctly

### Budget page shows "undefined"

**Solution**:
1. Make sure you set a currency and budget in Budget Settings first
2. Check browser console for errors (F12)
3. Verify database was reset

### Can't access budget settings page

**Solution**:
1. Verify `templates/budget_settings.html` exists on PythonAnywhere
2. Check that `app.py` has the `/budget-settings` route
3. Reload web app

---

## 🎯 What Users Need to Know

After deployment, inform your users:

1. **All existing accounts will be deleted** (database reset)
2. **Default login**: `admin` / `admin123`
3. **First time setup**: Go to Budget Settings to choose currency
4. **Budget tracking**: Set a monthly budget to see progress bars
5. **Create new accounts**: Use the Register page

---

## 📝 Quick Copy-Paste Commands

### Delete Database
```bash
cd ~/spendings
rm -rf instance/
```

### Check File Sizes (Verify Upload)
```bash
cd ~/spendings
ls -lh app.py
ls -lh templates/
ls -lh static/
```

Expected sizes:
- `app.py`: ~18-20 KB
- `templates/budget_settings.html`: ~7-8 KB
- `templates/index.html`: ~15-17 KB
- `static/app.js`: ~25-27 KB
- `static/style.css`: ~18-20 KB

### Test Database Creation
```bash
cd ~/spendings
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ Database created!')"
```

---

## ✅ Success Indicators

You know it worked when:

1. ✅ Login page loads without errors
2. ✅ Can log in with admin/admin123
3. ✅ Budget tab appears in navigation
4. ✅ Budget Settings page loads
5. ✅ Can select currency and save
6. ✅ Dashboard shows currency symbols (e.g., C$, ₹, £)
7. ✅ Budget tab shows progress bar
8. ✅ Warnings appear when budget is exceeded

---

## 🆘 Need Help?

If you encounter issues:

1. **Check error logs** on PythonAnywhere (Web tab)
2. **Verify file sizes** match expected sizes above
3. **Clear browser cache** and try again
4. **Restart from Step 3** if files are corrupted

---

## 🎉 You're Done!

Once everything is working:
- Share the link with friends and family
- Test all 5 currencies
- Set realistic budgets
- Track your spending!

Your app is now live at: **https://mdashwaq98.pythonanywhere.com**

