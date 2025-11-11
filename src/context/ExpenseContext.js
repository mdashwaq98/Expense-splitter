import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthContext } from './AuthContext';

export const ExpenseContext = createContext();

export const ExpenseProvider = ({ children }) => {
  const { user } = useContext(AuthContext);
  const [expenses, setExpenses] = useState([]);
  const [groups, setGroups] = useState([]);
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

      if (expensesData) setExpenses(JSON.parse(expensesData));
      if (groupsData) setGroups(JSON.parse(groupsData));
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

  const addExpense = async (expense) => {
    const newExpense = {
      id: Date.now().toString(),
      ...expense,
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
      createdBy: user.id,
      createdAt: new Date().toISOString(),
      members: [user.id, ...(group.members || [])],
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

    return balances;
  };

  return (
    <ExpenseContext.Provider
      value={{
        expenses,
        groups,
        loading,
        addExpense,
        updateExpense,
        deleteExpense,
        addGroup,
        updateGroup,
        deleteGroup,
        calculateBalances,
      }}
    >
      {children}
    </ExpenseContext.Provider>
  );
};
