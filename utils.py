"""
Utility functions for balance calculations and debt simplification
"""

def calculate_balances(group):
    """
    Calculate individual balances for all group members based on expenses
    Returns a list of dictionaries with user_id, user_name, amount, and currency
    """
    balances = {}
    
    # Initialize all members with 0 balance
    for member in group.members:
        balances[member.user_id] = {
            'user_id': member.user_id,
            'user_name': member.user.name,
            'amount': 0.0,
            'currency': group.currency
        }
    
    # Calculate balances from expenses
    for expense in group.expenses:
        paid_by_id = expense.paid_by
        paid_amount = expense.amount
        
        # Add to payer's balance (they paid, so they're owed money - positive)
        if paid_by_id in balances:
            balances[paid_by_id]['amount'] += paid_amount
        
        # Subtract from each participant's balance (they owe - negative)
        for participant in expense.participants:
            user_id = participant.user_id
            if user_id in balances:
                balances[user_id]['amount'] -= participant.share
    
    # Subtract settlements
    for settlement in group.settlements:
        if settlement.status == 'completed':
            # Person who paid reduces their debt
            if settlement.from_user in balances:
                balances[settlement.from_user]['amount'] += settlement.amount
            # Person who received increases their debt (they were paid)
            if settlement.to_user in balances:
                balances[settlement.to_user]['amount'] -= settlement.amount
    
    # Round to 2 decimal places
    for balance in balances.values():
        balance['amount'] = round(balance['amount'], 2)
    
    return list(balances.values())

def simplify_debts(balances):
    """
    Simplify debts using minimum number of transactions
    Uses a greedy algorithm to minimize the number of settlements needed
    Returns a list of simplified debts with from_id, from_name, to_id, to_name, and amount
    """
    debts = []
    
    # Separate creditors (positive balance) and debtors (negative balance)
    creditors = []
    debtors = []
    
    for balance in balances:
        if balance['amount'] > 0.01:  # Owed money (creditor)
            creditors.append(balance.copy())
        elif balance['amount'] < -0.01:  # Owes money (debtor)
            debtors.append({
                'user_id': balance['user_id'],
                'user_name': balance['user_name'],
                'amount': abs(balance['amount']),
                'currency': balance['currency']
            })
    
    # Sort by amount (largest first)
    creditors.sort(key=lambda x: x['amount'], reverse=True)
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    
    creditor_idx = 0
    debtor_idx = 0
    
    while creditor_idx < len(creditors) and debtor_idx < len(debtors):
        creditor = creditors[creditor_idx]
        debtor = debtors[debtor_idx]
        
        if creditor['amount'] < 0.01:
            creditor_idx += 1
            continue
        if debtor['amount'] < 0.01:
            debtor_idx += 1
            continue
        
        settlement_amount = min(creditor['amount'], debtor['amount'])
        
        debts.append({
            'from_id': debtor['user_id'],
            'from_name': debtor['user_name'],
            'to_id': creditor['user_id'],
            'to_name': creditor['user_name'],
            'amount': round(settlement_amount, 2),
            'currency': creditor['currency']
        })
        
        creditor['amount'] -= settlement_amount
        debtor['amount'] -= settlement_amount
        
        if creditor['amount'] < 0.01:
            creditor_idx += 1
        if debtor['amount'] < 0.01:
            debtor_idx += 1
    
    return debts

def format_currency(amount, currency='USD'):
    """Format amount with currency symbol"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'CAD': 'C$',
        'AUD': 'A$'
    }
    symbol = symbols.get(currency, currency + ' ')
    return f"{symbol}{abs(amount):,.2f}"

def get_expense_summary(group):
    """Get summary statistics for a group"""
    total_spent = sum(expense.amount for expense in group.expenses)
    num_expenses = len(group.expenses)
    num_members = len(group.members)
    
    # Calculate category breakdown
    category_totals = {}
    for expense in group.expenses:
        category = expense.category
        if category in category_totals:
            category_totals[category] += expense.amount
        else:
            category_totals[category] = expense.amount
    
    return {
        'total_spent': total_spent,
        'num_expenses': num_expenses,
        'num_members': num_members,
        'category_breakdown': category_totals,
        'average_per_expense': total_spent / num_expenses if num_expenses > 0 else 0,
        'average_per_member': total_spent / num_members if num_members > 0 else 0
    }

def get_friend_balance(user1_id, user2_id):
    """
    Calculate balance between two friends
    Returns positive if user1 is owed by user2, negative if user1 owes user2
    """
    from models import Expense, ExpenseParticipant, Group, GroupMember, Settlement
    
    # Find friend group
    friend_group = Group.query.filter(
        Group.is_friend_group == True,
        Group.members.any(GroupMember.user_id == user1_id),
        Group.members.any(GroupMember.user_id == user2_id)
    ).first()
    
    if not friend_group:
        return 0.0
    
    balance = 0.0
    
    # Calculate from expenses
    for expense in friend_group.expenses:
        if expense.paid_by == user1_id:
            # user1 paid, so they are owed
            for participant in expense.participants:
                if participant.user_id == user2_id:
                    balance += participant.share
        elif expense.paid_by == user2_id:
            # user2 paid, so user1 owes
            for participant in expense.participants:
                if participant.user_id == user1_id:
                    balance -= participant.share
    
    # Subtract settlements
    settlements = Settlement.query.filter_by(group_id=friend_group.id, status='completed').all()
    for settlement in settlements:
        if settlement.from_user == user1_id and settlement.to_user == user2_id:
            # user1 paid user2
            balance -= settlement.amount
        elif settlement.from_user == user2_id and settlement.to_user == user1_id:
            # user2 paid user1
            balance += settlement.amount
    
    return round(balance, 2)

