import React, { useContext, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Modal,
  TextInput,
  ScrollView,
} from 'react-native';
import { ExpenseContext } from '../context/ExpenseContext';
import { AuthContext } from '../context/AuthContext';

// Expense categories with icons
const EXPENSE_CATEGORIES = [
  { value: 'Food', label: 'Food', icon: '🍔', color: '#FF6B6B' },
  { value: 'Transport', label: 'Transport', icon: '🚗', color: '#4ECDC4' },
  { value: 'Entertainment', label: 'Entertainment', icon: '🎬', color: '#95E1D3' },
  { value: 'Utilities', label: 'Utilities', icon: '💡', color: '#F38181' },
  { value: 'Shopping', label: 'Shopping', icon: '🛍️', color: '#AA96DA' },
  { value: 'Travel', label: 'Travel', icon: '✈️', color: '#FCBAD3' },
  { value: 'Health', label: 'Health', icon: '💊', color: '#A8E6CF' },
  { value: 'Other', label: 'Other', icon: '📝', color: '#FFD3B6' },
];

export default function HomeScreen() {
  const { expenses, addExpense, deleteExpense, groups, getCurrencySymbol } = useContext(ExpenseContext);
  const { user } = useContext(AuthContext);
  const [modalVisible, setModalVisible] = useState(false);
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('Other');
  const [splitType, setSplitType] = useState('equal');

  const handleAddExpense = async () => {
    if (!description || !amount) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    const expense = {
      description: description.trim(),
      amount: parseFloat(amount),
      category: selectedCategory,
      splitType: splitType,
      paidBy: user.id,
      paidByName: user.name,
      groupId: selectedGroup,
      splitBetween: [user.id],
    };

    await addExpense(expense);
    setDescription('');
    setAmount('');
    setSelectedGroup(null);
    setSelectedCategory('Other');
    setSplitType('equal');
    setModalVisible(false);
    Alert.alert('Success', 'Expense added successfully');
  };

  const handleDeleteExpense = (expenseId) => {
    Alert.alert(
      'Delete Expense',
      'Are you sure you want to delete this expense?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteExpense(expenseId),
        },
      ]
    );
  };

  const getCategoryInfo = (categoryValue) => {
    return EXPENSE_CATEGORIES.find(cat => cat.value === categoryValue) || EXPENSE_CATEGORIES[7];
  };

  const renderExpense = ({ item }) => {
    const categoryInfo = getCategoryInfo(item.category);
    return (
    <TouchableOpacity
      style={styles.expenseCard}
      onLongPress={() => handleDeleteExpense(item.id)}
    >
      <View style={styles.expenseHeader}>
        <View style={styles.expenseHeaderLeft}>
          <View style={[styles.categoryBadge, { backgroundColor: categoryInfo.color }]}>
            <Text style={styles.categoryIcon}>{categoryInfo.icon}</Text>
          </View>
          <View style={styles.expenseInfo}>
            <Text style={styles.expenseDescription}>{item.description}</Text>
            <View style={styles.expenseMetadata}>
              <Text style={styles.categoryLabel}>{categoryInfo.label}</Text>
              {item.splitType && item.splitType !== 'equal' && (
                <Text style={styles.splitBadge}>• {item.splitType}</Text>
              )}
            </View>
          </View>
        </View>
        <Text style={styles.expenseAmount}>
          {getCurrencySymbol(item.currency)}{item.amount.toFixed(2)}
        </Text>
      </View>
      <View style={styles.expenseFooter}>
        <Text style={styles.expenseDetail}>Paid by: {item.paidByName}</Text>
        <Text style={styles.expenseDate}>
          {new Date(item.createdAt).toLocaleDateString()}
        </Text>
      </View>
      {item.groupId && (
        <Text style={styles.expenseGroup}>
          Group: {groups.find(g => g.id === item.groupId)?.name || 'Unknown'}
        </Text>
      )}
    </TouchableOpacity>
    );
  };

  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Expenses</Text>
        <View style={styles.totalCard}>
          <Text style={styles.totalLabel}>Total Expenses</Text>
          <Text style={styles.totalAmount}>
            {getCurrencySymbol('USD')}{totalExpenses.toFixed(2)}
          </Text>
        </View>
      </View>

      <FlatList
        data={expenses}
        renderItem={renderExpense}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No expenses yet</Text>
            <Text style={styles.emptySubtext}>
              Tap the + button to add your first expense
            </Text>
          </View>
        }
      />

      <TouchableOpacity
        style={styles.fab}
        onPress={() => setModalVisible(true)}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add Expense</Text>

            <TextInput
              style={styles.input}
              placeholder="Description"
              value={description}
              onChangeText={setDescription}
            />

            <TextInput
              style={styles.input}
              placeholder="Amount"
              value={amount}
              onChangeText={setAmount}
              keyboardType="decimal-pad"
            />

            <Text style={styles.label}>Category</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryScroll}>
              <View style={styles.categorySelector}>
                {EXPENSE_CATEGORIES.map((category) => (
                  <TouchableOpacity
                    key={category.value}
                    style={[
                      styles.categoryChip,
                      { borderColor: category.color },
                      selectedCategory === category.value && {
                        backgroundColor: category.color,
                      },
                    ]}
                    onPress={() => setSelectedCategory(category.value)}
                  >
                    <Text style={styles.categoryChipIcon}>{category.icon}</Text>
                    <Text
                      style={[
                        styles.categoryChipText,
                        selectedCategory === category.value && styles.categoryChipTextSelected,
                      ]}
                    >
                      {category.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>

            <Text style={styles.label}>Split Type</Text>
            <View style={styles.splitTypeSelector}>
              <TouchableOpacity
                style={[
                  styles.splitTypeButton,
                  splitType === 'equal' && styles.splitTypeButtonSelected,
                ]}
                onPress={() => setSplitType('equal')}
              >
                <Text style={[
                  styles.splitTypeText,
                  splitType === 'equal' && styles.splitTypeTextSelected,
                ]}>Equal Split</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.splitTypeButton,
                  splitType === 'custom' && styles.splitTypeButtonSelected,
                ]}
                onPress={() => setSplitType('custom')}
              >
                <Text style={[
                  styles.splitTypeText,
                  splitType === 'custom' && styles.splitTypeTextSelected,
                ]}>Custom</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.splitTypeButton,
                  splitType === 'percentage' && styles.splitTypeButtonSelected,
                ]}
                onPress={() => setSplitType('percentage')}
              >
                <Text style={[
                  styles.splitTypeText,
                  splitType === 'percentage' && styles.splitTypeTextSelected,
                ]}>Percentage</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.label}>Select Group (Optional)</Text>
            <View style={styles.groupSelector}>
              {groups.map((group) => (
                <TouchableOpacity
                  key={group.id}
                  style={[
                    styles.groupChip,
                    selectedGroup === group.id && styles.groupChipSelected,
                  ]}
                  onPress={() => setSelectedGroup(group.id)}
                >
                  <Text
                    style={[
                      styles.groupChipText,
                      selectedGroup === group.id && styles.groupChipTextSelected,
                    ]}
                  >
                    {group.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, styles.addButton]}
                onPress={handleAddExpense}
              >
                <Text style={styles.addButtonText}>Add</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 20,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  totalCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    padding: 15,
    borderRadius: 10,
  },
  totalLabel: {
    color: '#fff',
    fontSize: 14,
    marginBottom: 5,
  },
  totalAmount: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
  },
  list: {
    padding: 15,
  },
  expenseCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  expenseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  expenseHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  categoryBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  categoryIcon: {
    fontSize: 20,
  },
  expenseInfo: {
    flex: 1,
  },
  expenseDescription: {
    fontSize: 16,
    fontWeight: '600',
  },
  expenseMetadata: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  categoryLabel: {
    fontSize: 12,
    color: '#666',
  },
  splitBadge: {
    fontSize: 11,
    color: '#2196F3',
    marginLeft: 5,
    fontWeight: '500',
  },
  expenseAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  expenseFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  expenseDetail: {
    fontSize: 14,
    color: '#666',
  },
  expenseDate: {
    fontSize: 12,
    color: '#999',
  },
  expenseGroup: {
    fontSize: 12,
    color: '#2196F3',
    marginTop: 5,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 60,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#bbb',
    textAlign: 'center',
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#2196F3',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  fabText: {
    fontSize: 32,
    color: '#fff',
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    minHeight: 400,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
  },
  label: {
    fontSize: 16,
    marginBottom: 10,
    color: '#333',
  },
  groupSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 20,
  },
  groupChip: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    marginBottom: 10,
  },
  groupChipSelected: {
    backgroundColor: '#2196F3',
  },
  groupChipText: {
    color: '#333',
  },
  groupChipTextSelected: {
    color: '#fff',
  },
  categoryScroll: {
    marginBottom: 15,
  },
  categorySelector: {
    flexDirection: 'row',
    paddingVertical: 5,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    borderWidth: 2,
  },
  categoryChipIcon: {
    fontSize: 16,
    marginRight: 5,
  },
  categoryChipText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  categoryChipTextSelected: {
    color: '#fff',
    fontWeight: '600',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#f0f0f0',
    marginRight: 10,
  },
  cancelButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  addButton: {
    backgroundColor: '#2196F3',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  splitTypeSelector: {
    flexDirection: 'row',
    marginBottom: 15,
    gap: 10,
  },
  splitTypeButton: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#f0f0f0',
  },
  splitTypeButtonSelected: {
    backgroundColor: '#E3F2FD',
    borderColor: '#2196F3',
  },
  splitTypeText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  splitTypeTextSelected: {
    color: '#2196F3',
    fontWeight: '600',
  },
});
