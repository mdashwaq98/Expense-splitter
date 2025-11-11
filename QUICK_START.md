# Quick Start Guide - Expense Splitter

Get your Expense Splitter app running in 5 minutes!

## For Local Development (Testing on Your Computer)

### Windows

1. **Open PowerShell or Command Prompt** in the `expense-splitter-python` folder

2. **Create virtual environment**:
```powershell
python -m venv venv
```

3. **Activate virtual environment**:
```powershell
venv\Scripts\activate
```

4. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

5. **Set environment variables** (create a `.env` file):
```
SECRET_KEY=my-secret-key-for-testing
DATABASE_URL=sqlite:///expense_splitter.db
```

Or just run with defaults:

6. **Run the app**:
```powershell
python app.py
```

7. **Open your browser** and go to: `http://localhost:5000`

8. **Sign up** for an account and start using the app!

### Linux/Mac

1. **Open Terminal** in the `expense-splitter-python` folder

2. **Create virtual environment**:
```bash
python3 -m venv venv
```

3. **Activate virtual environment**:
```bash
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Run the app**:
```bash
python app.py
```

6. **Open your browser** and go to: `http://localhost:5000`

## For PythonAnywhere (Deploy Online)

See the detailed guide in `PYTHONANYWHERE_SETUP.md`

### Quick Version:

1. Create account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code
3. Create virtual environment
4. Setup MySQL database
5. Configure WSGI file
6. Reload and access your app!

## First Steps After Running

1. **Sign Up**
   - Click "Get Started"
   - Enter your name, email, and password
   - Click "Sign Up"

2. **Login**
   - Use your credentials to login

3. **Create a Group**
   - Click "Create Group" button
   - Name it (e.g., "Roommates", "Trip to Vegas")
   - Choose currency
   - Click "Create Group"

4. **Add Members**
   - Enter their email addresses
   - They need to sign up first!

5. **Add an Expense**
   - Click "Add Expense"
   - Enter details (dinner, rent, groceries, etc.)
   - Select who paid
   - Select who should split it
   - Click "Add Expense"

6. **View Balances**
   - See who owes what
   - View suggested settlements

7. **Settle Up**
   - Click "Settle Up"
   - Record when someone pays
   - Balances update automatically!

## Troubleshooting

### "pip is not recognized" (Windows)
Install Python from [python.org](https://www.python.org) and check "Add to PATH"

### "command not found: python" (Mac/Linux)
Try `python3` instead of `python`

### Port 5000 already in use
Change the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed to 5001
```

### Can't activate virtual environment
Make sure you're in the correct folder:
```bash
cd expense-splitter-python
```

## What's Included

✅ User authentication (signup/login)  
✅ Group management  
✅ Expense tracking  
✅ Multiple split types (equal, custom)  
✅ Balance calculation  
✅ Debt simplification  
✅ Settlement tracking  
✅ Beautiful responsive UI  
✅ Dashboard with statistics  

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (local) / MySQL (production)
- **Frontend**: Bootstrap 5, HTML, CSS, JavaScript
- **Authentication**: Flask-Login with password hashing

## File Structure

```
expense-splitter-python/
├── app.py              # Main application
├── models.py           # Database models
├── forms.py            # Web forms
├── utils.py            # Helper functions
├── requirements.txt    # Dependencies
├── templates/          # HTML pages
├── static/            # CSS, JS, images
└── README.md          # Documentation
```

## Need Help?

- Check `README.md` for detailed documentation
- See `PYTHONANYWHERE_SETUP.md` for deployment guide
- All features are documented with examples

## Next Steps

- Customize the look (edit `static/css/style.css`)
- Add more features (see TODO in README)
- Deploy to PythonAnywhere to share with friends!
- Add your own categories or currencies

Happy expense splitting! 💰✨

