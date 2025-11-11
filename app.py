"""
Main Flask application entry point for Expense Splitter
"""
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
from sqlalchemy import func
# Optional import for Excel functionality
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from models import db, User, Group, GroupMember, Expense, ExpenseParticipant, Settlement, Friendship, Invitation, PasswordReset, Income, PersonalExpense, Debt, DebtPayment, Savings, SavingsGoal, RecurringExpense
from forms import LoginForm, SignUpForm, CreateGroupForm, AddExpenseForm, SettlementForm, AddFriendForm, InviteFriendForm, ForgotPasswordForm, ResetPasswordForm
from utils import calculate_balances, simplify_debts, get_friend_balance
import secrets
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///expense_splitter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail Configuration (optional - app works without email)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@expensesplitter.com')

# Initialize Flask-Mail (optional)
mail = None
MAIL_ENABLED = False
Message = None
try:
    from flask_mail import Mail, Message
    mail = Mail(app)
    MAIL_ENABLED = bool(app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD'])
    if not MAIL_ENABLED:
        print("⚠️  Email not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
except ImportError:
    print("⚠️  Flask-Mail not installed. Email features disabled. Install with: pip install Flask-Mail")

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and handle migrations
with app.app_context():
    db.create_all()
    
    # Migration: Add theme_preference column if it doesn't exist
    try:
        # Try to query theme_preference to see if column exists
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'theme_preference' not in columns:
            print("⚠️  Migrating database: Adding theme_preference column...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN theme_preference VARCHAR(10) DEFAULT 'dark'"))
                conn.commit()
            print("✅ Migration complete: theme_preference column added")
        
        # Migration: Add monthly_budget column if it doesn't exist
        if 'monthly_budget' not in columns:
            print("⚠️  Migrating database: Adding monthly_budget column...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN monthly_budget FLOAT DEFAULT 0.0"))
                conn.commit()
            print("✅ Migration complete: monthly_budget column added")
        
        # Migration: Add view_preference column if it doesn't exist
        if 'view_preference' not in columns:
            print("⚠️  Migrating database: Adding view_preference column...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN view_preference VARCHAR(20) DEFAULT 'separate'"))
                conn.commit()
            print("✅ Migration complete: view_preference column added")
    except Exception as e:
        print(f"⚠️  Migration check failed (may already exist): {e}")

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        # Normalize email to lowercase
        email = form.email.data.lower().strip()
        
        # Check if user already exists (case-insensitive)
        existing_user = User.query.filter(func.lower(User.email) == email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user with lowercase email
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Normalize email to lowercase for case-insensitive lookup
        email = form.email.data.lower().strip()
        user = User.query.filter(func.lower(User.email) == email).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter(func.lower(User.email) == email).first()
        
        if user:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            
            # Create password reset record (expires in 1 hour)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Invalidate any existing reset tokens for this user
            PasswordReset.query.filter_by(user_id=user.id, used=False).update({'used': True})
            
            reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset)
            db.session.commit()
            
            # Send email if configured
            if MAIL_ENABLED and mail:
                try:
                    reset_url = url_for('reset_password', token=token, _external=True)
                    msg = Message(
                        subject='Password Reset Request - Expense Splitter',
                        recipients=[user.email],
                        html=f'''
                        <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                                <h2 style="color: #5b7cff;">Password Reset Request</h2>
                                <p>Hello {user.name},</p>
                                <p>You requested to reset your password. Click the button below to reset it:</p>
                                <p style="text-align: center; margin: 30px 0;">
                                    <a href="{reset_url}" style="background: #5b7cff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">Reset Password</a>
                                </p>
                                <p>Or copy and paste this link into your browser:</p>
                                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                                <p style="color: #999; font-size: 12px;">This link will expire in 1 hour.</p>
                                <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
                            </div>
                        </body>
                        </html>
                        '''
                    )
                    mail.send(msg)
                    flash('Password reset link has been sent to your email!', 'success')
                except Exception as e:
                    print(f"⚠️  Email sending failed: {e}")
                    flash(f'Password reset link generated. Since email is not configured, your reset token is: {token}. Please use /reset-password/{token}', 'warning')
            else:
                # Email not configured - show token in flash message (development only)
                reset_url = url_for('reset_password', token=token, _external=True)
                flash(f'Password reset link: {reset_url} (Email not configured. Copy this link.)', 'info')
        else:
            # Don't reveal if email exists (security best practice)
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Find valid reset token
    reset = PasswordReset.query.filter_by(token=token, used=False).first()
    
    if not reset or not reset.is_valid():
        flash('Invalid or expired password reset link. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update user password
        reset.user.password = generate_password_hash(form.password.data)
        
        # Mark reset token as used
        reset.used = True
        
        # Invalidate all other reset tokens for this user
        PasswordReset.query.filter_by(user_id=reset.user_id, used=False).update({'used': True})
        
        db.session.commit()
        
        flash('Password has been reset successfully! Please login with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', form=form, token=token)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all groups where user is a member
    user_groups = Group.query.join(GroupMember).filter(
        GroupMember.user_id == current_user.id
    ).all()
    
    # Calculate summary statistics
    total_balance = 0
    total_owed = 0
    total_owing = 0
    
    # Track who you owe and who owes you
    who_you_owe = []  # People you owe money to
    who_owes_you = []  # People who owe you money
    
    for group in user_groups:
        balances = calculate_balances(group)
        user_balance = next((b for b in balances if b['user_id'] == current_user.id), None)
        if user_balance:
            balance_amount = user_balance['amount']
            total_balance += balance_amount
            
            # Track individual balances - compare with current user's balance
            user_bal = user_balance['amount']
            for balance in balances:
                if balance['user_id'] != current_user.id and abs(balance['amount']) > 0.01:
                    other_user_id = balance['user_id']
                    other_user_name = balance['user_name']
                    other_balance = balance['amount']
                    
                    # Calculate relative debt: if other has more positive balance than you,
                    # you owe them; if they have more negative, they owe you
                    # Simplified: track based on relative difference
                    if user_bal < 0 and other_balance > 0:
                        # You owe, they're owed - you likely owe them
                        who_you_owe.append({
                            'name': other_user_name,
                            'amount': min(abs(user_bal), other_balance),
                            'group': group.name,
                            'group_id': group.id
                        })
                    elif user_bal > 0 and other_balance < 0:
                        # You're owed, they owe - they owe you
                        who_owes_you.append({
                            'name': other_user_name,
                            'amount': min(user_bal, abs(other_balance)),
                            'group': group.name,
                            'group_id': group.id
                        })
            
            if balance_amount > 0:
                total_owed += balance_amount
            else:
                total_owing += abs(balance_amount)
    
    # Get friend balances
    friendships = Friendship.query.filter(
        (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
    ).all()
    
    friend_users = []
    for friendship in friendships:
        if friendship.user_id == current_user.id:
            friend_users.append(friendship.friend)
        else:
            friend_users.append(friendship.user)
    
    friend_balances_list = []
    for friend in friend_users:
        balance = get_friend_balance(current_user.id, friend.id)
        if abs(balance) > 0.01:
            if balance > 0:
                who_owes_you.append({
                    'name': friend.name,
                    'amount': balance,
                    'group': 'Friends',
                    'group_id': None,
                    'friend_id': friend.id
                })
            else:
                who_you_owe.append({
                    'name': friend.name,
                    'amount': abs(balance),
                    'group': 'Friends',
                    'group_id': None,
                    'friend_id': friend.id
                })
    
    # Consolidate duplicate entries (same person across multiple groups)
    from collections import defaultdict
    consolidated_owe = defaultdict(lambda: {'amount': 0, 'groups': [], 'group_ids': []})
    consolidated_owed = defaultdict(lambda: {'amount': 0, 'groups': [], 'group_ids': []})
    
    for item in who_you_owe:
        consolidated_owe[item['name']]['amount'] += item['amount']
        if item['group'] not in consolidated_owe[item['name']]['groups']:
            consolidated_owe[item['name']]['groups'].append(item['group'])
        if item.get('group_id') and item['group_id'] not in consolidated_owe[item['name']]['group_ids']:
            consolidated_owe[item['name']]['group_ids'].append(item['group_id'])
        if item.get('friend_id'):
            consolidated_owe[item['name']]['friend_id'] = item['friend_id']
    
    for item in who_owes_you:
        consolidated_owed[item['name']]['amount'] += item['amount']
        if item['group'] not in consolidated_owed[item['name']]['groups']:
            consolidated_owed[item['name']]['groups'].append(item['group'])
        if item.get('group_id') and item['group_id'] not in consolidated_owed[item['name']]['group_ids']:
            consolidated_owed[item['name']]['group_ids'].append(item['group_id'])
        if item.get('friend_id'):
            consolidated_owed[item['name']]['friend_id'] = item['friend_id']
    
    # Convert back to list format
    who_you_owe_consolidated = [
        {
            'name': name,
            'amount': data['amount'],
            'group': ', '.join(data['groups'][:2]) + ('...' if len(data['groups']) > 2 else ''),
            'group_id': data['group_ids'][0] if data['group_ids'] else None,
            'friend_id': data.get('friend_id')
        }
        for name, data in consolidated_owe.items()
    ]
    
    who_owes_you_consolidated = [
        {
            'name': name,
            'amount': data['amount'],
            'group': ', '.join(data['groups'][:2]) + ('...' if len(data['groups']) > 2 else ''),
            'group_id': data['group_ids'][0] if data['group_ids'] else None,
            'friend_id': data.get('friend_id')
        }
        for name, data in consolidated_owed.items()
    ]
    
    # Get recent expenses across all groups
    from models import Expense
    recent_expenses = Expense.query.join(Group).join(GroupMember).filter(
        GroupMember.user_id == current_user.id
    ).order_by(Expense.date.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         groups=user_groups,
                         total_balance=total_balance,
                         total_owed=total_owed,
                         total_owing=total_owing,
                         who_you_owe=who_you_owe_consolidated,
                         who_owes_you=who_owes_you_consolidated,
                         recent_expenses=recent_expenses)

@app.route('/groups')
@login_required
def groups():
    # Only show regular groups, not friend groups (friend groups are shown in Friends tab)
    user_groups = Group.query.join(GroupMember).filter(
        GroupMember.user_id == current_user.id,
        Group.is_friend_group == False  # Exclude friend groups
    ).all()
    return render_template('groups.html', groups=user_groups)

@app.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            currency=form.currency.data,
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.flush()
        
        # Add creator as admin member
        member = GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            role='admin'
        )
        db.session.add(member)
        db.session.commit()
        
        flash('Group created successfully!', 'success')
        return redirect(url_for('group_detail', group_id=group.id))
    
    return render_template('create_group.html', form=form)

@app.route('/groups/<int:group_id>')
@login_required
def group_detail(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is a member
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    if not member:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups'))
    
    # Get expenses
    expenses = Expense.query.filter_by(group_id=group_id).order_by(Expense.date.desc()).all()
    
    # Calculate balances
    balances = calculate_balances(group)
    
    # Simplify debts
    simplified_debts = simplify_debts(balances)
    
    return render_template('group_detail.html', 
                         group=group, 
                         expenses=expenses,
                         balances=balances,
                         simplified_debts=simplified_debts,
                         is_admin=member.role == 'admin')

@app.route('/groups/<int:group_id>/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is a member
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    if not member:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups'))
    
    form = AddExpenseForm()
    
    # Populate member choices
    members = group.members
    form.paid_by.choices = [(m.user.id, m.user.name) for m in members]
    form.participants.choices = [(m.user.id, m.user.name) for m in members]
    
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            currency=group.currency,
            category=form.category.data,
            paid_by=form.paid_by.data,
            group_id=group_id,
            split_type=form.split_type.data,
            date=form.date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(expense)
        db.session.flush()
        
        # Add participants
        participant_ids = form.participants.data
        if form.split_type.data == 'equal':
            share = expense.amount / len(participant_ids)
            for user_id in participant_ids:
                participant = ExpenseParticipant(
                    expense_id=expense.id,
                    user_id=user_id,
                    share=round(share, 2)
                )
                db.session.add(participant)
        
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('group_detail', group_id=group_id))
    
    return render_template('add_expense.html', form=form, group=group)

@app.route('/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Check if user is authorized (must be creator or member of group)
    if expense.created_by != current_user.id:
        # Check if user is member of the group
        if expense.group_id:
            member = GroupMember.query.filter_by(
                group_id=expense.group_id,
                user_id=current_user.id
            ).first()
            if not member:
                flash('You are not authorized to edit this expense.', 'danger')
                return redirect(url_for('groups'))
        else:
            flash('You are not authorized to edit this expense.', 'danger')
            return redirect(url_for('groups'))
    
    group = expense.group
    form = AddExpenseForm(obj=expense)
    
    # Populate member choices
    members = group.members if group else []
    form.paid_by.choices = [(m.user.id, m.user.name) for m in members]
    form.participants.choices = [(m.user.id, m.user.name) for m in members]
    
    # Pre-populate participants
    existing_participants = [p.user_id for p in expense.participants]
    form.participants.data = existing_participants
    
    if form.validate_on_submit():
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.category = form.category.data
        expense.paid_by = form.paid_by.data
        expense.split_type = form.split_type.data
        expense.date = form.date.data
        expense.notes = form.notes.data
        
        # Delete existing participants
        ExpenseParticipant.query.filter_by(expense_id=expense.id).delete()
        
        # Add new participants
        participant_ids = form.participants.data
        if form.split_type.data == 'equal':
            share = expense.amount / len(participant_ids)
            for user_id in participant_ids:
                participant = ExpenseParticipant(
                    expense_id=expense.id,
                    user_id=user_id,
                    share=round(share, 2)
                )
                db.session.add(participant)
        
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('group_detail', group_id=expense.group_id))
    
    return render_template('edit_expense.html', form=form, expense=expense, group=group)

@app.route('/expenses/<int:expense_id>/edit-friend', methods=['GET', 'POST'])
@login_required
def edit_friend_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Check if user is authorized (must be creator or participant)
    if expense.created_by != current_user.id:
        participant = ExpenseParticipant.query.filter_by(
            expense_id=expense_id,
            user_id=current_user.id
        ).first()
        if not participant:
            flash('You are not authorized to edit this expense.', 'danger')
            return redirect(url_for('friends'))
    
    # Get friend from participants
    participants = expense.participants
    friend_id = None
    friend = None
    for p in participants:
        if p.user_id != current_user.id:
            friend_id = p.user_id
            friend = User.query.get(friend_id)
            break
    
    if not friend:
        flash('Friend not found for this expense.', 'danger')
        return redirect(url_for('friends'))
    
    # Get or find friend group
    friend_group = expense.group
    
    form = AddExpenseForm(obj=expense)
    form.paid_by.choices = [(current_user.id, current_user.name), (friend_id, friend.name)]
    form.participants.choices = [(current_user.id, current_user.name), (friend_id, friend.name)]
    
    # Pre-populate participants and percentages
    form.participants.data = [current_user.id, friend_id]
    
    # Get existing shares to calculate percentages
    user_participant = next((p for p in participants if p.user_id == current_user.id), None)
    friend_participant = next((p for p in participants if p.user_id == friend_id), None)
    
    if user_participant and friend_participant and expense.amount > 0:
        form.user_percentage.data = round((user_participant.share / expense.amount) * 100, 2)
        form.friend_percentage.data = round((friend_participant.share / expense.amount) * 100, 2)
        if abs(form.user_percentage.data + form.friend_percentage.data - 100) < 1:
            form.split_type.data = 'percentage'
        else:
            form.split_type.data = 'equal'
            form.user_percentage.data = 50.0
            form.friend_percentage.data = 50.0
    else:
        form.split_type.data = 'equal'
        form.user_percentage.data = 50.0
        form.friend_percentage.data = 50.0
    
    if form.validate_on_submit():
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.category = form.category.data
        expense.paid_by = form.paid_by.data
        expense.split_type = form.split_type.data
        expense.date = form.date.data
        expense.notes = form.notes.data
        
        # Delete existing participants
        ExpenseParticipant.query.filter_by(expense_id=expense.id).delete()
        
        # Calculate shares based on split type
        if form.split_type.data == 'percentage':
            user_percent = form.user_percentage.data / 100
            friend_percent = form.friend_percentage.data / 100
            user_share = round(expense.amount * user_percent, 2)
            friend_share = round(expense.amount * friend_percent, 2)
        else:
            share = expense.amount / 2
            user_share = round(share, 2)
            friend_share = round(share, 2)
        
        participant1 = ExpenseParticipant(expense_id=expense.id, user_id=current_user.id, share=user_share)
        participant2 = ExpenseParticipant(expense_id=expense.id, user_id=friend_id, share=friend_share)
        db.session.add(participant1)
        db.session.add(participant2)
        
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('friend_detail', friend_id=friend_id))
    
    return render_template('edit_friend_expense.html', form=form, expense=expense, friend=friend)

@app.route('/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Check if user is authorized (creator, admin, or participant)
    is_authorized = False
    redirect_url = url_for('groups')
    group_id = None
    
    if expense.created_by == current_user.id:
        is_authorized = True
    elif expense.group_id:
        # Check if user is admin of the group
        member = GroupMember.query.filter_by(
            group_id=expense.group_id,
            user_id=current_user.id,
            role='admin'
        ).first()
        if member:
            is_authorized = True
            redirect_url = url_for('group_detail', group_id=expense.group_id)
            group_id = expense.group_id
        else:
            # Check if user is a participant
            participant = ExpenseParticipant.query.filter_by(
                expense_id=expense_id,
                user_id=current_user.id
            ).first()
            if participant:
                is_authorized = True
                redirect_url = url_for('group_detail', group_id=expense.group_id)
                group_id = expense.group_id
    else:
        # Friend expense - check if user is participant
        participant = ExpenseParticipant.query.filter_by(
            expense_id=expense_id,
            user_id=current_user.id
        ).first()
        if participant:
            is_authorized = True
            # Find friend
            participants = expense.participants
            friend_id = None
            for p in participants:
                if p.user_id != current_user.id:
                    friend_id = p.user_id
                    break
            if friend_id:
                redirect_url = url_for('friend_detail', friend_id=friend_id)
            else:
                redirect_url = url_for('friends')
    
    if not is_authorized:
        flash('You are not authorized to delete this expense.', 'danger')
        return redirect(redirect_url)
    
    # Get expense info for flash message
    expense_description = expense.description
    expense_amount = expense.amount
    
    # Delete expense (participants will be deleted automatically due to cascade)
    db.session.delete(expense)
    db.session.commit()
    
    flash(f'Expense "{expense_description}" (${expense_amount:.2f}) has been deleted.', 'success')
    return redirect(redirect_url)

@app.route('/groups/<int:group_id>/settle', methods=['GET', 'POST'])
@login_required
def settle_up(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is a member
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    if not member:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups'))
    
    form = SettlementForm()
    
    # Populate member choices
    members = group.members
    form.from_user.choices = [(m.user.id, m.user.name) for m in members]
    form.to_user.choices = [(m.user.id, m.user.name) for m in members]
    
    if form.validate_on_submit():
        settlement = Settlement(
            group_id=group_id,
            from_user=form.from_user.data,
            to_user=form.to_user.data,
            amount=form.amount.data,
            currency=group.currency,
            payment_method=form.payment_method.data,
            status='completed'
        )
        db.session.add(settlement)
        db.session.commit()
        
        flash('Settlement recorded successfully!', 'success')
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Get suggested settlements
    balances = calculate_balances(group)
    simplified_debts = simplify_debts(balances)
    
    return render_template('settle_up.html', 
                         form=form, 
                         group=group,
                         suggested_settlements=simplified_debts)

@app.route('/groups/<int:group_id>/add-member', methods=['POST'])
@login_required
def add_member(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is admin
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id,
        role='admin'
    ).first()
    if not member:
        flash('Only admins can add members.', 'danger')
        return redirect(url_for('group_detail', group_id=group_id))
    
    email = request.form.get('email', '').lower().strip()
    if not email:
        flash('Please provide an email address.', 'warning')
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Case-insensitive user lookup
    user = User.query.filter(func.lower(User.email) == email).first()
    
    if not user:
        # Check if they're invited (friend) - allow adding even if they didn't accept
        invitation = Invitation.query.filter(
            func.lower(Invitation.email) == email,
            Invitation.invited_by == current_user.id,
            Invitation.status == 'pending'
        ).first()
        
        if invitation:
            # Allow adding friend even without invitation acceptance
            flash(f'{email} is invited but not yet registered. They can join when they sign up.', 'info')
            return redirect(url_for('group_detail', group_id=group_id))
        
        flash('User not found. They need to sign up first.', 'warning')
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Check if already a member
    existing_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=user.id
    ).first()
    if existing_member:
        flash('User is already a member of this group.', 'warning')
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Check if they're friends - allow adding friends even without invitation acceptance
    is_friend = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user.id)) |
        ((Friendship.user_id == user.id) & (Friendship.friend_id == current_user.id))
    ).first()
    
    if is_friend:
        # Friend can be added directly
        new_member = GroupMember(
            group_id=group_id,
            user_id=user.id,
            role='member'
        )
        db.session.add(new_member)
        db.session.commit()
        flash(f'{user.name} (your friend) added to the group!', 'success')
    else:
        # Regular user addition
        new_member = GroupMember(
            group_id=group_id,
            user_id=user.id,
            role='member'
        )
        db.session.add(new_member)
        db.session.commit()
        flash(f'{user.name} added to the group!', 'success')
    
    return redirect(url_for('group_detail', group_id=group_id))

@app.route('/groups/<int:group_id>/remove-member/<int:member_id>', methods=['POST'])
@login_required
def remove_member(group_id, member_id):
    group = Group.query.get_or_404(group_id)
    
    # Check if user is admin
    current_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id,
        role='admin'
    ).first()
    if not current_member:
        flash('Only admins can remove members.', 'danger')
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Get the member to remove
    member_to_remove = GroupMember.query.filter_by(
        group_id=group_id,
        id=member_id
    ).first_or_404()
    
    # Prevent removing yourself if you're the only admin
    if member_to_remove.user_id == current_user.id:
        admin_count = GroupMember.query.filter_by(
            group_id=group_id,
            role='admin'
        ).count()
        if admin_count <= 1:
            flash('You cannot remove yourself as you are the only admin. Transfer admin rights first or delete the group.', 'warning')
            return redirect(url_for('group_detail', group_id=group_id))
    
    # Prevent removing the last admin (if trying to remove someone else)
    if member_to_remove.role == 'admin':
        admin_count = GroupMember.query.filter_by(
            group_id=group_id,
            role='admin'
        ).count()
        if admin_count <= 1:
            flash('Cannot remove the last admin of the group.', 'warning')
            return redirect(url_for('group_detail', group_id=group_id))
    
    # Get user info before deletion for flash message
    user_name = member_to_remove.user.name
    
    # Delete the member
    db.session.delete(member_to_remove)
    db.session.commit()
    
    flash(f'{user_name} has been removed from the group.', 'success')
    return redirect(url_for('group_detail', group_id=group_id))

@app.route('/groups/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Get current user's membership
    member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    
    if not member:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups'))
    
    # Prevent leaving if you're the only admin
    if member.role == 'admin':
        admin_count = GroupMember.query.filter_by(
            group_id=group_id,
            role='admin'
        ).count()
        if admin_count <= 1:
            flash('You cannot leave as you are the only admin. Transfer admin rights first or delete the group.', 'warning')
            return redirect(url_for('group_detail', group_id=group_id))
    
    # Remove membership
    db.session.delete(member)
    db.session.commit()
    
    flash(f'You have left {group.name}.', 'success')
    return redirect(url_for('groups'))

@app.route('/profile')
@login_required
def profile():
    # Get user's activity history
    # Recent group joins
    recent_groups = GroupMember.query.filter_by(user_id=current_user.id)\
        .order_by(GroupMember.joined_at.desc())\
        .limit(5)\
        .all()
    
    # Recent expenses created
    recent_expenses = Expense.query.filter_by(created_by=current_user.id)\
        .order_by(Expense.created_at.desc())\
        .limit(10)\
        .all()
    
    # Count statistics
    total_groups = GroupMember.query.filter_by(user_id=current_user.id).count()
    total_expenses = Expense.query.filter_by(created_by=current_user.id).count()
    total_friends = Friendship.query.filter(
        (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
    ).count()
    
    return render_template('profile.html',
                         recent_groups=recent_groups,
                         recent_expenses=recent_expenses,
                         total_groups=total_groups,
                         total_expenses=total_expenses,
                         total_friends=total_friends)

# Friends Routes
@app.route('/friends')
@login_required
def friends():
    # Get all friendships
    friendships = Friendship.query.filter(
        (Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)
    ).all()
    
    # Extract friend users (avoid duplicates since friendships are bidirectional)
    friend_users = []
    seen_friend_ids = set()  # Track unique friend IDs
    
    for friendship in friendships:
        # Get the friend ID (the one that's not current_user)
        friend_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
        
        # Only add if we haven't seen this friend before
        if friend_id not in seen_friend_ids:
            seen_friend_ids.add(friend_id)
            friend = friendship.friend if friendship.user_id == current_user.id else friendship.user
            friend_users.append(friend)
    
    # Calculate balances with each friend
    friend_balances = []
    for friend in friend_users:
        balance = get_friend_balance(current_user.id, friend.id)
        friend_balances.append({
            'friend': friend,
            'balance': balance
        })
    
    # Get pending invitations sent by user
    sent_invitations = Invitation.query.filter_by(
        invited_by=current_user.id,
        status='pending'
    ).all()
    
    return render_template('friends.html', 
                         friend_balances=friend_balances,
                         sent_invitations=sent_invitations)

@app.route('/friends/add', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = AddFriendForm()
    invite_form = InviteFriendForm()
    
    if form.validate_on_submit() and request.form.get('action') == 'add_existing':
        # Normalize email to lowercase
        email = form.email.data.lower().strip()
        
        # Add existing user as friend (case-insensitive lookup)
        friend = User.query.filter(func.lower(User.email) == email).first()
        
        if not friend:
            flash('User not found. Try inviting them!', 'warning')
            return redirect(url_for('add_friend'))
        
        if friend.id == current_user.id:
            flash('You cannot add yourself as a friend!', 'danger')
            return redirect(url_for('add_friend'))
        
        # Check if already friends
        existing = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend.id)) |
            ((Friendship.user_id == friend.id) & (Friendship.friend_id == current_user.id))
        ).first()
        
        if existing:
            flash(f'You are already friends with {friend.name}!', 'info')
            return redirect(url_for('friends'))
        
        # Create friendship (bidirectional)
        friendship1 = Friendship(user_id=current_user.id, friend_id=friend.id)
        friendship2 = Friendship(user_id=friend.id, friend_id=current_user.id)
        
        db.session.add(friendship1)
        db.session.add(friendship2)
        db.session.commit()
        
        flash(f'{friend.name} added as friend!', 'success')
        return redirect(url_for('friends'))
    
    if invite_form.validate_on_submit() and request.form.get('action') == 'invite':
        # Normalize email to lowercase
        email = invite_form.email.data.lower().strip()
        
        # Check if user already exists (case-insensitive)
        existing_user = User.query.filter(func.lower(User.email) == email).first()
        if existing_user:
            flash('This user is already registered. Add them as a friend instead!', 'info')
            return redirect(url_for('add_friend'))
        
        # Check if invitation already sent (case-insensitive)
        existing_invite = Invitation.query.filter(
            func.lower(Invitation.email) == email,
            Invitation.invited_by == current_user.id,
            Invitation.status == 'pending'
        ).first()
        
        if existing_invite:
            flash('Invitation already sent to this email!', 'info')
            return redirect(url_for('friends'))
        
        # Create invitation with lowercase email
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        invitation = Invitation(
            email=email,
            invited_by=current_user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(invitation)
        db.session.commit()
        
        # Generate invitation link
        invite_link = url_for('signup_invite', token=token, _external=True)
        
        flash(f'Invitation sent to {email}!', 'success')
        flash(f'Share this link: {invite_link}', 'info')
        
        return redirect(url_for('friends'))
    
    return render_template('add_friend.html', form=form, invite_form=invite_form)

@app.route('/signup/invite/<token>', methods=['GET', 'POST'])
def signup_invite(token):
    invitation = Invitation.query.filter_by(token=token).first()
    
    if not invitation:
        flash('Invalid invitation link.', 'danger')
        return redirect(url_for('signup'))
    
    if invitation.status != 'pending':
        flash('This invitation has already been used.', 'warning')
        return redirect(url_for('login'))
    
    if invitation.expires_at < datetime.utcnow():
        flash('This invitation has expired.', 'warning')
        return redirect(url_for('signup'))
    
    form = SignUpForm()
    form.email.data = invitation.email  # Email is already lowercase from invitation
    
    if form.validate_on_submit():
        # Normalize email to lowercase (should already be lowercase from invitation, but ensure it)
        email = form.email.data.lower().strip()
        
        # Check if user already exists (case-insensitive)
        existing_user = User.query.filter(func.lower(User.email) == email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user with lowercase email
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.flush()
        
        # Mark invitation as accepted
        invitation.status = 'accepted'
        
        # Create friendship with inviter
        inviter = User.query.get(invitation.invited_by)
        if inviter:
            friendship1 = Friendship(user_id=user.id, friend_id=inviter.id)
            friendship2 = Friendship(user_id=inviter.id, friend_id=user.id)
            db.session.add(friendship1)
            db.session.add(friendship2)
        
        db.session.commit()
        
        flash(f'Account created! You are now friends with {inviter.name}!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup_invite.html', form=form, invitation=invitation)

@app.route('/friends/<int:friend_id>')
@login_required
def friend_detail(friend_id):
    friend = User.query.get_or_404(friend_id)
    
    # Check if they are friends
    friendship = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
    ).first()
    
    if not friendship:
        flash('This user is not your friend.', 'danger')
        return redirect(url_for('friends'))
    
    # Get or create friend group
    friend_group = Group.query.filter(
        Group.is_friend_group == True,
        Group.members.any(GroupMember.user_id == current_user.id),
        Group.members.any(GroupMember.user_id == friend_id)
    ).first()
    
    if not friend_group:
        # Create a friend group
        friend_group = Group(
            name=f"{current_user.name} & {friend.name}",
            currency=current_user.default_currency,
            is_friend_group=True,
            created_by=current_user.id
        )
        db.session.add(friend_group)
        db.session.flush()
        
        member1 = GroupMember(group_id=friend_group.id, user_id=current_user.id, role='admin')
        member2 = GroupMember(group_id=friend_group.id, user_id=friend_id, role='admin')
        db.session.add(member1)
        db.session.add(member2)
        db.session.commit()
    
    # Get expenses
    expenses = Expense.query.filter_by(group_id=friend_group.id).order_by(Expense.date.desc()).all()
    
    # Calculate balance
    balance = get_friend_balance(current_user.id, friend_id)
    
    return render_template('friend_detail.html',
                         friend=friend,
                         friend_group=friend_group,
                         expenses=expenses,
                         balance=balance)

@app.route('/friends/<int:friend_id>/settle', methods=['GET', 'POST'])
@login_required
def settle_friend(friend_id):
    friend = User.query.get_or_404(friend_id)
    
    # Check if they are friends
    friendship = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
    ).first()
    
    if not friendship:
        flash('This user is not your friend.', 'danger')
        return redirect(url_for('friends'))
    
    # Get or create friend group
    friend_group = Group.query.filter(
        Group.is_friend_group == True,
        Group.members.any(GroupMember.user_id == current_user.id),
        Group.members.any(GroupMember.user_id == friend_id)
    ).first()
    
    if not friend_group:
        friend_group = Group(
            name=f"{current_user.name} & {friend.name}",
            currency=current_user.default_currency,
            is_friend_group=True,
            created_by=current_user.id
        )
        db.session.add(friend_group)
        db.session.flush()
        
        member1 = GroupMember(group_id=friend_group.id, user_id=current_user.id, role='admin')
        member2 = GroupMember(group_id=friend_group.id, user_id=friend_id, role='admin')
        db.session.add(member1)
        db.session.add(member2)
        db.session.commit()
    
    # Calculate current balance
    balance = get_friend_balance(current_user.id, friend_id)
    
    form = SettlementForm()
    
    # For friends, only 2 options
    form.from_user.choices = [(current_user.id, current_user.name), (friend_id, friend.name)]
    form.to_user.choices = [(current_user.id, current_user.name), (friend_id, friend.name)]
    
    # Pre-fill based on balance
    if balance < 0:  # Current user owes friend
        form.from_user.data = current_user.id
        form.to_user.data = friend_id
        form.amount.data = abs(balance)
    elif balance > 0:  # Friend owes current user
        form.from_user.data = friend_id
        form.to_user.data = current_user.id
        form.amount.data = balance
    
    if form.validate_on_submit():
        settlement = Settlement(
            group_id=friend_group.id,  # Link to friend group
            from_user=form.from_user.data,
            to_user=form.to_user.data,
            amount=form.amount.data,
            currency=friend_group.currency,
            payment_method=form.payment_method.data,
            status='completed'
        )
        db.session.add(settlement)
        db.session.commit()
        
        flash('Settlement recorded successfully!', 'success')
        return redirect(url_for('friend_detail', friend_id=friend_id))
    
    return render_template('settle_friend.html',
                         form=form,
                         friend=friend,
                         friend_group=friend_group,
                         balance=balance)

@app.route('/friends/<int:friend_id>/add-expense', methods=['GET', 'POST'])
@login_required
def add_friend_expense(friend_id):
    friend = User.query.get_or_404(friend_id)
    
    # Check friendship
    friendship = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user.id))
    ).first()
    
    if not friendship:
        flash('This user is not your friend.', 'danger')
        return redirect(url_for('friends'))
    
    # Get or create friend group
    friend_group = Group.query.filter(
        Group.is_friend_group == True,
        Group.members.any(GroupMember.user_id == current_user.id),
        Group.members.any(GroupMember.user_id == friend_id)
    ).first()
    
    if not friend_group:
        friend_group = Group(
            name=f"{current_user.name} & {friend.name}",
            currency=current_user.default_currency,
            is_friend_group=True,
            created_by=current_user.id
        )
        db.session.add(friend_group)
        db.session.flush()
        
        member1 = GroupMember(group_id=friend_group.id, user_id=current_user.id, role='admin')
        member2 = GroupMember(group_id=friend_group.id, user_id=friend_id, role='admin')
        db.session.add(member1)
        db.session.add(member2)
        db.session.commit()
    
    form = AddExpenseForm()
    form.paid_by.choices = [(current_user.id, current_user.name), (friend_id, friend.name)]
    form.participants.choices = [(current_user.id, current_user.name), (friend_id, friend.name)]
    
    # Pre-select both participants for friend expense
    form.participants.data = [current_user.id, friend_id]
    form.split_type.data = 'equal'  # Default to equal split
    form.user_percentage.data = 50.0
    form.friend_percentage.data = 50.0
    
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            currency=friend_group.currency,
            category=form.category.data,
            paid_by=form.paid_by.data,
            group_id=friend_group.id,
            split_type=form.split_type.data,
            date=form.date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(expense)
        db.session.flush()
        
        # Calculate shares based on split type
        if form.split_type.data == 'percentage':
            # Use percentage split
            user_percent = form.user_percentage.data / 100
            friend_percent = form.friend_percentage.data / 100
            user_share = round(expense.amount * user_percent, 2)
            friend_share = round(expense.amount * friend_percent, 2)
        else:
            # Equal split (default)
            share = expense.amount / 2
            user_share = round(share, 2)
            friend_share = round(share, 2)
        
        participant1 = ExpenseParticipant(expense_id=expense.id, user_id=current_user.id, share=user_share)
        participant2 = ExpenseParticipant(expense_id=expense.id, user_id=friend_id, share=friend_share)
        db.session.add(participant1)
        db.session.add(participant2)
        
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('friend_detail', friend_id=friend_id))
    
    return render_template('add_friend_expense.html', form=form, friend=friend)

# Profile Management Routes
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from forms import EditProfileForm
    form = EditProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if email is being changed and if it's available
        if form.email.data.lower() != current_user.email.lower():
            existing_user = User.query.filter(func.lower(User.email) == form.email.data.lower()).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Email already exists. Please choose another.', 'danger')
                return render_template('edit_profile.html', form=form)
        
        current_user.name = form.name.data
        current_user.email = form.email.data.lower()
        if form.phone.data:
            current_user.phone = form.phone.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', form=form)

@app.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    from forms import ChangePasswordForm
    from werkzeug.security import check_password_hash, generate_password_hash
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html', form=form)
        
        # Update password
        current_user.password = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html', form=form)

@app.route('/profile/export', methods=['GET', 'POST'])
@login_required
def export_data():
    from forms import ExportDataForm
    import csv
    import io
    from datetime import datetime
    
    form = ExportDataForm()
    
    if form.validate_on_submit():
        # Get expenses based on filters
        query = Expense.query.filter_by(created_by=current_user.id)
        
        # Apply date filter
        if form.date_from.data:
            query = query.filter(Expense.date >= form.date_from.data)
        if form.date_to.data:
            query = query.filter(Expense.date <= form.date_to.data)
        
        # Apply scope filter
        if form.scope.data == 'groups':
            query = query.filter(Expense.group_id.isnot(None), Expense.group.has(is_friend_group=False))
        elif form.scope.data == 'friends':
            query = query.filter(Expense.group_id.isnot(None), Expense.group.has(is_friend_group=True))
        
        expenses = query.order_by(Expense.date.desc()).all()
        
        if form.format.data == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Description', 'Amount', 'Currency', 'Category', 'Paid By', 'Group/Friend', 'Notes'])
            
            for expense in expenses:
                group_name = expense.group.name if expense.group else 'Direct Friend'
                writer.writerow([
                    expense.date.strftime('%Y-%m-%d'),
                    expense.description,
                    expense.amount,
                    expense.currency,
                    expense.category,
                    expense.payer.name,
                    group_name,
                    expense.notes or ''
                ])
            
            from flask import Response
            response = Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=expenses_{datetime.now().strftime("%Y%m%d")}.csv'}
            )
            return response
    
    return render_template('export_data.html', form=form)

@app.route('/profile/update-currency', methods=['POST'])
@login_required
def update_currency():
    currency = request.form.get('currency', 'USD')
    if currency in ['USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD']:
        current_user.default_currency = currency
        db.session.commit()
        flash('Currency updated successfully!', 'success')
    else:
        flash('Invalid currency selected.', 'danger')
    return redirect(url_for('profile'))

@app.route('/profile/update-theme', methods=['POST'])
@login_required
def update_theme():
    theme = request.form.get('theme', 'dark')
    if theme in ['dark', 'light', 'auto']:
        # Safely set theme_preference (handles missing column)
        if hasattr(current_user, 'theme_preference'):
            current_user.theme_preference = theme
        else:
            # If column doesn't exist, try to add it
            try:
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN theme_preference VARCHAR(10) DEFAULT 'dark'"))
                    conn.commit()
                # Refresh the user object
                db.session.refresh(current_user)
                current_user.theme_preference = theme
            except Exception as e:
                flash('Theme preference could not be saved. Please restart the app.', 'warning')
        db.session.commit()
        flash('Theme updated successfully!', 'success')
    else:
        flash('Invalid theme selected.', 'danger')
    return redirect(url_for('profile'))

@app.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_account():
    # Delete user account and all related data
    # Note: This is a destructive operation
    try:
        db.session.delete(current_user)
        db.session.commit()
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash('Error deleting account. Please contact support.', 'danger')
        return redirect(url_for('profile'))

# Personal Finance Routes (from spendings app)
@app.route('/personal-finance')
@login_required
def personal_finance_dashboard():
    """Main personal finance dashboard page"""
    return render_template('personal_finance_dashboard.html')

@app.route('/api/personal-finance/dashboard', methods=['GET'])
@login_required
def get_personal_finance_dashboard():
    """Get personal finance dashboard summary"""
    # Calculate dashboard metrics for current user
    total_income = db.session.query(func.sum(Income.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_expenses = db.session.query(func.sum(PersonalExpense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_savings = db.session.query(func.sum(Savings.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_debt = db.session.query(func.sum(Debt.current_balance)).filter_by(user_id=current_user.id, status='active').scalar() or 0
    total_debt_paid = db.session.query(func.sum(DebtPayment.amount)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Get recent transactions
    recent_income = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = PersonalExpense.query.filter_by(user_id=current_user.id).order_by(PersonalExpense.date.desc()).limit(5).all()
    
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
        'currency': current_user.default_currency or 'USD',
        'monthly_budget': current_user.monthly_budget or 0
    })

# Income endpoints
@app.route('/api/personal-finance/income', methods=['GET', 'POST'])
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

@app.route('/api/personal-finance/income/<int:id>', methods=['PUT', 'DELETE'])
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

# Personal Expense endpoints (renamed from /api/expenses to avoid conflict)
@app.route('/api/personal-expenses', methods=['GET', 'POST'])
@login_required
def handle_personal_expenses():
    if request.method == 'POST':
        data = request.json
        expense = PersonalExpense(
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
        expenses = PersonalExpense.query.filter_by(user_id=current_user.id).order_by(PersonalExpense.date.desc()).all()
        return jsonify([e.to_dict() for e in expenses])

@app.route('/api/personal-expenses/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def handle_personal_expense_item(id):
    expense = PersonalExpense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
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
@app.route('/api/personal-finance/debts', methods=['GET', 'POST'])
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

@app.route('/api/personal-finance/debts/<int:id>', methods=['PUT', 'DELETE'])
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
@app.route('/api/personal-finance/debt-payments', methods=['GET', 'POST'])
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
                debt.status = 'paid'
        
        db.session.commit()
        return jsonify(payment.to_dict()), 201
    else:
        payments = DebtPayment.query.filter_by(user_id=current_user.id).order_by(DebtPayment.date.desc()).all()
        return jsonify([p.to_dict() for p in payments])

# Savings endpoints
@app.route('/api/personal-finance/savings', methods=['GET', 'POST'])
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
        return jsonify([s.to_dict() for s in savings])

# Savings Goals endpoints
@app.route('/api/personal-finance/savings-goals', methods=['GET', 'POST'])
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
@app.route('/api/personal-finance/recurring-expenses', methods=['GET', 'POST'])
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
@app.route('/api/personal-finance/analytics/expenses-by-category', methods=['GET'])
@login_required
def expenses_by_category():
    results = db.session.query(
        PersonalExpense.category,
        func.sum(PersonalExpense.amount).label('total')
    ).filter_by(user_id=current_user.id).group_by(PersonalExpense.category).all()
    
    return jsonify([{'category': r[0], 'total': round(r[1], 2)} for r in results])

@app.route('/api/personal-finance/analytics/income-by-type', methods=['GET'])
@login_required
def income_by_type():
    results = db.session.query(
        Income.type,
        func.sum(Income.amount).label('total')
    ).filter_by(user_id=current_user.id).group_by(Income.type).all()
    
    return jsonify([{'type': r[0], 'total': round(r[1], 2)} for r in results])

@app.route('/api/personal-finance/analytics/monthly-summary', methods=['GET'])
@login_required
def monthly_summary():
    """Get monthly income and expense summary for current year"""
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
        func.strftime('%m', PersonalExpense.date).label('month'),
        func.sum(PersonalExpense.amount).label('total')
    ).filter(
        PersonalExpense.user_id == current_user.id,
        func.strftime('%Y', PersonalExpense.date) == str(current_year)
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
@app.route('/api/personal-finance/import-excel', methods=['POST'])
@login_required
def import_excel():
    """Import data from Excel file"""
    if not PANDAS_AVAILABLE:
        return jsonify({'success': False, 'error': 'Pandas library is not installed. Install it with: pip install pandas openpyxl'}), 400
    
    try:
        # Check if file exists
        excel_file = 'spendings/Master Sheet.xlsx'
        if not os.path.exists(excel_file):
            return jsonify({'success': False, 'error': 'Excel file not found'}), 400
        
        xls = pd.ExcelFile(excel_file)
        
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
                expense = PersonalExpense(
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
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Budget Settings Page
@app.route('/budget-settings')
@login_required
def budget_settings():
    """Budget settings page"""
    return render_template('budget_settings.html')

# Update User Settings (Currency & Budget)
@app.route('/api/personal-finance/user/settings', methods=['PUT'])
@login_required
def update_personal_finance_settings():
    """Update user currency and budget settings"""
    data = request.json
    if 'currency' in data:
        current_user.default_currency = data['currency']
    if 'monthly_budget' in data:
        current_user.monthly_budget = float(data['monthly_budget'])
    db.session.commit()
    return jsonify({'success': True})

# Get Budget Status
@app.route('/api/personal-finance/budget/status', methods=['GET'])
@login_required
def get_budget_status():
    """Get current month budget status"""
    # Get current month expenses
    today = datetime.utcnow()
    month_start = datetime(today.year, today.month, 1)
    
    month_expenses = db.session.query(func.sum(PersonalExpense.amount))\
        .filter(PersonalExpense.user_id == current_user.id)\
        .filter(PersonalExpense.date >= month_start)\
        .scalar() or 0
    
    budget = current_user.monthly_budget or 0
    percentage = (month_expenses / budget * 100) if budget > 0 else 0
    remaining = budget - month_expenses
    
    return jsonify({
        'budget': budget,
        'spent': round(month_expenses, 2),
        'remaining': round(remaining, 2),
        'percentage': round(percentage, 2),
        'currency': current_user.default_currency or 'USD',
        'status': 'over' if remaining < 0 else 'under'
    })

# Update view preference (separate/combined)
@app.route('/api/view-preference', methods=['PUT'])
@login_required
def update_view_preference():
    """Update user's view preference for expenses"""
    data = request.json
    if 'preference' in data and data['preference'] in ['separate', 'combined']:
        current_user.view_preference = data['preference']
        db.session.commit()
        return jsonify({'success': True, 'preference': current_user.view_preference})
    return jsonify({'success': False, 'error': 'Invalid preference'}), 400

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Allow access from mobile devices on same network
    # Get local IP address
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\n{'='*60}")
    print(f"🚀 Server starting...")
    print(f"📱 Access from phone: http://{local_ip}:5000")
    print(f"💻 Access from computer: http://localhost:5000")
    print(f"{'='*60}\n")
    
    # Run on all interfaces (0.0.0.0) to allow mobile access
    app.run(host='0.0.0.0', port=5000, debug=True)

