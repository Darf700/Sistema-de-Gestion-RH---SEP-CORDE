import { useEffect, useState } from 'react';
import { AlertTriangle, Plus, X } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function AdeudosPage() {
  const { isAdmin } = useAuth();
  const [adeudos, setAdeudos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ empleado_id: '', tipo: '', descripcion: '', monto: '' });
  const [empleados, setEmpleados] = useState([]);
  const [error, setError] = useState('');

  const fetchAdeudos = () => {
    api.get('/api/adeudos').then(r => setAdeudos(r.data)).catch(() => {});
  };

  useEffect(() => {
    fetchAdeudos();
    if (isAdmin) {
      api.get('/api/empleados').then(r => setEmpleados(r.data)).catch(() => {});
    }
  }, [isAdmin]);

  const handleCrear = async () => {
    setError('');
    try {
      await api.post('/api/adeudos', {
        empleado_id: parseInt(form.empleado_id),
        tipo: form.tipo,
        descripcion: form.descripcion,
        monto: form.monto ? parseFloat(form.monto) : null,
      });
      setShowForm(false);
      setForm({ empleado_id: '', tipo: '', descripcion: '', monto: '' });
      fetchAdeudos();
    } catch (e) {
      setError(e.response?.data?.detail || 'Error');
    }
  };

  const handleResolver = async (id) => {
    try {
      await api.put(`/api/adeudos/${id}`, { estado: 'Resuelto' });
      fetchAdeudos();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  const handleEliminar = async (id) => {
    if (!confirm('Eliminar este adeudo?')) return;
    try {
      await api.delete(`/api/adeudos/${id}`);
      fetchAdeudos();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Adeudos</h2>
        {isAdmin && (
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700">
            <Plus size={18} /> Marcar Adeudo
          </button>
        )}
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-700">Nuevo Adeudo</h3>
            <button onClick={() => setShowForm(false)}><X size={20} className="text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Empleado</label>
              <select value={form.empleado_id} onChange={e => setForm({...form, empleado_id: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Seleccionar...</option>
                {empleados.map(e => <option key={e.id} value={e.id}>{e.nombre_completo}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Seleccionar...</option>
                <option value="Justificante no entregado">Justificante no entregado</option>
                <option value="Documento pendiente">Documento pendiente</option>
                <option value="Otro">Otro</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descripcion</label>
              <input type="text" value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Monto (opcional)</label>
              <input type="number" value={form.monto} onChange={e => setForm({...form, monto: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
          </div>
          {error && <div className="mt-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
          <button onClick={handleCrear} disabled={!form.empleado_id || !form.tipo || !form.descripcion} className="mt-4 bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 disabled:opacity-50">
            Marcar Adeudo
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Tipo</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Descripcion</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Monto</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Estado</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Fecha</th>
              {isAdmin && <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {adeudos.map(a => (
              <tr key={a.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">{a.tipo}</td>
                <td className="px-4 py-3 text-sm">{a.descripcion}</td>
                <td className="px-4 py-3 text-sm">{a.monto ? `$${a.monto}` : '-'}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    a.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                  }`}>{a.estado}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(a.fecha_marcado).toLocaleDateString()}</td>
                {isAdmin && (
                  <td className="px-4 py-3 text-sm">
                    {a.estado === 'Pendiente' && (
                      <div className="flex gap-2">
                        <button onClick={() => handleResolver(a.id)} className="text-green-600 hover:underline text-xs">Resolver</button>
                        <button onClick={() => handleEliminar(a.id)} className="text-red-600 hover:underline text-xs">Eliminar</button>
                      </div>
                    )}
                  </td>
                )}
              </tr>
            ))}
            {adeudos.length === 0 && (
              <tr><td colSpan={isAdmin ? 6 : 5} className="px-4 py-8 text-center text-gray-400">No hay adeudos</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
