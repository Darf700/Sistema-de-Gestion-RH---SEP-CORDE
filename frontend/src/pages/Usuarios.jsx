import { useEffect, useState } from 'react';
import { Users, Plus, X, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function UsuariosPage() {
  const [usuarios, setUsuarios] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', role: 'USUARIO', empleado_id: '' });
  const [empleados, setEmpleados] = useState([]);
  const [error, setError] = useState('');

  const fetchUsuarios = () => {
    api.get('/api/auth/usuarios').then(r => setUsuarios(r.data)).catch(() => {});
  };

  useEffect(() => {
    fetchUsuarios();
    api.get('/api/empleados').then(r => setEmpleados(r.data)).catch(() => {});
  }, []);

  const handleCrear = async () => {
    setError('');
    try {
      const payload = { ...form };
      if (payload.empleado_id) payload.empleado_id = parseInt(payload.empleado_id);
      else delete payload.empleado_id;
      await api.post('/api/auth/usuarios', payload);
      setShowForm(false);
      setForm({ username: '', password: '', role: 'USUARIO', empleado_id: '' });
      fetchUsuarios();
    } catch (e) {
      setError(e.response?.data?.detail || 'Error');
    }
  };

  const handleDesactivar = async (id) => {
    if (!confirm('Desactivar este usuario?')) return;
    try {
      await api.delete(`/api/auth/usuarios/${id}`);
      fetchUsuarios();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  const handleResetPassword = async (id) => {
    const newPassword = prompt('Nueva contrasena (min 8 caracteres):');
    if (!newPassword) return;
    try {
      await api.post('/api/auth/reset-password', { user_id: id, new_password: newPassword });
      alert('Contrasena reseteada');
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Usuarios</h2>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> Nuevo Usuario
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-700">Nuevo Usuario</h3>
            <button onClick={() => setShowForm(false)}><X size={20} className="text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input type="text" value={form.username} onChange={e => setForm({...form, username: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contrasena</label>
              <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
              <select value={form.role} onChange={e => setForm({...form, role: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="USUARIO">USUARIO</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Empleado (opcional)</label>
              <select value={form.empleado_id} onChange={e => setForm({...form, empleado_id: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Sin asociar</option>
                {empleados.map(e => <option key={e.id} value={e.id}>{e.nombre_completo}</option>)}
              </select>
            </div>
          </div>
          {error && <div className="mt-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
          <button onClick={handleCrear} disabled={!form.username || !form.password} className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
            Crear Usuario
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Username</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Rol</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Estado</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Ultimo Login</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map(u => (
              <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium">{u.username}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    u.role === 'ROOT' ? 'bg-red-100 text-red-700' :
                    u.role === 'ADMIN' ? 'bg-purple-100 text-purple-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>{u.role}</span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${u.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {u.active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{u.last_login ? new Date(u.last_login).toLocaleString() : 'Nunca'}</td>
                <td className="px-4 py-3 text-sm">
                  {u.role !== 'ROOT' && (
                    <div className="flex gap-2">
                      <button onClick={() => handleResetPassword(u.id)} className="text-blue-600 hover:underline text-xs">Reset Pass</button>
                      <button onClick={() => handleDesactivar(u.id)} className="text-red-600 hover:text-red-700"><Trash2 size={14} /></button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
