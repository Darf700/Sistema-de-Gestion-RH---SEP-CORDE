import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotifications must be used within NotificationProvider');
  return context;
};

export const NotificationProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const [notifRes, countRes] = await Promise.all([
        api.get('/api/notificaciones'),
        api.get('/api/notificaciones/conteo'),
      ]);
      setNotifications(notifRes.data);
      setUnreadCount(countRes.data.no_leidas);
    } catch {
      // silently fail
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // Poll cada 30s
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markAsRead = async (id) => {
    await api.put(`/api/notificaciones/${id}/leer`);
    fetchNotifications();
  };

  const markAllRead = async () => {
    await api.put('/api/notificaciones/leer-todas');
    fetchNotifications();
  };

  return (
    <NotificationContext.Provider value={{
      notifications, unreadCount, fetchNotifications, markAsRead, markAllRead,
    }}>
      {children}
    </NotificationContext.Provider>
  );
};
