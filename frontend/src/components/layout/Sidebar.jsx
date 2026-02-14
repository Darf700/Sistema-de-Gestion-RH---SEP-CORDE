import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, FileText, Gift, FolderOpen, AlertTriangle,
  Users, BarChart3, Settings, Bell,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const menuEmpleado = [
  { to: '/empleado', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/empleado/justificantes', icon: FileText, label: 'Justificantes' },
  { to: '/empleado/prestaciones', icon: Gift, label: 'Prestaciones' },
  { to: '/empleado/documentos', icon: FolderOpen, label: 'Documentos' },
  { to: '/empleado/adeudos', icon: AlertTriangle, label: 'Adeudos' },
  { to: '/empleado/notificaciones', icon: Bell, label: 'Notificaciones' },
];

const menuAdmin = [
  { to: '/rh', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/rh/empleados', icon: Users, label: 'Empleados' },
  { to: '/rh/justificantes', icon: FileText, label: 'Justificantes' },
  { to: '/rh/prestaciones', icon: Gift, label: 'Prestaciones' },
  { to: '/rh/documentos', icon: FolderOpen, label: 'Documentos' },
  { to: '/rh/adeudos', icon: AlertTriangle, label: 'Adeudos' },
  { to: '/rh/reportes', icon: BarChart3, label: 'Reportes' },
  { to: '/rh/notificaciones', icon: Bell, label: 'Notificaciones' },
];

const menuRoot = [
  { to: '/admin', icon: Settings, label: 'Administracion', end: true },
  { to: '/admin/usuarios', icon: Users, label: 'Usuarios' },
];

export default function Sidebar() {
  const { user, isAdmin, isRoot } = useAuth();

  const getMenu = () => {
    if (user?.role === 'USUARIO') return menuEmpleado;
    if (isAdmin) return menuAdmin;
    return [];
  };

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors ${
      isActive
        ? 'bg-blue-50 text-blue-700 font-medium'
        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
    }`;

  return (
    <aside className="w-60 bg-white border-r border-gray-200 min-h-screen p-4">
      <nav className="space-y-1">
        {getMenu().map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className={linkClass}>
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}

        {isRoot && (
          <>
            <hr className="my-3 border-gray-200" />
            <p className="text-xs text-gray-400 px-4 mb-2 uppercase">Admin</p>
            {menuRoot.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.end} className={linkClass}>
                <item.icon size={18} />
                {item.label}
              </NavLink>
            ))}
          </>
        )}
      </nav>
    </aside>
  );
}
