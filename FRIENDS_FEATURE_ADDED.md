# Friends Feature Added! 🎉

I've added the Splitwise-style friend expenses and invitation system you requested!

## New Features

### 1. **Direct Friend Expenses** (Like Splitwise!)
- ✅ Add expenses directly between 2 users without creating a group
- ✅ Track balances with each friend individually
- ✅ Automatically split expenses 50/50
- ✅ View expense history with each friend

### 2. **Friend Invitation System**
- ✅ Invite unregistered users via email
- ✅ Generate unique invitation links
- ✅ Auto-friend when they sign up
- ✅ Track pending invitations
- ✅ Add existing users as friends

## How to Use

### Adding a Friend

**Option 1: Add Existing User**
1. Click "Friends" in navigation
2. Click "Add Friend"
3. Enter their email (they must be registered)
4. Click "Add Friend"

**Option 2: Invite New User**
1. Click "Friends" in navigation
2. Click "Add Friend"
3. Go to "Invite Someone New" section
4. Enter their email
5. Click "Send Invitation"
6. Share the generated link with them
7. When they sign up, you'll automatically become friends!

### Adding an Expense with a Friend

1. Go to "Friends" page
2. Click on a friend's card
3. Click "Add Expense"
4. Fill in details (description, amount, category, who paid)
5. The expense is automatically split 50/50
6. Done!

### Viewing Balances

- **Friends Page**: See balance summary for each friend
- **Friend Detail Page**: See complete expense history
- **Green Balance**: Friend owes you
- **Red Balance**: You owe friend
- **Gray Balance**: All settled up!

## What Changed

### New Database Models
- `Friendship` - Stores friend relationships
- `Invitation` - Stores invitation tokens and status
- Updated `Group` - Added `is_friend_group` flag
- Updated `Expense` - Made `group_id` optional

### New Routes
- `/friends` - View all friends
- `/friends/add` - Add friend or send invitation
- `/friends/<id>` - View friend detail and expenses
- `/friends/<id>/add-expense` - Add expense with friend
- `/signup/invite/<token>` - Sign up via invitation link

### New Templates
- `friends.html` - Friends list page
- `add_friend.html` - Add friend/invite page
- `friend_detail.html` - Friend detail with expenses
- `add_friend_expense.html` - Add expense form
- `signup_invite.html` - Invitation signup page

### Updated Templates
- `base.html` - Added "Friends" to navigation

## Database Migration Needed

Since you've already run the app, you need to update the database:

### Option 1: Reset Database (LOSES ALL DATA)
```bash
# Delete the old database
del expense_splitter.db

# Run the app (it will create new tables)
python app.py
```

### Option 2: Keep Data (Manual)
If you have important data, you'll need to:
1. Use Flask-Migrate (not included yet)
2. Or manually add columns using SQL

For now, Option 1 is easiest since you're testing.

## Example Usage Scenario

**Alice wants to split expenses with Bob:**

1. **Alice adds Bob as friend:**
   - If Bob has account: Enter bob@email.com → Instant friends
   - If Bob doesn't have account: Send invitation → Bob signs up → Auto-friends

2. **Alice adds an expense:**
   - "Lunch at Café" - $30
   - Paid by: Alice
   - Auto-split: $15 each
   - Balance: Bob owes Alice $15

3. **Bob adds an expense:**
   - "Movie tickets" - $24
   - Paid by: Bob
   - Auto-split: $12 each
   - Balance: Alice owes Bob $12 (net: Bob owes Alice $3)

4. **View on Friends page:**
   - Shows net balance: Bob owes Alice $3
   - Click to see all expenses together

## Features Still Available

✅ Groups (for 3+ people)  
✅ Friends (for 1-on-1 expenses)  
✅ Dashboard with overall balances  
✅ Multiple currencies  
✅ Expense categories  
✅ Settlement tracking  

## Next Steps

1. **Delete the old database**:
   ```bash
   del expense_splitter.db
   ```

2. **Run the app**:
   ```bash
   python app.py
   ```

3. **Test it out**:
   - Sign up with 2 test accounts
   - Add each other as friends
   - Add some expenses
   - See the balances!

## Screenshots (What You'll See)

### Friends Page
- Cards for each friend
- Shows balance (green/red/gray)
- Quick actions: View Details, Add Expense

### Add Friend Page
- Two options: Add existing or Invite new
- Simple email input
- Generates shareable invitation link

### Friend Detail Page
- Shows net balance at top
- Complete expense history
- Add expense button

### Add Expense with Friend
- Simple form
- Auto-splits 50/50
- Choose who paid

## Technical Details

- **Friendships are bidirectional**: When Alice adds Bob, both can see each other
- **Friend groups are auto-created**: Hidden from main groups list
- **Invitations expire after 7 days**: Configurable in code
- **Balances calculated in real-time**: No caching

## Comparison: Friends vs Groups

| Feature | Friends | Groups |
|---------|---------|--------|
| Number of people | Exactly 2 | 2 or more |
| Split method | Always 50/50 | Equal or custom |
| Creation | Auto-created | Manual |
| Visibility | Hidden | Shown in groups list |
| Use case | Regular 1-on-1 expenses | Trips, roommates, events |

## Future Enhancements (Ideas)

- [ ] Custom split percentages for friends
- [ ] Settle up between friends
- [ ] Friend request system (instead of direct add)
- [ ] Email notifications for invitations
- [ ] Friend activity feed
- [ ] Export friend expenses to PDF

Enjoy the new features! This makes it much more like Splitwise now. 🎊

