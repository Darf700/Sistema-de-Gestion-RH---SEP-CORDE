import { Bell, LogOut, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotifications } from '../../contexts/NotificationContext';
import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { unreadCount } = useNotifications();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-blue-800">Sistema RH SEP/CORDE</h1>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(user.role === 'USUARIO' ? '/empleado/notificaciones' : '/rh/notificaciones')}
          className="relative p-2 text-gray-600 hover:text-blue-600 rounded-lg hover:bg-gray-100"
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User size={16} />
          <span className="font-medium">{user?.username}</span>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{user?.role}</span>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600 px-3 py-1.5 rounded-lg hover:bg-red-50"
        >
          <LogOut size={16} />
          Salir
        </button>
      </div>
    </nav>
  );
}
