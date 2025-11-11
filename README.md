# Expense Splitter

A beautiful and intuitive mobile app for tracking and splitting expenses with friends and groups.

## Features

### ✅ Authentication
- **User Registration**: Create a new account with name, email, and password
- **Login System**: Secure login with email and password
- **Profile Management**: Edit your profile information
- **Persistent Sessions**: Stay logged in across app restarts

### 💰 Expense Tracking
- **Add Expenses**: Track expenses with description, amount, and optional group assignment
- **View All Expenses**: See a complete list of all your expenses
- **Total Tracking**: Automatically calculated total expenses
- **Delete Expenses**: Long-press to remove expenses

### 👥 Group Management
- **Create Groups**: Organize expenses by creating groups (e.g., "Roommates", "Vacation Trip")
- **Group Overview**: View all your groups with member counts
- **Group Balances**: See how much you owe or are owed in each group
- **Delete Groups**: Long-press to remove groups

### 📊 Profile & Statistics
- **Personal Dashboard**: View your expense statistics
- **Balance Overview**: See your overall balance across all groups
- **Account Management**: Edit profile, access settings
- **Activity Summary**: Track total expenses and group memberships

### 💎 User Experience
- **Beautiful UI**: Modern, clean design with intuitive navigation
- **Bottom Tab Navigation**: Easy access to Expenses, Groups, and Profile
- **Color-Coded Sections**: Different colors for each main section
- **Responsive Design**: Works on all screen sizes
- **Data Persistence**: All data stored locally using AsyncStorage

## Tech Stack

- **React Native** with Expo
- **React Navigation** for navigation (Stack & Bottom Tabs)
- **AsyncStorage** for local data persistence
- **Context API** for state management

## Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start the Development Server**
   ```bash
   npm start
   ```

3. **Run on Device/Emulator**
   - Press `a` for Android
   - Press `i` for iOS
   - Scan QR code with Expo Go app

## Usage

### First Time Setup
1. Launch the app
2. Tap "Sign up" to create a new account
3. Fill in your name, email, and password
4. You'll be automatically logged in

### Adding Expenses
1. Go to the "Expenses" tab
2. Tap the "+" button
3. Enter expense description and amount
4. Optionally assign to a group
5. Tap "Add"

### Creating Groups
1. Go to the "Groups" tab
2. Tap the "+" button
3. Enter a group name
4. Tap "Create"

### Managing Profile
1. Go to the "Profile" tab
2. View your statistics and balance
3. Tap "Edit Profile" to update your information
4. Tap "Logout" when you're done

## Project Structure

```
expense-splitter/
├── App.js                          # Main app entry point with navigation
├── src/
│   ├── context/
│   │   ├── AuthContext.js          # Authentication state management
│   │   └── ExpenseContext.js       # Expense & group state management
│   └── screens/
│       ├── LoginScreen.js          # Login screen
│       ├── SignupScreen.js         # Registration screen
│       ├── HomeScreen.js           # Expenses tab (main screen)
│       ├── GroupsScreen.js         # Groups tab
│       └── ProfileScreen.js        # Profile tab
├── assets/                         # App icons and images
├── package.json
├── app.json                        # Expo configuration
└── babel.config.js

```

## Features Breakdown

### Authentication System
- Secure user registration and login
- Password validation (minimum 6 characters)
- Email validation and duplicate checking
- Automatic session management
- Local storage of user credentials

### Expense Management
- Create, view, and delete expenses
- Link expenses to groups
- Track who paid for each expense
- Automatic date tracking
- Currency formatting

### Group Features
- Create unlimited groups
- View group members
- Calculate balances per group
- Track overall balance across all groups
- Visual balance indicators (green for owed, red for owing)

### Profile Features
- Editable user information
- Statistics dashboard
- Overall balance calculation
- Settings and support options
- Logout functionality

## Data Storage

All data is stored locally on the device using AsyncStorage:
- User credentials and session
- Personal expenses
- Group information
- Profile data

**Note**: In a production app, you would want to:
- Use a backend API for data synchronization
- Implement proper password hashing
- Add user authentication tokens
- Enable cloud backup

## Future Enhancements

- [ ] Add members to groups by email
- [ ] Split expenses between multiple people
- [ ] Calculate who owes whom
- [ ] Payment settlements
- [ ] Expense categories and filtering
- [ ] Search functionality
- [ ] Export expenses to CSV
- [ ] Push notifications
- [ ] Dark mode
- [ ] Multiple currencies

## Known Limitations

- Data is stored locally only (no cloud sync)
- Limited to single-device usage
- No real-time collaboration
- Basic expense splitting (equal splits only)

## Troubleshooting

### App won't start
- Make sure you've run `npm install`
- Check that you have Expo CLI installed: `npm install -g expo-cli`
- Clear cache: `expo start -c`

### Login/Signup issues
- Check that all fields are filled in
- Password must be at least 6 characters
- Email must be unique for signup

### Data not persisting
- Check that AsyncStorage has proper permissions
- Try clearing app data and re-logging in

## License

MIT License - feel free to use this app for personal or commercial projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using React Native and Expo**
