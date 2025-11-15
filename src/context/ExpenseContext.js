import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthContext } from './AuthContext';

export const ExpenseContext = createContext();

export const ExpenseProvider = ({ children }) => {
  const { user } = useContext(AuthContext);
  const [expenses, setExpenses] = useState([]);
  const [groups, setGroups] = useState([]);
  const [settlements, setSettlements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      const expensesData = await AsyncStorage.getItem(`expenses_${user.id}`);
      const groupsData = await AsyncStorage.getItem(`groups_${user.id}`);
      const settlementsData = await AsyncStorage.getItem(`settlements_${user.id}`);

      if (expensesData) setExpenses(JSON.parse(expensesData));
      if (groupsData) setGroups(JSON.parse(groupsData));
      if (settlementsData) setSettlements(JSON.parse(settlementsData));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveExpenses = async (newExpenses) => {
    try {
      await AsyncStorage.setItem(`expenses_${user.id}`, JSON.stringify(newExpenses));
      setExpenses(newExpenses);
    } catch (error) {
      console.error('Error saving expenses:', error);
    }
  };

  const saveGroups = async (newGroups) => {
    try {
      await AsyncStorage.setItem(`groups_${user.id}`, JSON.stringify(newGroups));
      setGroups(newGroups);
    } catch (error) {
      console.error('Error saving groups:', error);
    }
  };

  const saveSettlements = async (newSettlements) => {
    try {
      await AsyncStorage.setItem(`settlements_${user.id}`, JSON.stringify(newSettlements));
      setSettlements(newSettlements);
    } catch (error) {
      console.error('Error saving settlements:', error);
    }
  };

  const addExpense = async (expense) => {
    // If expense is for a group, use group's currency
    let currency = expense.currency || 'USD';
    if (expense.groupId) {
      const group = groups.find(g => g.id === expense.groupId);
      if (group) currency = group.currency || 'USD';
    }
    
    const newExpense = {
      id: Date.now().toString(),
      ...expense,
      currency,
      createdBy: user.id,
      createdAt: new Date().toISOString(),
    };
    const updatedExpenses = [...expenses, newExpense];
    await saveExpenses(updatedExpenses);
    return newExpense;
  };

  const updateExpense = async (expenseId, updates) => {
    const updatedExpenses = expenses.map(exp =>
      exp.id === expenseId ? { ...exp, ...updates } : exp
    );
    await saveExpenses(updatedExpenses);
  };

  const deleteExpense = async (expenseId) => {
    const updatedExpenses = expenses.filter(exp => exp.id !== expenseId);
    await saveExpenses(updatedExpenses);
  };

  const addGroup = async (group) => {
    const newGroup = {
      id: Date.now().toString(),
      ...group,
      currency: group.currency || 'USD',
      createdBy: user.id,
      createdAt: new Date().toISOString(),
      description: group.description || '',
      category: group.category || 'General',
      members: [
        {
          userId: user.id,
          name: user.name,
          role: 'admin',
          joinedAt: new Date().toISOString(),
        },
        ...(group.members || [])
      ],
    };
    const updatedGroups = [...groups, newGroup];
    await saveGroups(updatedGroups);
    return newGroup;
  };

  const updateGroup = async (groupId, updates) => {
    const updatedGroups = groups.map(grp =>
      grp.id === groupId ? { ...grp, ...updates } : grp
    );
    await saveGroups(updatedGroups);
  };

  const deleteGroup = async (groupId) => {
    const updatedGroups = groups.filter(grp => grp.id !== groupId);
    await saveGroups(updatedGroups);
  };

  const addSettlement = async (settlement) => {
    const newSettlement = {
      id: Date.now().toString(),
      ...settlement,
      recordedBy: user.id,
      createdAt: new Date().toISOString(),
      status: 'completed',
    };
    const updatedSettlements = [...settlements, newSettlement];
    await saveSettlements(updatedSettlements);
    return newSettlement;
  };

  const deleteSettlement = async (settlementId) => {
    const updatedSettlements = settlements.filter(s => s.id !== settlementId);
    await saveSettlements(updatedSettlements);
  };

  // Member management functions
  const addMemberToGroup = async (groupId, memberName) => {
    const group = groups.find(g => g.id === groupId);
    if (!group) return;

    const newMember = {
      userId: `member_${Date.now()}`, // In real app, would be actual user ID
      name: memberName,
      role: 'member',
      joinedAt: new Date().toISOString(),
    };

    const updatedGroups = groups.map(g => 
      g.id === groupId 
        ? { ...g, members: [...(g.members || []), newMember] }
        : g
    );
    await saveGroups(updatedGroups);
  };

  const removeMemberFromGroup = async (groupId, userId) => {
    const updatedGroups = groups.map(g => 
      g.id === groupId 
        ? { ...g, members: (g.members || []).filter(m => m.userId !== userId) }
        : g
    );
    await saveGroups(updatedGroups);
  };

  const updateMemberRole = async (groupId, userId, newRole) => {
    const updatedGroups = groups.map(g => 
      g.id === groupId 
        ? {
            ...g,
            members: (g.members || []).map(m => 
              m.userId === userId ? { ...m, role: newRole } : m
            )
          }
        : g
    );
    await saveGroups(updatedGroups);
  };

  const calculateBalances = (groupId = null) => {
    const relevantExpenses = groupId
      ? expenses.filter(exp => exp.groupId === groupId)
      : expenses;

    const balances = {};

    relevantExpenses.forEach(expense => {
      const { paidBy, amount, splitBetween = [] } = expense;
      const splitAmount = amount / (splitBetween.length || 1);

      // Person who paid gets credited
      balances[paidBy] = (balances[paidBy] || 0) + amount;

      // Each person in split gets debited
      splitBetween.forEach(personId => {
        balances[personId] = (balances[personId] || 0) - splitAmount;
      });
    });

    // Subtract settlements
    const relevantSettlements = groupId
      ? settlements.filter(s => s.groupId === groupId && s.status === 'completed')
      : settlements.filter(s => s.status === 'completed');

    relevantSettlements.forEach(settlement => {
      const { fromUser, toUser, amount } = settlement;
      // Person who paid reduces their debt (they paid someone)
      balances[fromUser] = (balances[fromUser] || 0) + amount;
      // Person who received payment reduces what they're owed
      balances[toUser] = (balances[toUser] || 0) - amount;
    });

    return balances;
  };

  // Debt Simplification Algorithm - minimizes number of transactions
  const simplifyDebts = (groupId = null) => {
    const balances = calculateBalances(groupId);
    
    // Separate creditors (positive balance) and debtors (negative balance)
    const creditors = [];
    const debtors = [];
    
    Object.entries(balances).forEach(([userId, balance]) => {
      if (balance > 0.01) {
        creditors.push({ userId, amount: balance });
      } else if (balance < -0.01) {
        debtors.push({ userId, amount: Math.abs(balance) });
      }
    });
    
    // Sort by amount (largest first) for greedy algorithm
    creditors.sort((a, b) => b.amount - a.amount);
    debtors.sort((a, b) => b.amount - a.amount);
    
    const settlements = [];
    let creditorIdx = 0;
    let debtorIdx = 0;
    
    while (creditorIdx < creditors.length && debtorIdx < debtors.length) {
      const creditor = creditors[creditorIdx];
      const debtor = debtors[debtorIdx];
      
      if (creditor.amount < 0.01) {
        creditorIdx++;
        continue;
      }
      if (debtor.amount < 0.01) {
        debtorIdx++;
        continue;
      }
      
      const settlementAmount = Math.min(creditor.amount, debtor.amount);
      
      settlements.push({
        from: debtor.userId,
        to: creditor.userId,
        amount: Math.round(settlementAmount * 100) / 100,
      });
      
      creditor.amount -= settlementAmount;
      debtor.amount -= settlementAmount;
      
      if (creditor.amount < 0.01) creditorIdx++;
      if (debtor.amount < 0.01) debtorIdx++;
    }
    
    return settlements;
  };

  // Helper function to get currency symbol
  const getCurrencySymbol = (currency = 'USD') => {
    const symbols = {
      'USD': '$',
      'EUR': '€',
      'GBP': '£',
      'INR': '₹',
      'CAD': 'C$',
      'AUD': 'A$',
      'JPY': '¥',
      'CNY': '¥',
    };
    return symbols[currency] || currency + ' ';
  };

  return (
    <ExpenseContext.Provider
      value={{
        expenses,
        groups,
        settlements,
        loading,
        addExpense,
        updateExpense,
        deleteExpense,
        addGroup,
        updateGroup,
        deleteGroup,
        addSettlement,
        deleteSettlement,
        addMemberToGroup,
        removeMemberFromGroup,
        updateMemberRole,
        calculateBalances,
        simplifyDebts,
        getCurrencySymbol,
      }}
    >
      {children}
    </ExpenseContext.Provider>
  );
};
