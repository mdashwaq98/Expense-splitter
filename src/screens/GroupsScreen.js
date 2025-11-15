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

// Currency options
const CURRENCIES = [
  { value: 'USD', label: 'USD ($)', symbol: '$' },
  { value: 'EUR', label: 'EUR (€)', symbol: '€' },
  { value: 'GBP', label: 'GBP (£)', symbol: '£' },
  { value: 'INR', label: 'INR (₹)', symbol: '₹' },
  { value: 'CAD', label: 'CAD (C$)', symbol: 'C$' },
  { value: 'AUD', label: 'AUD (A$)', symbol: 'A$' },
];

export default function GroupsScreen() {
  const { groups, addGroup, deleteGroup, calculateBalances, simplifyDebts, getCurrencySymbol, settlements, addSettlement, addMemberToGroup, removeMemberFromGroup } = useContext(ExpenseContext);
  const { user } = useContext(AuthContext);
  const [modalVisible, setModalVisible] = useState(false);
  const [groupName, setGroupName] = useState('');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [settlementModalVisible, setSettlementModalVisible] = useState(false);
  const [settlementAmount, setSettlementAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Cash');
  const [addMemberModalVisible, setAddMemberModalVisible] = useState(false);
  const [newMemberName, setNewMemberName] = useState('');

  const handleAddGroup = async () => {
    if (!groupName) {
      Alert.alert('Error', 'Please enter a group name');
      return;
    }

    const group = {
      name: groupName.trim(),
      description: '',
      currency: selectedCurrency,
    };

    await addGroup(group);
    setGroupName('');
    setSelectedCurrency('USD');
    setModalVisible(false);
    Alert.alert('Success', 'Group created successfully');
  };

  const handleDeleteGroup = (groupId) => {
    Alert.alert(
      'Delete Group',
      'Are you sure you want to delete this group?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteGroup(groupId),
        },
      ]
    );
  };

  const showGroupDetails = (group) => {
    setSelectedGroup(group);
    setDetailModalVisible(true);
  };

  const handleRecordSettlement = async () => {
    if (!settlementAmount || parseFloat(settlementAmount) <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }

    const settlement = {
      groupId: selectedGroup.id,
      fromUser: user.id,
      toUser: user.id, // In real app, would select recipient
      amount: parseFloat(settlementAmount),
      currency: selectedGroup.currency || 'USD',
      paymentMethod,
    };

    await addSettlement(settlement);
    setSettlementAmount('');
    setPaymentMethod('Cash');
    setSettlementModalVisible(false);
    Alert.alert('Success', 'Payment recorded successfully');
  };

  const handleAddMember = async () => {
    if (!newMemberName.trim()) {
      Alert.alert('Error', 'Please enter a member name');
      return;
    }

    await addMemberToGroup(selectedGroup.id, newMemberName.trim());
    setNewMemberName('');
    setAddMemberModalVisible(false);
    Alert.alert('Success', `${newMemberName} added to group`);
  };

  const handleRemoveMember = (memberId, memberName) => {
    if (memberId === user.id) {
      Alert.alert('Error', 'You cannot remove yourself. Use "Leave Group" instead.');
      return;
    }

    Alert.alert(
      'Remove Member',
      `Remove ${memberName} from group?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            await removeMemberFromGroup(selectedGroup.id, memberId);
            Alert.alert('Success', `${memberName} removed from group`);
          },
        },
      ]
    );
  };

  const renderGroup = ({ item }) => {
    const balances = calculateBalances(item.id);
    const memberCount = item.members?.length || 1;

    return (
      <TouchableOpacity
        style={styles.groupCard}
        onPress={() => showGroupDetails(item)}
        onLongPress={() => handleDeleteGroup(item.id)}
      >
        <View style={styles.groupHeader}>
          <View style={styles.groupIcon}>
            <Text style={styles.groupIconText}>
              {item.name.charAt(0).toUpperCase()}
            </Text>
          </View>
          <View style={styles.groupInfo}>
            <Text style={styles.groupName}>{item.name}</Text>
            <Text style={styles.groupMembers}>
              {memberCount} member{memberCount !== 1 ? 's' : ''}
            </Text>
          </View>
        </View>
        <Text style={styles.groupDate}>
          Created {new Date(item.createdAt).toLocaleDateString()}
        </Text>
      </TouchableOpacity>
    );
  };

  const renderGroupDetails = () => {
    if (!selectedGroup) return null;

    const balances = calculateBalances(selectedGroup.id);
    const balance = balances[user.id] || 0;
    const suggestedSettlements = simplifyDebts(selectedGroup.id);
    const currencySymbol = getCurrencySymbol(selectedGroup.currency);
    const groupSettlements = settlements.filter(s => s.groupId === selectedGroup.id);

    return (
      <View style={styles.detailContent}>
        <Text style={styles.detailTitle}>{selectedGroup.name}</Text>
        <Text style={styles.currencyBadge}>Currency: {selectedGroup.currency || 'USD'}</Text>

        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Your Balance</Text>
          <Text
            style={[
              styles.balanceAmount,
              balance > 0 ? styles.positiveBalance : styles.negativeBalance,
            ]}
          >
            {currencySymbol}{Math.abs(balance).toFixed(2)}
          </Text>
          <Text style={styles.balanceStatus}>
            {balance > 0 ? 'You are owed' : balance < 0 ? 'You owe' : 'Settled up'}
          </Text>
        </View>

        {balance !== 0 && (
          <TouchableOpacity
            style={styles.recordPaymentButton}
            onPress={() => setSettlementModalVisible(true)}
          >
            <Text style={styles.recordPaymentText}>💳 Record Payment</Text>
          </TouchableOpacity>
        )}

        {suggestedSettlements.length > 0 && (
          <View style={styles.settlementsSection}>
            <Text style={styles.sectionTitle}>💡 Suggested Settlements (Optimized)</Text>
            <Text style={styles.sectionSubtitle}>
              {suggestedSettlements.length} transaction{suggestedSettlements.length !== 1 ? 's' : ''} to settle all debts
            </Text>
            {suggestedSettlements.map((settlement, index) => (
              <View key={index} style={styles.settlementCard}>
                <Text style={styles.settlementText}>
                  {settlement.from === user.id ? 'You pay' : 'Paid'} 
                  {' → '} 
                  {settlement.to === user.id ? 'You' : 'Member'}
                </Text>
                <Text style={styles.settlementAmountText}>
                  {currencySymbol}{settlement.amount.toFixed(2)}
                </Text>
              </View>
            ))}
          </View>
        )}

        {groupSettlements.length > 0 && (
          <View style={styles.settlementsSection}>
            <Text style={styles.sectionTitle}>📜 Payment History</Text>
            {groupSettlements.map((settlement) => (
              <View key={settlement.id} style={styles.historyCard}>
                <View>
                  <Text style={styles.historyText}>
                    {settlement.paymentMethod} payment
                  </Text>
                  <Text style={styles.historyDate}>
                    {new Date(settlement.createdAt).toLocaleDateString()}
                  </Text>
                </View>
                <Text style={styles.historyAmount}>
                  {currencySymbol}{settlement.amount.toFixed(2)}
                </Text>
              </View>
            ))}
          </View>
        )}

        <View style={styles.membersSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Group Members ({selectedGroup.members?.length || 0})</Text>
            <TouchableOpacity
              style={styles.addMemberButton}
              onPress={() => setAddMemberModalVisible(true)}
            >
              <Text style={styles.addMemberButtonText}>+ Add</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.membersList}>
            {selectedGroup.members?.map((member, index) => {
              const isObject = typeof member === 'object';
              const memberName = isObject ? member.name : (member === user.id ? 'You' : `Member ${index + 1}`);
              const memberId = isObject ? member.userId : member;
              const memberRole = isObject ? member.role : (member === user.id ? 'admin' : 'member');
              
              return (
                <View key={index} style={styles.memberCard}>
                  <View style={styles.memberInfo}>
                    <View style={styles.memberAvatar}>
                      <Text style={styles.memberAvatarText}>
                        {memberName.charAt(0).toUpperCase()}
                      </Text>
                    </View>
                    <View>
                      <Text style={styles.memberName}>{memberName}</Text>
                      <Text style={styles.memberRole}>
                        {memberRole === 'admin' ? '👑 Admin' : 'Member'}
                      </Text>
                    </View>
                  </View>
                  {memberId !== user.id && memberRole !== 'admin' && (
                    <TouchableOpacity
                      style={styles.removeMemberButton}
                      onPress={() => handleRemoveMember(memberId, memberName)}
                    >
                      <Text style={styles.removeMemberText}>Remove</Text>
                    </TouchableOpacity>
                  )}
                </View>
              );
            })}
          </View>
        </View>

        <TouchableOpacity
          style={styles.closeButton}
          onPress={() => setDetailModalVisible(false)}
        >
          <Text style={styles.closeButtonText}>Close</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Groups</Text>
        <Text style={styles.headerSubtitle}>
          {groups.length} group{groups.length !== 1 ? 's' : ''}
        </Text>
      </View>

      <FlatList
        data={groups}
        renderItem={renderGroup}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No groups yet</Text>
            <Text style={styles.emptySubtext}>
              Create a group to split expenses with friends
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
            <Text style={styles.modalTitle}>Create Group</Text>

            <TextInput
              style={styles.input}
              placeholder="Group Name"
              value={groupName}
              onChangeText={setGroupName}
            />

            <Text style={styles.label}>Currency</Text>
            <View style={styles.currencySelector}>
              {CURRENCIES.map((currency) => (
                <TouchableOpacity
                  key={currency.value}
                  style={[
                    styles.currencyChip,
                    selectedCurrency === currency.value && styles.currencyChipSelected,
                  ]}
                  onPress={() => setSelectedCurrency(currency.value)}
                >
                  <Text
                    style={[
                      styles.currencyChipText,
                      selectedCurrency === currency.value && styles.currencyChipTextSelected,
                    ]}
                  >
                    {currency.label}
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
                onPress={handleAddGroup}
              >
                <Text style={styles.addButtonText}>Create</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent={true}
        visible={detailModalVisible}
        onRequestClose={() => setDetailModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            {renderGroupDetails()}
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent={true}
        visible={settlementModalVisible}
        onRequestClose={() => setSettlementModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Record Payment</Text>

            <TextInput
              style={styles.input}
              placeholder="Amount"
              value={settlementAmount}
              onChangeText={setSettlementAmount}
              keyboardType="decimal-pad"
            />

            <Text style={styles.label}>Payment Method</Text>
            <View style={styles.paymentMethodSelector}>
              {['Cash', 'Card', 'UPI', 'Bank Transfer'].map((method) => (
                <TouchableOpacity
                  key={method}
                  style={[
                    styles.paymentChip,
                    paymentMethod === method && styles.paymentChipSelected,
                  ]}
                  onPress={() => setPaymentMethod(method)}
                >
                  <Text
                    style={[
                      styles.paymentChipText,
                      paymentMethod === method && styles.paymentChipTextSelected,
                    ]}
                  >
                    {method}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setSettlementModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, styles.addButton]}
                onPress={handleRecordSettlement}
              >
                <Text style={styles.addButtonText}>Record</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent={true}
        visible={addMemberModalVisible}
        onRequestClose={() => setAddMemberModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add Member</Text>

            <TextInput
              style={styles.input}
              placeholder="Member Name"
              value={newMemberName}
              onChangeText={setNewMemberName}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => {
                  setNewMemberName('');
                  setAddMemberModalVisible(false);
                }}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, styles.addButton]}
                onPress={handleAddMember}
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
    backgroundColor: '#4CAF50',
    padding: 20,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 5,
  },
  list: {
    padding: 15,
  },
  groupCard: {
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
  groupHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  groupIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#4CAF50',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  groupIconText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  groupInfo: {
    flex: 1,
  },
  groupName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 5,
  },
  groupMembers: {
    fontSize: 14,
    color: '#666',
  },
  groupDate: {
    fontSize: 12,
    color: '#999',
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
    backgroundColor: '#4CAF50',
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
    minHeight: 300,
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
    backgroundColor: '#4CAF50',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  detailContent: {
    paddingVertical: 10,
  },
  detailTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  currencyBadge: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
    fontWeight: '500',
    textAlign: 'center',
  },
  balanceCard: {
    backgroundColor: '#f5f5f5',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 20,
  },
  balanceLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  balanceAmount: {
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  positiveBalance: {
    color: '#4CAF50',
  },
  negativeBalance: {
    color: '#f44336',
  },
  balanceStatus: {
    fontSize: 14,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
  },
  membersList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 20,
  },
  membersSection: {
    marginTop: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  addMemberButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  addMemberButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  memberCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  memberInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  memberAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2196F3',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  memberAvatarText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  memberName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  memberRole: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  removeMemberButton: {
    backgroundColor: '#ffebee',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  removeMemberText: {
    color: '#f44336',
    fontSize: 12,
    fontWeight: '600',
  },
  closeButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  settlementsSection: {
    marginTop: 20,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  settlementCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  settlementText: {
    fontSize: 15,
    color: '#333',
    flex: 1,
  },
  settlementAmountText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  recordPaymentButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 15,
  },
  recordPaymentText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  historyCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  historyText: {
    fontSize: 15,
    color: '#333',
    fontWeight: '500',
  },
  historyDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 3,
  },
  historyAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  paymentMethodSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 20,
  },
  paymentChip: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    marginBottom: 10,
  },
  paymentChipSelected: {
    backgroundColor: '#4CAF50',
  },
  paymentChipText: {
    fontSize: 14,
    color: '#333',
  },
  paymentChipTextSelected: {
    color: '#fff',
    fontWeight: '600',
  },
  label: {
    fontSize: 16,
    marginBottom: 10,
    marginTop: 10,
    color: '#333',
  },
  currencySelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 20,
  },
  currencyChip: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    marginBottom: 10,
  },
  currencyChipSelected: {
    backgroundColor: '#4CAF50',
  },
  currencyChipText: {
    fontSize: 14,
    color: '#333',
  },
  currencyChipTextSelected: {
    color: '#fff',
    fontWeight: '600',
  },
});
