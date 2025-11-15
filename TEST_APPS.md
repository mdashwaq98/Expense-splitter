# Quick Testing Guide

## 🎯 Choose Your App to Test

### Option A: Test Mobile App (Current Branch - 5 minutes)

```bash
# 1. Install dependencies
npm install

# 2. Start the app
npm start

# 3. Follow the instructions:
#    - Press 'a' for Android
#    - Press 'i' for iOS
#    - Or scan QR code with Expo Go app

# 4. Test these features:
#    ✓ Sign up with name, email, password
#    ✓ Add an expense (Expenses tab)
#    ✓ Create a group (Groups tab)
#    ✓ View profile (Profile tab)
#    ✓ Close and reopen - data persists!
```

**Pros**: 
- ✅ Quick to test
- ✅ Works offline
- ✅ Mobile-optimized

**Cons**:
- ❌ Data only on your device
- ❌ Basic features only

---

### Option B: Test Python Web App (10 minutes)

```bash
# 1. Switch to python-app branch
git checkout python-app

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "SECRET_KEY=test-secret-key-123" > .env

# 5. Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database ready!')"

# 6. Run the app
python3 app.py

# 7. Open browser to: http://localhost:5000

# 8. Test these features:
#    ✓ Sign up and login
#    ✓ Create a group
#    ✓ Add expenses and split between people
#    ✓ View balances (who owes what)
#    ✓ Settle up and record payments
#    ✓ Add friends for 1-on-1 expenses
#    ✓ Track personal income/expenses
#    ✓ Set savings goals
#    ✓ Export to Excel
```

**Pros**:
- ✅ Full features
- ✅ Database storage
- ✅ Multiple users can share
- ✅ Advanced calculations

**Cons**:
- ❌ Needs server running
- ❌ Web-based (not native mobile)

---

## 🔄 Switching Between Apps

### Back to Mobile App
```bash
git checkout cursor/merge-repo-and-python-app-branches-3ea4
npm start
```

### Back to Python App
```bash
git checkout python-app
source venv/bin/activate
python3 app.py
```

---

## 🐛 Troubleshooting

### Mobile App Issues

**"npm: command not found"**
```bash
# Install Node.js first
# Visit: https://nodejs.org/
```

**"Expo app won't connect"**
```bash
# Clear cache and restart
npm start -- --clear
```

**"Module not found"**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Python App Issues

**"python3: command not found"**
```bash
# Install Python 3.8+
# Visit: https://www.python.org/downloads/
```

**"ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"Database errors"**
```bash
# Delete and recreate database
rm -f instance/expense_splitter.db expense_splitter.db
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**"Address already in use"**
```bash
# Port 5000 is busy, kill the process
lsof -ti:5000 | xargs kill -9
# Or run on different port
python3 app.py --port 5001
```

---

## ✅ Success Checklist

### Mobile App Working If:
- [ ] App opens in Expo Go or simulator
- [ ] Can create account
- [ ] Can add expenses
- [ ] Data persists after closing

### Python App Working If:
- [ ] Browser shows login page at localhost:5000
- [ ] Can create account
- [ ] Can create group and add expenses
- [ ] Can see balance calculations

---

## 📊 Feature Comparison Quick Reference

| What You Need | Use This |
|---------------|----------|
| Quick personal tracking | **Mobile App** |
| Share expenses with roommates | **Python App** |
| Works without internet | **Mobile App** |
| Track who owes what | **Python App** |
| Native mobile feel | **Mobile App** |
| Settlement tracking | **Python App** |
| Simple & fast | **Mobile App** |
| Full features | **Python App** |

---

## 🚀 Next Steps

1. **Test both apps** (20 minutes total)
2. **Decide which fits your needs**
3. **If you want BOTH**:
   - Keep them separate for different use cases, OR
   - Let me help you connect them together!

---

## 💬 Need Help?

If you encounter any issues or want to:
- Connect the mobile app to Python backend
- Add features from Python app to mobile
- Deploy either app to production
- Fix any bugs

Just let me know! 🙂
