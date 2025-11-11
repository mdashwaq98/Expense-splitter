# Expense Splitter - Python Web Application

A full-featured expense splitting web application built with Flask. Split bills with friends, family, and roommates. Track who owes what and settle up easily.

## Features

- 👥 **User Authentication** - Sign up, login, and manage your account
- 🎯 **Group Management** - Create groups for trips, households, or any shared expenses
- 💰 **Expense Tracking** - Add expenses with custom categories and split methods
- 📊 **Balance Calculation** - Automatically calculate who owes what
- 🔄 **Debt Simplification** - Minimize the number of transactions needed to settle
- 💳 **Settlement Tracking** - Record payments and track settlement history
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / MySQL (production)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Forms**: Flask-WTF
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy

## Installation

### Local Development

1. **Clone or download this folder**

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` and set your SECRET_KEY

6. **Run the application**
```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Deploying to PythonAnywhere

### Step 1: Create a PythonAnywhere Account

1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account
3. Verify your email address

### Step 2: Upload Your Code

1. Open a Bash console from your PythonAnywhere dashboard
2. Clone or upload your code:
```bash
git clone <your-repo-url> expense-splitter-python
# OR upload via Files tab
```

### Step 3: Create Virtual Environment

```bash
cd expense-splitter-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Setup MySQL Database

1. Go to **Databases** tab in PythonAnywhere
2. Create a new MySQL database
3. Note down your database credentials

### Step 5: Configure WSGI File

1. Go to **Web** tab
2. Click "Add a new web app"
3. Choose "Manual configuration" and Python 3.10
4. Edit the WSGI configuration file
5. Replace contents with your `wsgi.py` file
6. Update the following in wsgi.py:
   - Replace `yourusername` with your PythonAnywhere username
   - Update `DATABASE_URL` with your MySQL credentials
   - Set a secure `SECRET_KEY`

Example:
```python
# Add your project directory to the sys.path
project_home = '/home/yourusername/expense-splitter-python'

# Set environment variables
os.environ['DATABASE_URL'] = 'mysql://yourusername:dbpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$expensesplitter'
os.environ['SECRET_KEY'] = 'generate-a-random-secret-key-here'
```

### Step 6: Configure Virtual Environment

1. In the **Web** tab, find "Virtualenv" section
2. Enter: `/home/yourusername/expense-splitter-python/venv`

### Step 7: Configure Static Files

In the **Web** tab, add static files mapping:

- URL: `/static/`
- Directory: `/home/yourusername/expense-splitter-python/static`

### Step 8: Initialize Database

1. Open a Bash console
2. Run:
```bash
cd expense-splitter-python
source venv/bin/activate
python
```

In Python shell:
```python
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

### Step 9: Reload Web App

1. Go to **Web** tab
2. Click the green "Reload" button
3. Visit your site at `yourusername.pythonanywhere.com`

## Usage

### Creating an Account

1. Click "Get Started" or "Sign Up"
2. Enter your name, email, and password
3. Click "Sign Up"

### Creating a Group

1. From dashboard, click "Create Group"
2. Enter group name, description, and currency
3. Click "Create Group"

### Adding Members

1. Open a group
2. In the Members section, enter member's email
3. Click "Add" (member must have an account)

### Adding Expenses

1. Open a group
2. Click "Add Expense"
3. Fill in expense details:
   - Description
   - Amount
   - Category
   - Who paid
   - Who to split between
   - Split type (equal or custom)
4. Click "Add Expense"

### Settling Up

1. Open a group
2. Click "Settle Up"
3. View suggested settlements (minimum transactions)
4. Record a settlement:
   - Select who paid whom
   - Enter amount
   - Select payment method
5. Click "Record Settlement"

## Project Structure

```
expense-splitter-python/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── forms.py              # WTForms form definitions
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── wsgi.py              # WSGI entry point for PythonAnywhere
├── .env.example         # Environment variables template
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── groups.html
│   ├── create_group.html
│   ├── group_detail.html
│   ├── add_expense.html
│   ├── settle_up.html
│   ├── profile.html
│   ├── 404.html
│   └── 500.html
└── static/              # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Features Explained

### Balance Calculation

The app automatically calculates balances for each member:
- Positive balance = they are owed money
- Negative balance = they owe money
- Zero balance = all settled

### Debt Simplification

Uses a greedy algorithm to minimize transactions:
- Instead of everyone paying everyone
- Calculates optimal payment flow
- Reduces number of settlements needed

Example:
- Alice owes Bob $10
- Bob owes Charlie $10
- Simplified: Alice pays Charlie $10 (one transaction instead of two)

## Security Features

- Password hashing with bcrypt
- CSRF protection on all forms
- SQL injection prevention via SQLAlchemy ORM
- Session-based authentication
- Secure secret key for production

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Troubleshooting

### Database Issues

If you get database errors:
```python
from app import app, db
with app.app_context():
    db.drop_all()  # Warning: deletes all data
    db.create_all()
```

### Import Errors

Make sure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### PythonAnywhere 404 Error

1. Check WSGI file path is correct
2. Verify virtual environment path
3. Check error logs in PythonAnywhere

## Future Enhancements

- [ ] Export expenses to CSV/PDF
- [ ] Recurring expenses
- [ ] Receipt image upload
- [ ] Email notifications
- [ ] Multi-currency support with live exchange rates
- [ ] Expense categories analytics
- [ ] Mobile app (React Native)

## Contributing

Feel free to fork and submit pull requests!

## License

MIT License - feel free to use for personal or commercial projects

## Support

For issues or questions, please open an issue on GitHub.

## Credits

Built with ❤️ using Flask and Bootstrap

