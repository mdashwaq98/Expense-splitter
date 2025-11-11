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
} from 'react-native';
import { ExpenseContext } from '../context/ExpenseContext';
import { AuthContext } from '../context/AuthContext';

export default function HomeScreen() {
  const { expenses, addExpense, deleteExpense, groups } = useContext(ExpenseContext);
  const { user } = useContext(AuthContext);
  const [modalVisible, setModalVisible] = useState(false);
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);

  const handleAddExpense = async () => {
    if (!description || !amount) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    const expense = {
      description: description.trim(),
      amount: parseFloat(amount),
      paidBy: user.id,
      paidByName: user.name,
      groupId: selectedGroup,
      splitBetween: [user.id],
    };

    await addExpense(expense);
    setDescription('');
    setAmount('');
    setSelectedGroup(null);
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

  const renderExpense = ({ item }) => (
    <TouchableOpacity
      style={styles.expenseCard}
      onLongPress={() => handleDeleteExpense(item.id)}
    >
      <View style={styles.expenseHeader}>
        <Text style={styles.expenseDescription}>{item.description}</Text>
        <Text style={styles.expenseAmount}>${item.amount.toFixed(2)}</Text>
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

  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Expenses</Text>
        <View style={styles.totalCard}>
          <Text style={styles.totalLabel}>Total Expenses</Text>
          <Text style={styles.totalAmount}>${totalExpenses.toFixed(2)}</Text>
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
  expenseDescription: {
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
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
});
