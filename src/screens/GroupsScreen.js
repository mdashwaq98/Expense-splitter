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

export default function GroupsScreen() {
  const { groups, addGroup, deleteGroup, calculateBalances } = useContext(ExpenseContext);
  const { user } = useContext(AuthContext);
  const [modalVisible, setModalVisible] = useState(false);
  const [groupName, setGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  const handleAddGroup = async () => {
    if (!groupName) {
      Alert.alert('Error', 'Please enter a group name');
      return;
    }

    const group = {
      name: groupName.trim(),
      description: '',
    };

    await addGroup(group);
    setGroupName('');
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

    return (
      <View style={styles.detailContent}>
        <Text style={styles.detailTitle}>{selectedGroup.name}</Text>

        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Your Balance</Text>
          <Text
            style={[
              styles.balanceAmount,
              balance > 0 ? styles.positiveBalance : styles.negativeBalance,
            ]}
          >
            ${Math.abs(balance).toFixed(2)}
          </Text>
          <Text style={styles.balanceStatus}>
            {balance > 0 ? 'You are owed' : balance < 0 ? 'You owe' : 'Settled up'}
          </Text>
        </View>

        <Text style={styles.sectionTitle}>Group Members</Text>
        <View style={styles.membersList}>
          {selectedGroup.members?.map((memberId, index) => (
            <View key={index} style={styles.memberChip}>
              <Text style={styles.memberText}>
                {memberId === user.id ? 'You' : `Member ${index + 1}`}
              </Text>
            </View>
          ))}
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
    marginBottom: 20,
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
  memberChip: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    marginBottom: 10,
  },
  memberText: {
    color: '#2196F3',
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
});
