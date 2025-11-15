from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
import pandas as pd
from sqlalchemy import func
import os

app = Flask(__name__)
# Secret key for session management - CHANGE THIS to a random string!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-to-a-random-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spendings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model for Authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    currency = db.Column(db.String(3), default='USD')
    monthly_budget = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'source': self.source,
            'amount': self.amount,
            'type': self.type,
            'notes': self.notes
        }

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'notes': self.notes
        }

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creditor = db.Column(db.String(100), nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    minimum_payment = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.Integer)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'creditor': self.creditor,
            'original_amount': self.original_amount,
            'current_balance': self.current_balance,
            'interest_rate': self.interest_rate,
            'minimum_payment': self.minimum_payment,
            'due_date': self.due_date,
            'status': self.status
        }

class DebtPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debt_id = db.Column(db.Integer, db.ForeignKey('debt.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'debt_id': self.debt_id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'notes': self.notes
        }

class Savings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    goal_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'goal_name': self.goal_name,
            'notes': self.notes
        }

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        progress = (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'progress': round(progress, 2)
        }

class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat(),
            'category': self.category,
            'active': self.active
        }

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Convert empty email to None to avoid UNIQUE constraint issues
        if email == '' or email is None:
            email = None
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user, remember=True)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Main Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)

@app.route('/modern')
@login_required
def modern_dashboard():
    return render_template('modern_dashboard.html', username=current_user.username)

@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    # Calculate dashboard metrics for current user
    total_income = db.session.query(func.sum(Income.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_savings = db.session.query(func.sum(Savings.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_debt = db.session.query(func.sum(Debt.current_balance)).filter_by(user_id=current_user.id, status='active').scalar() or 0
    total_debt_paid = db.session.query(func.sum(DebtPayment.amount)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Get recent transactions
    recent_income = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    
    return jsonify({
        'summary': {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'total_savings': round(total_savings, 2),
            'total_debt': round(total_debt, 2),
            'total_debt_paid': round(total_debt_paid, 2),
            'net_balance': round(total_income - total_expenses - total_savings, 2)
        },
        'recent_income': [i.to_dict() for i in recent_income],
        'recent_expenses': [e.to_dict() for e in recent_expenses],
        'currency': current_user.currency or 'USD',
        'monthly_budget': current_user.monthly_budget or 0
    })

# Income endpoints
@app.route('/api/income', methods=['GET', 'POST'])
@login_required
def handle_income():
    if request.method == 'POST':
        data = request.json
        income = Income(
            user_id=current_user.id,
            date=datetime.fromisoformat(data['date']).date(),
            source=data['source'],
            amount=float(data['amount']),
            type=data['type'],
            notes=data.get('notes', '')
        )
        db.session.add(income)
        db.session.commit()
        return jsonify(income.to_dict()), 201
    else:
        incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
        return jsonify([i.to_dict() for i in incomes])

@app.route('/api/income/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def handle_income_item(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'PUT':
        data = request.json
        income.date = datetime.fromisoformat(data['date']).date()
        income.source = data['source']
        income.amount = float(data['amount'])
        income.type = data['type']
        income.notes = data.get('notes', '')
        db.session.commit()
        return jsonify(income.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(income)
        db.session.commit()
        return '', 204

# Expense endpoints
@app.route('/api/expenses', methods=['GET', 'POST'])
@login_required
def handle_expenses():
    if request.method == 'POST':
        data = request.json
        expense = Expense(
            user_id=current_user.id,
            date=datetime.fromisoformat(data['date']).date(),
            category=data['category'],
            amount=float(data['amount']),
            description=data.get('description', ''),
            notes=data.get('notes', '')
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify(expense.to_dict()), 201
    else:
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        return jsonify([e.to_dict() for e in expenses])

@app.route('/api/expenses/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def handle_expense_item(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'PUT':
        data = request.json
        expense.date = datetime.fromisoformat(data['date']).date()
        expense.category = data['category']
        expense.amount = float(data['amount'])
        expense.description = data.get('description', '')
        expense.notes = data.get('notes', '')
        db.session.commit()
        return jsonify(expense.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(expense)
        db.session.commit()
        return '', 204

# Debt endpoints
@app.route('/api/debts', methods=['GET', 'POST'])
@login_required
def handle_debts():
    if request.method == 'POST':
        data = request.json
        debt = Debt(
            user_id=current_user.id,
            creditor=data['creditor'],
            original_amount=float(data['original_amount']),
            current_balance=float(data['current_balance']),
            interest_rate=float(data.get('interest_rate', 0)),
            minimum_payment=float(data.get('minimum_payment', 0)),
            due_date=data.get('due_date'),
            status=data.get('status', 'active')
        )
        db.session.add(debt)
        db.session.commit()
        return jsonify(debt.to_dict()), 201
    else:
        debts = Debt.query.filter_by(user_id=current_user.id).all()
        return jsonify([d.to_dict() for d in debts])

@app.route('/api/debts/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def handle_debt_item(id):
    debt = Debt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'PUT':
        data = request.json
        debt.creditor = data['creditor']
        debt.current_balance = float(data['current_balance'])
        debt.interest_rate = float(data.get('interest_rate', 0))
        debt.minimum_payment = float(data.get('minimum_payment', 0))
        debt.due_date = data.get('due_date')
        debt.status = data.get('status', 'active')
        db.session.commit()
        return jsonify(debt.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(debt)
        db.session.commit()
        return '', 204

# Debt Payment endpoints
@app.route('/api/debt-payments', methods=['GET', 'POST'])
@login_required
def handle_debt_payments():
    if request.method == 'POST':
        data = request.json
        payment = DebtPayment(
            user_id=current_user.id,
            debt_id=int(data['debt_id']),
            date=datetime.fromisoformat(data['date']).date(),
            amount=float(data['amount']),
            notes=data.get('notes', '')
        )
        db.session.add(payment)
        
        # Update debt balance
        debt = Debt.query.filter_by(id=data['debt_id'], user_id=current_user.id).first()
        if debt:
            debt.current_balance -= float(data['amount'])
            if debt.current_balance <= 0:
                debt.current_balance = 0
                debt.status = 'paid_off'
        
        db.session.commit()
        return jsonify(payment.to_dict()), 201
    else:
        payments = DebtPayment.query.filter_by(user_id=current_user.id).order_by(DebtPayment.date.desc()).all()
        return jsonify([p.to_dict() for p in payments])

# Savings endpoints
@app.route('/api/savings', methods=['GET', 'POST'])
@login_required
def handle_savings():
    if request.method == 'POST':
        data = request.json
        saving = Savings(
            user_id=current_user.id,
            date=datetime.fromisoformat(data['date']).date(),
            amount=float(data['amount']),
            goal_name=data.get('goal_name', ''),
            notes=data.get('notes', '')
        )
        db.session.add(saving)
        
        # Update savings goal if specified
        if data.get('goal_name'):
            goal = SavingsGoal.query.filter_by(user_id=current_user.id, name=data['goal_name'], status='active').first()
            if goal:
                goal.current_amount += float(data['amount'])
                if goal.current_amount >= goal.target_amount:
                    goal.status = 'completed'
        
        db.session.commit()
        return jsonify(saving.to_dict()), 201
    else:
        savings = Savings.query.filter_by(user_id=current_user.id).order_by(Savings.date.desc()).all()
        return jsonify([s.to_dict() for i in savings])

# Savings Goals endpoints
@app.route('/api/savings-goals', methods=['GET', 'POST'])
@login_required
def handle_savings_goals():
    if request.method == 'POST':
        data = request.json
        goal = SavingsGoal(
            user_id=current_user.id,
            name=data['name'],
            target_amount=float(data['target_amount']),
            current_amount=float(data.get('current_amount', 0)),
            deadline=datetime.fromisoformat(data['deadline']).date() if data.get('deadline') else None,
            status=data.get('status', 'active')
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify(goal.to_dict()), 201
    else:
        goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
        return jsonify([g.to_dict() for g in goals])

# Recurring Expenses endpoints
@app.route('/api/recurring-expenses', methods=['GET', 'POST'])
@login_required
def handle_recurring_expenses():
    if request.method == 'POST':
        data = request.json
        recurring = RecurringExpense(
            user_id=current_user.id,
            name=data['name'],
            amount=float(data['amount']),
            frequency=data['frequency'],
            start_date=datetime.fromisoformat(data['start_date']).date(),
            category=data.get('category', ''),
            active=data.get('active', True)
        )
        db.session.add(recurring)
        db.session.commit()
        return jsonify(recurring.to_dict()), 201
    else:
        recurring = RecurringExpense.query.filter_by(user_id=current_user.id).all()
        return jsonify([r.to_dict() for r in recurring])

# Analytics endpoints
@app.route('/api/analytics/expenses-by-category', methods=['GET'])
@login_required
def expenses_by_category():
    results = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter_by(user_id=current_user.id).group_by(Expense.category).all()
    
    return jsonify([{'category': r[0], 'total': round(r[1], 2)} for r in results])

@app.route('/api/analytics/income-by-type', methods=['GET'])
@login_required
def income_by_type():
    results = db.session.query(
        Income.type,
        func.sum(Income.amount).label('total')
    ).filter_by(user_id=current_user.id).group_by(Income.type).all()
    
    return jsonify([{'type': r[0], 'total': round(r[1], 2)} for r in results])

@app.route('/api/analytics/monthly-summary', methods=['GET'])
@login_required
def monthly_summary():
    # Get current year data for current user
    current_year = datetime.now().year
    
    # Income by month
    income_data = db.session.query(
        func.strftime('%m', Income.date).label('month'),
        func.sum(Income.amount).label('total')
    ).filter(
        Income.user_id == current_user.id,
        func.strftime('%Y', Income.date) == str(current_year)
    ).group_by('month').all()
    
    # Expenses by month
    expense_data = db.session.query(
        func.strftime('%m', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        func.strftime('%Y', Expense.date) == str(current_year)
    ).group_by('month').all()
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    income_by_month = {str(i+1).zfill(2): 0 for i in range(12)}
    expense_by_month = {str(i+1).zfill(2): 0 for i in range(12)}
    
    for row in income_data:
        income_by_month[row[0]] = round(row[1], 2)
    
    for row in expense_data:
        expense_by_month[row[0]] = round(row[1], 2)
    
    return jsonify({
        'months': months,
        'income': [income_by_month[str(i+1).zfill(2)] for i in range(12)],
        'expenses': [expense_by_month[str(i+1).zfill(2)] for i in range(12)]
    })

# Import from Excel
@app.route('/api/import-excel', methods=['POST'])
@login_required
def import_excel():
    try:
        xls = pd.ExcelFile('Master Sheet.xlsx')
        
        # Import main income/expense data
        side_income_df = pd.read_excel(xls, sheet_name='Side Income')
        expenses_df = pd.read_excel(xls, sheet_name='ManualExpenses')
        
        imported_count = 0
        
        # Import side income
        for _, row in side_income_df.iterrows():
            if pd.notna(row.get('source')) and pd.notna(row.get('pay')):
                income = Income(
                    user_id=current_user.id,
                    date=pd.to_datetime(row.get('date')).date() if pd.notna(row.get('date')) else date.today(),
                    source=str(row['source']),
                    amount=float(row['pay']),
                    type='side',
                    notes=f"Period: {row.get('period', '')}"
                )
                db.session.add(income)
                imported_count += 1
        
        # Import manual expenses
        for _, row in expenses_df.iterrows():
            if pd.notna(row.get('expense')) and row.get('expense') != 'Total':
                expense = Expense(
                    user_id=current_user.id,
                    date=pd.to_datetime(row.get('date')).date() if pd.notna(row.get('date')) else date.today(),
                    category=str(row.get('type', 'Other')),
                    amount=float(row['expense']),
                    description=f"Period: {row.get('Period', '')}"
                )
                db.session.add(expense)
                imported_count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'imported': imported_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Budget Settings Page
@app.route('/budget-settings')
@login_required
def budget_settings():
    return render_template('budget_settings.html', username=current_user.username)

# Update User Settings (Currency & Budget)
@app.route('/api/user/settings', methods=['PUT'])
@login_required
def update_user_settings():
    data = request.json
    if 'currency' in data:
        current_user.currency = data['currency']
    if 'monthly_budget' in data:
        current_user.monthly_budget = float(data['monthly_budget'])
    db.session.commit()
    return jsonify({'success': True})

# Get Budget Status
@app.route('/api/budget/status', methods=['GET'])
@login_required
def get_budget_status():
    # Get current month expenses
    today = datetime.utcnow()
    month_start = datetime(today.year, today.month, 1)
    
    month_expenses = db.session.query(func.sum(Expense.amount))\
        .filter(Expense.user_id == current_user.id)\
        .filter(Expense.date >= month_start)\
        .scalar() or 0
    
    budget = current_user.monthly_budget or 0
    percentage = (month_expenses / budget * 100) if budget > 0 else 0
    remaining = budget - month_expenses
    
    return jsonify({
        'budget': budget,
        'spent': month_expenses,
        'remaining': remaining,
        'percentage': percentage,
        'currency': current_user.currency,
        'warning': percentage >= 80,
        'exceeded': percentage >= 100
    })

# For local development only - Uncomment to run locally
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default user if none exists
        if not User.query.first():
            default_user = User(username='admin', email='admin@spendings.com')
            default_user.set_password('admin123')  # CHANGE THIS PASSWORD!
            db.session.add(default_user)
            db.session.commit()
            print("Default user created: username='admin', password='admin123'")
    
    # host='0.0.0.0' makes it accessible from other devices on your network
    app.run(host='0.0.0.0', debug=True, port=5000)
