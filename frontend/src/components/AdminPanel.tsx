import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';

interface User {
  id: number;
  telegram_id: string;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  subscription_tier: string;
  projects_count: number;
}

const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userDetailLoading, setUserDetailLoading] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/api/admin/users');
      setUsers(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleUserClick = async (userId: number) => {
    setUserDetailLoading(true);
    setActionError(null);
    try {
      const response = await api.get(`/api/admin/users/${userId}`);
      setSelectedUser(response.data);
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Failed to load user details');
    } finally {
      setUserDetailLoading(false);
    }
  };

  const handleBan = async (userId: number) => {
    try {
      await api.post(`/api/admin/users/${userId}/ban`);
      // Update local state only after successful API call
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: false } : u));
      if (selectedUser?.id === userId) {
        setSelectedUser(prev => prev ? { ...prev, is_active: false } : prev);
      }
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Failed to ban user');
    }
  };

  // Component rendering (placeholder – add actual JSX as needed)
  return (
    <div>
      {/* Admin panel UI */}
    </div>
  );
};

export default AdminPanel;