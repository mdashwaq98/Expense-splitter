# Branch Comparison & Testing Guide

## 📊 Overview

You have **TWO DIFFERENT APPLICATIONS** for the same expense splitter concept:

### 1. **Current Branch** (`cursor/merge-repo-and-python-app-branches-3ea4`)
- **Type**: Mobile App
- **Technology**: React Native + Expo
- **Platform**: iOS/Android mobile devices
- **Storage**: Local (AsyncStorage - device only)
- **Backend**: None (fully client-side)

### 2. **python-app Branch**
- **Type**: Web Application  
- **Technology**: Flask (Python) + Bootstrap
- **Platform**: Web browsers (desktop/mobile)
- **Storage**: Database (SQLite/MySQL)
- **Backend**: Full Flask server with API

---

## 🔍 Feature Comparison

| Feature | Mobile App (Current) | Web App (python-app) |
|---------|---------------------|----------------------|
| **User Authentication** | ✅ Local only | ✅ Database with sessions |
| **Expense Tracking** | ✅ Basic | ✅ Advanced with categories |
| **Group Management** | ✅ Basic | ✅ Full with permissions |
| **Balance Calculations** | ✅ Simple | ✅ Advanced with debt simplification |
| **Settlements** | ❌ Not implemented | ✅ Full settlement tracking |
| **Friends System** | ❌ Not implemented | ✅ Friend requests & management |
| **Personal Finance** | ❌ Not implemented | ✅ Income, personal expenses, debts |
| **Savings Goals** | ❌ Not implemented | ✅ Track savings with targets |
| **Multi-currency** | ❌ Not implemented | ✅ Per-group currencies |
| **Export Data** | ❌ Not implemented | ✅ CSV/Excel export |
| **Email Notifications** | ❌ Not implemented | ✅ Optional email features |
| **Theme Support** | ❌ Not implemented | ✅ Dark/Light modes |
| **Data Sync** | ❌ Device only | ✅ Cloud database |
| **Recurring Expenses** | ❌ Not implemented | ✅ Set up recurring bills |

---

## 🎯 Possible Adjustments & Integration Options

### Option 1: Keep Both Separate (Recommended)
**Best for**: Different use cases
- **Mobile App**: Quick personal tracking on-the-go
- **Web App**: Full-featured shared expense management

### Option 2: Connect Mobile App to Python Backend
**Effort**: High (3-5 days development)
- Modify React Native app to make API calls instead of local storage
- Create REST API endpoints in Flask backend
- Add JWT authentication
- Handle network states and offline mode

**Benefits**:
- Data syncs across devices
- Access from both mobile and web
- Shared features between platforms

**Files to Modify**:
```
Mobile App:
- src/context/AuthContext.js (API integration)
- src/context/ExpenseContext.js (API calls)
- Add axios/fetch for HTTP requests

Python Backend:
- Add REST API routes (JSON responses)
- Add CORS support
- Add JWT token authentication
```

### Option 3: Build React Native UI with Python Features
**Effort**: Medium (2-3 days)
- Port advanced features from Python to React Native
- Implement debt simplification algorithm
- Add settlements, friends system
- Keep local storage

### Option 4: Hybrid Approach
**Effort**: Medium
- Run Flask backend locally or on server
- Use React Native for mobile UI only
- Connect via API
- Best of both worlds

---

## 🧪 How to Test Both Apps

### Testing the Mobile App (Current Branch)

#### Prerequisites
```bash
# Check if Node.js is installed
node --version  # Should be 16+

# Check if npm is installed
npm --version
```

#### Step 1: Install Dependencies
```bash
cd /workspace
npm install
```

#### Step 2: Start the App
```bash
npm start
```

#### Step 3: Run on Device/Emulator
You'll see options:
- Press `a` for Android emulator
- Press `i` for iOS simulator (Mac only)
- Scan QR code with **Expo Go app** on your phone

#### Step 4: Test Features
1. **Sign Up**: Create a new account
2. **Add Expense**: Go to Expenses tab, click +
3. **Create Group**: Go to Groups tab, click +
4. **Check Profile**: View stats and balance
5. **Test Persistence**: Close and reopen app

### Testing the Python Web App

#### Prerequisites
```bash
# Check Python version
python3 --version  # Should be 3.8+
```

#### Step 1: Switch to python-app Branch
```bash
git checkout python-app
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Set Environment Variables
```bash
# Create .env file
cp .env.example .env 2>/dev/null || echo "SECRET_KEY=dev-secret-key-for-testing" > .env
```

#### Step 5: Initialize Database
```bash
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database created!")
EOF
```

#### Step 6: Run the App
```bash
python3 app.py
```

#### Step 7: Open in Browser
Visit: `http://localhost:5000`

#### Step 8: Test Features
1. **Sign Up**: Create account
2. **Create Group**: Add a new group
3. **Add Members**: Invite others by email
4. **Add Expense**: Create expenses and split
5. **View Balances**: Check who owes what
6. **Settle Up**: Record payments
7. **Try Friends**: Add friends for 1-on-1 expenses
8. **Personal Finance**: Track income/expenses
9. **Savings Goals**: Set financial targets
10. **Export Data**: Download expense reports

---

## 🚀 Recommended Approach

### For Personal Use
👉 **Use the Mobile App** - Simple, quick, works offline

### For Shared Expenses with Others
👉 **Use the Python Web App** - Full features, real-time sync, settlements

### For Best Experience
👉 **Connect them together** (Option 2 above)

---

## 🛠️ Quick Integration Example

If you want to connect the mobile app to Python backend:

### 1. Add API Routes to Flask (python-app)
```python
# In app.py, add API endpoints
@app.route('/api/expenses', methods=['GET'])
@login_required
def api_get_expenses():
    expenses = Expense.query.filter_by(paid_by=current_user.id).all()
    return jsonify([{
        'id': e.id,
        'description': e.description,
        'amount': e.amount,
        'date': e.date.isoformat()
    } for e in expenses])
```

### 2. Update React Native to Call API
```javascript
// In ExpenseContext.js
const API_URL = 'http://your-server:5000/api';

const fetchExpenses = async () => {
  const response = await fetch(`${API_URL}/expenses`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  const data = await response.json();
  setExpenses(data);
};
```

---

## 📝 Summary

**Current State**:
- ✅ Mobile app works - fully functional locally
- ✅ Python web app works - full-featured web application
- ❌ They are NOT connected

**To Connect Them**:
1. Add REST API to Flask backend
2. Update React Native to use fetch/axios
3. Implement JWT authentication
4. Handle offline/online states
5. Deploy Flask backend to a server

**Estimated Time**: 3-5 days for full integration

---

## 💡 My Recommendation

**Start by testing both separately**:
1. Test mobile app first (easier, faster)
2. Then test Python web app (more features)
3. Decide which features you need most
4. Then consider integration if needed

Both apps are production-ready in their current form - they just serve different purposes!
