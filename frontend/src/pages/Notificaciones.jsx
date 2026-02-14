import { Bell, CheckCheck } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';

export default function NotificacionesPage() {
  const { notifications, unreadCount, markAsRead, markAllRead } = useNotifications();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Notificaciones</h2>
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700">
            <CheckCheck size={16} /> Marcar todas como leidas
          </button>
        )}
      </div>

      <div className="space-y-2">
        {notifications.map(n => (
          <div
            key={n.id}
            onClick={() => !n.leida && markAsRead(n.id)}
            className={`bg-white rounded-xl border p-4 cursor-pointer transition-colors ${
              n.leida ? 'border-gray-200' : 'border-blue-200 bg-blue-50'
            }`}
          >
            <div className="flex items-start gap-3">
              <Bell size={18} className={n.leida ? 'text-gray-400' : 'text-blue-500'} />
              <div className="flex-1">
                <p className={`text-sm ${n.leida ? 'text-gray-600' : 'text-gray-800 font-medium'}`}>{n.mensaje}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.leida && <span className="w-2 h-2 bg-blue-500 rounded-full mt-2"></span>}
            </div>
          </div>
        ))}
        {notifications.length === 0 && (
          <div className="text-center py-12 text-gray-400">No tienes notificaciones</div>
        )}
      </div>
    </div>
  );
}
