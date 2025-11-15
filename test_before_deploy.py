"""
Pre-Deployment Verification Script
Run this before deploying to PythonAnywhere to catch any issues early!
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("✓ Testing package imports...")
    try:
        import flask
        print("  ✓ Flask installed")
        import flask_sqlalchemy
        print("  ✓ Flask-SQLAlchemy installed")
        import flask_login
        print("  ✓ Flask-Login installed")
        import pandas
        print("  ✓ Pandas installed")
        import openpyxl
        print("  ✓ Openpyxl installed")
        from werkzeug.security import generate_password_hash
        print("  ✓ Werkzeug installed")
        return True
    except ImportError as e:
        print(f"  ✗ ERROR: {e}")
        print("\n  Fix: Run 'pip install -r requirements.txt'")
        return False

def test_files():
    """Test if all required files exist"""
    print("\n✓ Testing required files...")
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'templates/login.html',
        'static/style.css',
        'static/app.js',
        'Master Sheet.xlsx'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ MISSING: {file}")
            all_exist = False
    
    return all_exist

def test_app_structure():
    """Test if app.py has correct structure"""
    print("\n✓ Testing app.py structure...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = {
            'Flask import': 'from flask import Flask',
            'Flask-Login import': 'from flask_login import',
            'LoginManager setup': 'login_manager = LoginManager',
            'User model': 'class User',
            'Login route': '@app.route(\'/login\'',
            'Logout route': '@app.route(\'/logout\'',
        }
        
        all_passed = True
        for check, code in checks.items():
            if code in content:
                print(f"  ✓ {check}")
            else:
                print(f"  ✗ MISSING: {check}")
                all_passed = False
                
        return all_passed
    except Exception as e:
        print(f"  ✗ ERROR reading app.py: {e}")
        return False

def main():
    print("="*60)
    print("🚀 PRE-DEPLOYMENT VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("Required Files", test_files()))
    results.append(("App Structure", test_app_structure()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ You're ready to deploy to PythonAnywhere!")
        print("\n📖 Next step: Follow PYTHONANYWHERE_STEP_BY_STEP.md")
    else:
        print("\n⚠️  SOME CHECKS FAILED!")
        print("❌ Please fix the errors above before deploying")
        print("\n💡 Need help? Copy the error messages and ask!")
    
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

