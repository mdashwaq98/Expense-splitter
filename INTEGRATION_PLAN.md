# Integration Plan: Connecting Mobile App to Python Backend

## 🎯 Goal
Connect the React Native mobile app to the Flask Python backend so users can:
- Access data from any device
- Share expenses with other users in real-time
- Use advanced features from Python backend
- Keep the beautiful mobile UI

---

## 📋 Current Architecture

### Mobile App (React Native)
```
User Interface (React Native)
        ↓
Local State (Context API)
        ↓
AsyncStorage (Device)
```

### Python Backend (Flask)
```
Web Templates (HTML/Jinja2)
        ↓
Flask Routes
        ↓
SQLAlchemy ORM
        ↓
Database (SQLite/MySQL)
```

---

## 🔄 Target Architecture

```
Mobile App (React Native) ←→ REST API ←→ Flask Backend ←→ Database
                                ↓
                          Web App (Browser)
```

Both mobile and web would share the same backend!

---

## 🛠️ Implementation Steps

### Phase 1: Prepare Python Backend for API (2-3 hours)

#### 1.1 Add CORS Support
```python
# In requirements.txt, add:
Flask-CORS==4.0.0

# In app.py, add:
from flask_cors import CORS
CORS(app)
```

#### 1.2 Create API Blueprint
```python
# New file: api/routes.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/expenses', methods=['GET'])
@login_required
def get_expenses():
    expenses = Expense.query.filter_by(paid_by=current_user.id).all()
    return jsonify([{
        'id': e.id,
        'description': e.description,
        'amount': float(e.amount),
        'date': e.date.isoformat(),
        'category': e.category
    } for e in expenses])

@api.route('/expenses', methods=['POST'])
@login_required
def add_expense():
    data = request.json
    expense = Expense(
        description=data['description'],
        amount=data['amount'],
        paid_by=current_user.id,
        group_id=data.get('group_id')
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({'id': expense.id, 'success': True})

# Add more endpoints for groups, profile, etc.
```

#### 1.3 Add JWT Authentication
```python
# In requirements.txt, add:
PyJWT==2.8.0

# Create token generation
import jwt
from datetime import datetime, timedelta

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@api.route('/auth/login', methods=['POST'])
def api_login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        token = generate_token(user.id)
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        })
    return jsonify({'error': 'Invalid credentials'}), 401
```

### Phase 2: Update Mobile App for API (3-4 hours)

#### 2.1 Install HTTP Client
```bash
npm install axios
```

#### 2.2 Create API Service
```javascript
// New file: src/services/api.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://localhost:5000/api';  // Change for production

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  signup: async (name, email, password) => {
    const response = await api.post('/auth/signup', { name, email, password });
    return response.data;
  },
};

export const expensesAPI = {
  getAll: async () => {
    const response = await api.get('/expenses');
    return response.data;
  },
  create: async (expense) => {
    const response = await api.post('/expenses', expense);
    return response.data;
  },
  delete: async (id) => {
    await api.delete(`/expenses/${id}`);
  },
};

export const groupsAPI = {
  getAll: async () => {
    const response = await api.get('/groups');
    return response.data;
  },
  create: async (group) => {
    const response = await api.post('/groups', group);
    return response.data;
  },
};

export default api;
```

#### 2.3 Update AuthContext
```javascript
// In src/context/AuthContext.js
import { authAPI } from '../services/api';

const login = async (email, password) => {
  try {
    const data = await authAPI.login(email, password);
    await AsyncStorage.setItem('authToken', data.token);
    await AsyncStorage.setItem('currentUser', JSON.stringify(data.user));
    setUser(data.user);
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Login failed');
  }
};
```

#### 2.4 Update ExpenseContext
```javascript
// In src/context/ExpenseContext.js
import { expensesAPI, groupsAPI } from '../services/api';

const fetchExpenses = async () => {
  try {
    const data = await expensesAPI.getAll();
    setExpenses(data);
  } catch (error) {
    console.error('Failed to fetch expenses:', error);
  }
};

const addExpense = async (description, amount, groupId) => {
  try {
    const newExpense = await expensesAPI.create({
      description,
      amount,
      group_id: groupId
    });
    setExpenses([...expenses, newExpense]);
  } catch (error) {
    throw new Error('Failed to add expense');
  }
};
```

#### 2.5 Add Offline Support (Optional)
```javascript
// New file: src/services/offline.js
import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

const PENDING_ACTIONS_KEY = 'pendingActions';

export const queueAction = async (action) => {
  const pending = await AsyncStorage.getItem(PENDING_ACTIONS_KEY);
  const actions = pending ? JSON.parse(pending) : [];
  actions.push({ ...action, timestamp: Date.now() });
  await AsyncStorage.setItem(PENDING_ACTIONS_KEY, JSON.stringify(actions));
};

export const syncPendingActions = async () => {
  const state = await NetInfo.fetch();
  if (!state.isConnected) return;
  
  const pending = await AsyncStorage.getItem(PENDING_ACTIONS_KEY);
  if (!pending) return;
  
  const actions = JSON.parse(pending);
  // Process each action...
  await AsyncStorage.removeItem(PENDING_ACTIONS_KEY);
};
```

### Phase 3: Testing (1-2 hours)

#### 3.1 Test Locally
```bash
# Terminal 1: Start Python backend
cd /workspace
git checkout python-app
source venv/bin/activate
python3 app.py

# Terminal 2: Start mobile app
git checkout cursor/merge-repo-and-python-app-branches-3ea4
npm start
```

#### 3.2 Test Scenarios
- [ ] Sign up creates user in database
- [ ] Login returns valid token
- [ ] Create expense syncs to database
- [ ] Create group syncs to database
- [ ] Data persists across app restarts
- [ ] Multiple devices see same data
- [ ] Handle network errors gracefully

### Phase 4: Deployment (2-3 hours)

#### 4.1 Deploy Backend
```bash
# Option A: PythonAnywhere (Free)
# Follow: python-app branch README

# Option B: Heroku
heroku create expense-splitter-api
git push heroku python-app:main

# Option C: AWS/DigitalOcean
# Deploy Flask with gunicorn
```

#### 4.2 Update Mobile App Config
```javascript
// src/config.js
export const API_URL = __DEV__ 
  ? 'http://localhost:5000/api'
  : 'https://your-api-domain.com/api';
```

#### 4.3 Build Mobile App
```bash
# For production build
eas build --platform android
eas build --platform ios
```

---

## 📊 Estimated Timeline

| Phase | Time | Difficulty |
|-------|------|-----------|
| Phase 1: Backend API | 2-3 hours | Medium |
| Phase 2: Mobile Updates | 3-4 hours | Medium |
| Phase 3: Testing | 1-2 hours | Easy |
| Phase 4: Deployment | 2-3 hours | Medium |
| **Total** | **8-12 hours** | **Medium** |

---

## 🎯 Alternative: Simpler Approaches

### Option A: Use Python Backend As-Is
- Keep the web app for desktop
- Keep mobile app for mobile
- They work independently
- **Time: 0 hours** ✅

### Option B: Add Key Features to Mobile
- Port debt simplification algorithm
- Add settlement tracking
- Keep everything local
- **Time: 4-6 hours**

### Option C: Create Sync Button
- Add "Sync to Cloud" feature
- Upload local data to backend when user clicks
- Simple one-way sync
- **Time: 2-3 hours**

---

## 💰 Cost Considerations

| Service | Free Tier | Paid |
|---------|-----------|------|
| PythonAnywhere | ✅ 1 web app | $5/month |
| Heroku | ❌ No longer free | $7/month |
| Vercel | ✅ Hobby projects | $20/month |
| Railway | ✅ $5 credit | Pay as you go |
| AWS EC2 | ✅ 1 year | Varies |

---

## 🔒 Security Checklist

Before going live:
- [ ] Use HTTPS for API
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Enable CSRF protection
- [ ] Add request logging
- [ ] Implement proper error handling
- [ ] Add API versioning (/api/v1/)
- [ ] Set up monitoring

---

## 📝 Decision Matrix

| Factor | Keep Separate | Connect Them |
|--------|--------------|--------------|
| Development Time | 0 hours | 8-12 hours |
| Complexity | Low | Medium |
| Data Sync | No | Yes |
| Server Required | No | Yes |
| Monthly Cost | $0 | $5-20 |
| Multiple Devices | No | Yes |
| Team Collaboration | No | Yes |
| Offline Mode | Full | Partial |
| Maintenance | Easy | Medium |

---

## 🚀 My Recommendation

**For Personal Use**: Keep them separate
- Mobile app for quick tracking
- Web app when you need advanced features

**For Team/Sharing**: Connect them
- Worth the 8-12 hours investment
- Much better user experience
- Enables collaboration

**Quick Win**: Start with Option C (Sync Button)
- 2-3 hours only
- Best of both worlds
- Can expand later

---

## 📞 Next Steps

Want me to:
1. ✅ Implement the full integration?
2. ✅ Add just the sync button?
3. ✅ Port specific features to mobile?
4. ✅ Help deploy the backend?
5. ✅ Something else?

Just let me know what works best for you! 🙂
