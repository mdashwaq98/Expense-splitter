import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const userData = await AsyncStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error loading user:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      // In a real app, this would make an API call
      // For now, simulate login
      const users = await AsyncStorage.getItem('users');
      const userList = users ? JSON.parse(users) : [];
      
      const foundUser = userList.find(
        u => u.email === email && u.password === password
      );

      if (foundUser) {
        const userToSave = { ...foundUser };
        delete userToSave.password; // Don't store password in user session
        await AsyncStorage.setItem('user', JSON.stringify(userToSave));
        setUser(userToSave);
        return { success: true };
      } else {
        return { success: false, error: 'Invalid email or password' };
      }
    } catch (error) {
      return { success: false, error: 'Login failed' };
    }
  };

  const signup = async (name, email, password) => {
    try {
      // Get existing users
      const users = await AsyncStorage.getItem('users');
      const userList = users ? JSON.parse(users) : [];

      // Check if user already exists
      if (userList.find(u => u.email === email)) {
        return { success: false, error: 'Email already registered' };
      }

      // Create new user
      const newUser = {
        id: Date.now().toString(),
        name,
        email,
        password,
        createdAt: new Date().toISOString(),
      };

      userList.push(newUser);
      await AsyncStorage.setItem('users', JSON.stringify(userList));

      // Auto login after signup
      const userToSave = { ...newUser };
      delete userToSave.password;
      await AsyncStorage.setItem('user', JSON.stringify(userToSave));
      setUser(userToSave);

      return { success: true };
    } catch (error) {
      return { success: false, error: 'Signup failed' };
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('user');
      setUser(null);
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const updateProfile = async (updatedData) => {
    try {
      const updatedUser = { ...user, ...updatedData };
      await AsyncStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Failed to update profile' };
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        signup,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
