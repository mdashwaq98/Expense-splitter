"""
WTForms for Expense Splitter application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField, SelectField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    currency = SelectField('Currency', 
                          choices=[('USD', 'USD - US Dollar'),
                                  ('EUR', 'EUR - Euro'),
                                  ('GBP', 'GBP - British Pound'),
                                  ('INR', 'INR - Indian Rupee'),
                                  ('CAD', 'CAD - Canadian Dollar'),
                                  ('AUD', 'AUD - Australian Dollar')],
                          default='USD')
    submit = SubmitField('Create Group')

class AddExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category',
                          choices=[('Grocery', 'Grocery'),
                                  ('Transport', 'Transport'),
                                  ('Entertainment', 'Entertainment'),
                                  ('Food & Dining', 'Food & Dining'),
                                  ('Shopping', 'Shopping'),
                                  ('Utilities', 'Utilities'),
                                  ('Healthcare', 'Healthcare'),
                                  ('Other', 'Other')],
                          validators=[DataRequired()])
    paid_by = SelectField('Paid By', coerce=int, validators=[DataRequired()])
    participants = SelectMultipleField('Split Between', coerce=int, validators=[DataRequired()])
    split_type = SelectField('Split Type',
                            choices=[('equal', 'Split Equally'),
                                    ('percentage', 'Split by Percentage'),
                                    ('custom', 'Custom Split')],
                            default='equal')
    date = DateField('Date', default=datetime.utcnow, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    # Percentage fields for friend expenses (optional)
    user_percentage = FloatField('Your Share (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=50.0)
    friend_percentage = FloatField('Friend Share (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=50.0)
    submit = SubmitField('Add Expense')
    
    def validate_user_percentage(self, field):
        """Validate percentage when split type is percentage."""
        if self.split_type.data == 'percentage':
            if not field.data or field.data <= 0:
                raise ValidationError('Please enter a valid percentage for your share.')
    
    def validate_friend_percentage(self, field):
        """Validate percentage when split type is percentage."""
        if self.split_type.data == 'percentage':
            if not field.data or field.data <= 0:
                raise ValidationError('Please enter a valid percentage for friend\'s share.')
        
        # Validate total equals 100% when both are set
        if self.split_type.data == 'percentage' and self.user_percentage.data and field.data:
            total = self.user_percentage.data + field.data
            if abs(total - 100.0) > 0.01:
                raise ValidationError(f'Percentages must total 100% (currently {total:.2f}%).')

class SettlementForm(FlaskForm):
    from_user = SelectField('From', coerce=int, validators=[DataRequired()])
    to_user = SelectField('To', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_method = SelectField('Payment Method',
                                choices=[('Cash', 'Cash'),
                                        ('Bank Transfer', 'Bank Transfer'),
                                        ('PayPal', 'PayPal'),
                                        ('Venmo', 'Venmo'),
                                        ('Other', 'Other')],
                                default='Cash')
    submit = SubmitField('Record Settlement')
    
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if self.from_user.data == self.to_user.data:
            self.to_user.errors.append('Cannot settle with yourself!')
            return False
        return True

class AddFriendForm(FlaskForm):
    email = StringField('Friend\'s Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Add Friend')

class InviteFriendForm(FlaskForm):
    email = StringField('Email to Invite', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Invitation')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Length(max=20)])
    submit = SubmitField('Save Changes')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ExportDataForm(FlaskForm):
    format = SelectField('Export Format',
                        choices=[('csv', 'CSV'), ('pdf', 'PDF'), ('xls', 'Excel (XLS)')],
                        default='csv')
    date_from = DateField('From Date')
    date_to = DateField('To Date')
    scope = SelectField('Export Scope',
                       choices=[('all', 'All Expenses'),
                               ('groups', 'Groups Only'),
                               ('friends', 'Friends Only')],
                       default='all')
    submit = SubmitField('Export Data')

