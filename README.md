# Spending Tracker - Financial Management App

A comprehensive web-based financial management application to track income, expenses, debt, and savings goals.

## Features

### 📊 Dashboard
- Real-time financial overview
- Summary cards for income, expenses, debt, and savings
- Interactive charts and visualizations
- Recent transaction history

### 💰 Income Management
- Track main income and side income
- Multiple income sources
- Date-based tracking
- Notes and categorization

### 💳 Expense Tracking
- Category-based expense tracking
- Visual expense breakdown
- Detailed transaction history
- Custom notes per expense

### 🏦 Debt Management
- Track multiple debts
- Interest rate tracking
- Payment history
- Progress visualization
- Debt payoff calculator

### 🎯 Savings Goals
- Create multiple savings goals
- Track progress with visual indicators
- Deadline management
- Goal completion tracking

### 🔄 Recurring Expenses
- Manage recurring bills
- Frequency tracking (weekly, bi-weekly, monthly)
- Category organization
- Automatic reminders

### 📈 Analytics
- Monthly income vs expenses comparison
- Expense breakdown by category
- Income source analysis
- Debt overview and progress

### 📥 Data Import
- Import existing data from Excel
- Seamless integration with Master Sheet.xlsx

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### First Time Setup
1. Start the application
2. The database will be created automatically
3. Click "Import from Excel" to load existing data (if you have Master Sheet.xlsx)
4. Start adding your financial transactions

### Adding Income
1. Navigate to the "Income" tab
2. Click "+ Add Income"
3. Fill in the details (date, source, type, amount)
4. Submit to save

### Recording Expenses
1. Go to the "Expenses" tab
2. Click "+ Add Expense"
3. Select category and enter amount
4. Add optional description and notes

### Managing Debt
1. Open the "Debt" tab
2. Click "+ Add Debt" to register a debt
3. Record payments as you make them
4. Track your progress with visual indicators

### Setting Savings Goals
1. Visit the "Savings" tab
2. Click "+ Add Goal" to create a new goal
3. Set target amount and deadline
4. Add savings contributions regularly

### Recurring Expenses
1. Go to "Recurring" tab
2. Add bills that repeat (car loan, insurance, etc.)
3. Set frequency and amount
4. Track all recurring expenses in one place

## Data Structure

### Database Tables
- **Income**: Tracks all income sources
- **Expense**: Records all expenses
- **Debt**: Manages debt accounts
- **DebtPayment**: Tracks debt payments
- **Savings**: Records savings contributions
- **SavingsGoal**: Manages savings goals
- **RecurringExpense**: Tracks recurring bills

### Excel Import
The app can import data from your existing Excel file with sheets:
- Main: Primary financial data
- Side Income: Additional income sources
- ManualExpenses: Expense entries
- And more...

## API Endpoints

### Dashboard
- `GET /api/dashboard` - Get dashboard summary

### Income
- `GET /api/income` - List all income
- `POST /api/income` - Add new income
- `PUT /api/income/<id>` - Update income
- `DELETE /api/income/<id>` - Delete income

### Expenses
- `GET /api/expenses` - List all expenses
- `POST /api/expenses` - Add new expense
- `PUT /api/expenses/<id>` - Update expense
- `DELETE /api/expenses/<id>` - Delete expense

### Debts
- `GET /api/debts` - List all debts
- `POST /api/debts` - Add new debt
- `PUT /api/debts/<id>` - Update debt
- `DELETE /api/debts/<id>` - Delete debt

### Debt Payments
- `GET /api/debt-payments` - List all payments
- `POST /api/debt-payments` - Record payment

### Savings
- `GET /api/savings` - List all savings
- `POST /api/savings` - Add savings
- `GET /api/savings-goals` - List savings goals
- `POST /api/savings-goals` - Create goal

### Recurring Expenses
- `GET /api/recurring-expenses` - List recurring expenses
- `POST /api/recurring-expenses` - Add recurring expense

### Analytics
- `GET /api/analytics/expenses-by-category` - Expense breakdown
- `GET /api/analytics/income-by-type` - Income analysis
- `GET /api/analytics/monthly-summary` - Monthly trends

## Technologies Used

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database
- **Pandas** - Data processing

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern design
- **JavaScript** - Interactivity
- **Chart.js** - Data visualization

## Features Highlights

✅ Beautiful, modern UI with responsive design
✅ Real-time data updates
✅ Interactive charts and graphs
✅ Easy-to-use interface
✅ Comprehensive financial tracking
✅ Data import from Excel
✅ Mobile-friendly responsive design
✅ No authentication required (local use)

## Development

### Project Structure
```
spendings/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── spendings.db           # SQLite database (auto-created)
├── Master Sheet.xlsx      # Excel data source
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── style.css          # Styles
    └── app.js             # Frontend JavaScript
```

## Future Enhancements

- [ ] Export data to Excel/CSV
- [ ] Email reminders for bills
- [ ] Budget planning tools
- [ ] Expense forecasting
- [ ] Multi-user support
- [ ] Cloud backup
- [ ] Mobile app version
- [ ] Receipt scanning
- [ ] Category customization

## License

This project is for personal use.

## Support

For issues or questions, please refer to the code comments or modify as needed for your use case.

---

Built with ❤️ for better financial management

