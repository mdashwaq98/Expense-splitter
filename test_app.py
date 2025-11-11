"""
Simple test script to verify the application setup
Run this to check if everything is configured correctly
"""
import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        print("✓ Flask installed")
        import flask_sqlalchemy
        print("✓ Flask-SQLAlchemy installed")
        import flask_login
        print("✓ Flask-Login installed")
        import flask_wtf
        print("✓ Flask-WTF installed")
        import flask_bcrypt
        print("✓ Flask-Bcrypt installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created"""
    print("\nTesting app creation...")
    try:
        from app import app, db
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating app: {e}")
        return False

def test_database():
    """Test if database can be initialized"""
    print("\nTesting database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def test_models():
    """Test if models are properly defined"""
    print("\nTesting models...")
    try:
        from models import User, Group, GroupMember, Expense, ExpenseParticipant, Settlement
        print("✓ User model imported")
        print("✓ Group model imported")
        print("✓ GroupMember model imported")
        print("✓ Expense model imported")
        print("✓ ExpenseParticipant model imported")
        print("✓ Settlement model imported")
        return True
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False

def test_forms():
    """Test if forms are properly defined"""
    print("\nTesting forms...")
    try:
        from forms import LoginForm, SignUpForm, CreateGroupForm, AddExpenseForm, SettlementForm
        print("✓ LoginForm imported")
        print("✓ SignUpForm imported")
        print("✓ CreateGroupForm imported")
        print("✓ AddExpenseForm imported")
        print("✓ SettlementForm imported")
        return True
    except Exception as e:
        print(f"✗ Error importing forms: {e}")
        return False

def test_utils():
    """Test if utility functions work"""
    print("\nTesting utilities...")
    try:
        from utils import calculate_balances, simplify_debts
        print("✓ Utility functions imported")
        return True
    except Exception as e:
        print(f"✗ Error importing utilities: {e}")
        return False

def test_routes():
    """Test if basic routes are accessible"""
    print("\nTesting routes...")
    try:
        from app import app
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible")
            else:
                print(f"✗ Home page returned status {response.status_code}")
                return False
            
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                print("✓ Login page accessible")
            else:
                print(f"✗ Login page returned status {response.status_code}")
                return False
            
            # Test signup page
            response = client.get('/signup')
            if response.status_code == 200:
                print("✓ Signup page accessible")
            else:
                print(f"✗ Signup page returned status {response.status_code}")
                return False
            
        return True
    except Exception as e:
        print(f"✗ Error testing routes: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("EXPENSE SPLITTER - APPLICATION TEST")
    print("=" * 50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("App Creation", test_app_creation()))
    results.append(("Database", test_database()))
    results.append(("Models", test_models()))
    results.append(("Forms", test_forms()))
    results.append(("Utilities", test_utils()))
    results.append(("Routes", test_routes()))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("Your app is ready to run: python app.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please check the errors above and fix them.")
        print("Common fixes:")
        print("  1. Make sure virtual environment is activated")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Check for typos in code")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

