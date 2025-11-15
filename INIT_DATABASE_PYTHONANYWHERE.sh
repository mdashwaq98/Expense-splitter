#!/bin/bash
# Run this script on PythonAnywhere Bash console to initialize the database

cd ~/spendings

python3 << 'EOF'
from app import app, db, User

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create admin user if doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@spendings.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin / admin123")
    else:
        print("✅ Admin user already exists")
    
    print("✅ Database initialized!")
    print(f"✅ Total users in database: {User.query.count()}")
    
    # List all users
    users = User.query.all()
    print(f"\n👥 Users:")
    for user in users:
        print(f"   - {user.username}")

EOF

echo ""
echo "🎉 Database is ready!"
echo "✅ Now go to Web tab and click 'Reload' button"

