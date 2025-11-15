# ✅ Testing Your Spending Tracker

## 🔧 **App is Now Fixed!**

The database has been reset with the correct schema. New users can now register and login successfully!

---

## 🧪 **How to Test:**

### **Step 1: Open the App**
Go to: **http://localhost:5000**

### **Step 2: Test Default Login**
- Username: `admin`
- Password: `admin123`
- Click "Login"
- ✅ Should work!

### **Step 3: Test Registration (NEW USER)**
1. Click "Register here"
2. Enter:
   - Username: `testuser`
   - Password: `test123`
   - Email: (optional)
3. Click "Create Account"
4. ✅ Should automatically login!

### **Step 4: Test Adding Data**
1. After login, click "Income" tab
2. Click "+ Add Income"
3. Fill in:
   - Date: Today's date
   - Source: "Test Income"
   - Type: "Main"
   - Amount: 1000
4. Click "Add Income"
5. ✅ Should appear in the list!

### **Step 5: Test Logout and Re-login**
1. Click "Logout" button
2. Login again with `testuser` / `test123`
3. Go to "Income" tab
4. ✅ Should see your data!

---

## 🐛 **If Something Goes Wrong:**

### **"Can't login" or "Database error":**
1. Stop the app (Ctrl+C in terminal or close window)
2. Delete database:
   ```powershell
   Remove-Item -Recurse -Force instance
   ```
3. Restart app:
   ```powershell
   python app.py
   ```

### **"Module not found" error:**
```powershell
pip install Flask Flask-SQLAlchemy Flask-Login pandas openpyxl
```

### **"Port already in use":**
```powershell
taskkill /F /IM python.exe
python app.py
```

---

## ✅ **What Should Work Now:**

✅ **Default admin account** (admin/admin123)
✅ **Register new users**
✅ **Login with new users**
✅ **Add income/expenses**
✅ **Track debts**
✅ **Set savings goals**
✅ **Each user sees only their data**
✅ **Logout and re-login**
✅ **Data persists after restart**

---

## 📱 **Next: Deploy to PythonAnywhere**

Once local testing works:
1. Follow `CLOUD_DEPLOYMENT.md`
2. Upload all files to PythonAnywhere
3. Configure as described
4. Access from anywhere!

---

## 🔑 **Important Files:**

- **`instance/spendings.db`** - Your database (backup this!)
- **`LOGIN_INFO.txt`** - Default credentials
- **`app.py`** - Main application
- **`requirements.txt`** - Dependencies

---

## 💡 **Tips:**

1. **Change admin password** after first login
2. **Create your own account** instead of using admin
3. **Backup database file** regularly
4. **Test on phone** before deploying (http://192.168.2.99:5000)

---

**Everything should work now! Test it out!** 🎉

