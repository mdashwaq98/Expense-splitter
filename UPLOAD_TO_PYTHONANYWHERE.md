# 📤 Upload PWA Files to PythonAnywhere

## Quick Upload Guide

### **Files You Need to Upload:**

```
📁 spendings/
├── 📁 static/
│   ├── manifest.json          ← NEW (upload)
│   ├── service-worker.js      ← NEW (upload)
│   ├── pwa-install.js         ← NEW (upload)
│   ├── icon-192.png           ← NEW (upload)
│   ├── icon-512.png           ← NEW (upload)
│   ├── app.js                 ← Already uploaded
│   └── style.css              ← Already uploaded
│
├── 📁 templates/
│   ├── index.html             ← REPLACE (updated with PWA)
│   └── login.html             ← REPLACE (updated with PWA)
│
└── app.py                      ← REPLACE (uncommented for local use)
```

---

## 🚀 Step-by-Step Upload Process

### **Step 1: On PythonAnywhere**

1. Go to **Files** tab
2. Navigate to `/home/mdashwaq98/spendings/`

---

### **Step 2: Upload to `static/` folder**

1. Click into `static` folder
2. Click **"Upload a file"** button
3. Select and upload these 5 new files from your computer:
   - `manifest.json`
   - `service-worker.js`
   - `pwa-install.js`
   - `icon-192.png`
   - `icon-512.png`

**Location on your computer:**
```
C:\Users\mdash\Downloads\spendings\static\
```

---

### **Step 3: Replace `templates/` files**

1. Navigate back to `/home/mdashwaq98/spendings/`
2. Click into `templates` folder

#### **Replace index.html:**
3. Click the **trash icon** next to existing `index.html` → Delete it
4. Click **"Upload a file"**
5. Upload the NEW `index.html` from:
   ```
   C:\Users\mdash\Downloads\spendings\templates\index.html
   ```

#### **Replace login.html:**
6. Click the **trash icon** next to existing `login.html` → Delete it
7. Click **"Upload a file"**
8. Upload the NEW `login.html` from:
   ```
   C:\Users\mdash\Downloads\spendings\templates\login.html
   ```

---

### **Step 4: Update app.py (Important!)**

**⚠️ WAIT!** Before uploading `app.py`, you need to **comment out** the `if __name__ == '__main__':` block again for production!

**Open your local `app.py` and change the last lines to:**

```python
# For local development only - Comment out for production
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         # Create default user if none exists
#         if not User.query.first():
#             default_user = User(username='admin', email='admin@spendings.com')
#             default_user.set_password('admin123')  # CHANGE THIS PASSWORD!
#             db.session.add(default_user)
#             db.session.commit()
#             print("Default user created: username='admin', password='admin123'")
#     
#     # host='0.0.0.0' makes it accessible from other devices on your network
#     app.run(host='0.0.0.0', debug=True, port=5000)
```

**Then:**

1. Save the file
2. On PythonAnywhere, navigate to `/home/mdashwaq98/spendings/`
3. Click on `app.py` to edit it
4. **Select ALL** (`Ctrl+A`), delete it
5. Copy your ENTIRE local `app.py` file
6. Paste it into PythonAnywhere's editor
7. Click **"Save"**

---

### **Step 5: Reload Your Web App**

1. Go to **Web** tab
2. Click the big green **"Reload mdashwaq98.pythonanywhere.com"** button
3. Wait for the checkmark (✅)

---

### **Step 6: Test Your PWA!**

#### **On Desktop:**
1. Visit: `https://mdashwaq98.pythonanywhere.com`
2. Look for the **"📱 Install App"** button in the navbar
3. Login with `admin` / `admin123`
4. Click "📱 Install App"
5. Confirm installation
6. App should open in its own window!

#### **On Your Phone:**

**Android:**
1. Open Chrome
2. Visit: `https://mdashwaq98.pythonanywhere.com`
3. Look for "📱 Install App" button OR tap menu (⋮) → "Add to Home screen"
4. Tap "Install"
5. Check your home screen - app icon should appear!

**iPhone:**
1. Open Safari
2. Visit: `https://mdashwaq98.pythonanywhere.com`
3. Tap the **Share** button (square with arrow up)
4. Scroll down, tap **"Add to Home Screen"**
5. Tap **"Add"**
6. Check your home screen - app icon should appear!

---

## ✅ Checklist

- [ ] Uploaded `manifest.json` to `static/`
- [ ] Uploaded `service-worker.js` to `static/`
- [ ] Uploaded `pwa-install.js` to `static/`
- [ ] Uploaded `icon-192.png` to `static/`
- [ ] Uploaded `icon-512.png` to `static/`
- [ ] Replaced `index.html` in `templates/`
- [ ] Replaced `login.html` in `templates/`
- [ ] Updated `app.py` (commented out `if __name__`)
- [ ] Reloaded web app
- [ ] Tested on desktop - "📱 Install App" button appears
- [ ] Tested installation - app opens in standalone mode
- [ ] Tested on phone - can install as app
- [ ] App icon appears correctly

---

## 🐛 Troubleshooting

### **"Install App" button doesn't show:**
- Check browser console (F12) for errors
- Make sure all 5 files are uploaded to `static/` folder
- Try hard refresh: `Ctrl+Shift+R`
- Check manifest.json is accessible: visit `https://mdashwaq98.pythonanywhere.com/static/manifest.json`

### **Service Worker error:**
- Make sure `service-worker.js` is in `static/` folder
- Check error log on PythonAnywhere
- Clear browser cache and try again

### **Icons not showing:**
- Make sure both `.png` files are uploaded
- Check they're in the `static/` folder
- Verify file names are exactly: `icon-192.png` and `icon-512.png`

---

## 🎉 After Installation

Once everything works:

1. **Share with friends & family!**
2. **Create a short URL** (optional):
   - Go to: https://bitly.com or https://tinyurl.com
   - Shorten: `mdashwaq98.pythonanywhere.com`
   - Get something like: `bit.ly/myspendingtracker`

3. **Send installation instructions:**
   ```
   📱 My Spending Tracker App is ready!
   
   🌐 Visit: [your short URL]
   
   📲 Install as an app:
   - Android: Click "Install App" or Add to Home screen
   - iPhone: Safari → Share → Add to Home Screen
   
   Login: admin / admin123
   ```

---

**Need help?** Let me know what error you're seeing! 🚀

