"""
Database models for Expense Splitter application
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(200))
    default_currency = db.Column(db.String(3), default='USD')
    theme_preference = db.Column(db.String(10), default='dark', nullable=True)  # 'dark', 'light', 'auto'
    monthly_budget = db.Column(db.Float, default=0.0)
    view_preference = db.Column(db.String(20), default='separate')  # 'separate' or 'combined'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('GroupMember', back_populates='user', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', back_populates='payer', foreign_keys='Expense.paid_by')
    
    @property
    def theme(self):
        """Safe access to theme_preference with default."""
        return self.theme_preference if self.theme_preference else 'dark'
    
    def __repr__(self):
        return f'<User {self.email}>'

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    currency = db.Column(db.String(3), default='USD')
    cover_photo = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50))
    is_friend_group = db.Column(db.Boolean, default=False)  # True for 1-on-1 friend expenses
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = db.relationship('GroupMember', back_populates='group', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', back_populates='group', cascade='all, delete-orphan')
    settlements = db.relationship('Settlement', back_populates='group', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Group {self.name}>'

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'admin' or 'member'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    group = db.relationship('Group', back_populates='members')
    user = db.relationship('User', back_populates='memberships')
    
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='unique_group_user'),)
    
    def __repr__(self):
        return f'<GroupMember group={self.group_id} user={self.user_id}>'

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    category = db.Column(db.String(50), nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)  # Nullable for direct friend expenses
    split_type = db.Column(db.String(20), default='equal')  # 'equal', 'custom', 'percentage'
    receipt_image = db.Column(db.String(200))
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    group = db.relationship('Group', back_populates='expenses')
    payer = db.relationship('User', back_populates='expenses', foreign_keys=[paid_by])
    participants = db.relationship('ExpenseParticipant', back_populates='expense', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Expense {self.description} ${self.amount}>'

class ExpenseParticipant(db.Model):
    __tablename__ = 'expense_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    share = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    
    # Relationships
    expense = db.relationship('Expense', back_populates='participants')
    user = db.relationship('User')
    
    __table_args__ = (db.UniqueConstraint('expense_id', 'user_id', name='unique_expense_user'),)
    
    def __repr__(self):
        return f'<ExpenseParticipant expense={self.expense_id} user={self.user_id} share=${self.share}>'

class Settlement(db.Model):
    __tablename__ = 'settlements'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)  # Nullable for friend settlements
    from_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed'
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    receipt_image = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    group = db.relationship('Group', back_populates='settlements')
    payer = db.relationship('User', foreign_keys=[from_user])
    payee = db.relationship('User', foreign_keys=[to_user])
    
    def __repr__(self):
        return f'<Settlement {self.from_user} -> {self.to_user} ${self.amount}>'

class Friendship(db.Model):
    __tablename__ = 'friendships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    friend = db.relationship('User', foreign_keys=[friend_id])
    
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)
    
    def __repr__(self):
        return f'<Friendship {self.user_id} <-> {self.friend_id}>'

class Invitation(db.Model):
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'expired'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    inviter = db.relationship('User', foreign_keys=[invited_by])
    
    def __repr__(self):
        return f'<Invitation to {self.email}>'

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def is_valid(self):
        """Check if reset token is still valid."""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def __repr__(self):
        return f'<PasswordReset for user {self.user_id}>'

# Personal Finance Models (from spendings app)
class Income(db.Model):
    __tablename__ = 'income'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'main' or 'side'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'source': self.source,
            'amount': self.amount,
            'type': self.type,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Income {self.source} ${self.amount}>'

class PersonalExpense(db.Model):
    """Personal expense (renamed from Expense to avoid conflict with split Expense model)"""
    __tablename__ = 'personal_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<PersonalExpense {self.category} ${self.amount}>'

class Debt(db.Model):
    __tablename__ = 'debts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creditor = db.Column(db.String(100), nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    minimum_payment = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.Integer)  # Day of month (1-31)
    status = db.Column(db.String(50), default='active')  # 'active', 'paid', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    payments = db.relationship('DebtPayment', back_populates='debt', cascade='all, delete-orphan')
    
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
    
    def __repr__(self):
        return f'<Debt {self.creditor} ${self.current_balance}>'

class DebtPayment(db.Model):
    __tablename__ = 'debt_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    debt_id = db.Column(db.Integer, db.ForeignKey('debts.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    debt = db.relationship('Debt', back_populates='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'debt_id': self.debt_id,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<DebtPayment debt={self.debt_id} ${self.amount}>'

class Savings(db.Model):
    __tablename__ = 'savings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    goal_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'goal_name': self.goal_name,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Savings ${self.amount}>'

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')  # 'active', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
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
    
    def __repr__(self):
        return f'<SavingsGoal {self.name} ${self.current_amount}/${self.target_amount}>'

class RecurringExpense(db.Model):
    __tablename__ = 'recurring_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # 'weekly', 'bi-weekly', 'monthly'
    start_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'category': self.category,
            'active': self.active
        }
    
    def __repr__(self):
        return f'<RecurringExpense {self.name} ${self.amount} ({self.frequency})>'

