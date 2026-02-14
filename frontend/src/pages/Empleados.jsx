import { useEffect, useState } from 'react';
import { Users, Plus, X, Edit2 } from 'lucide-react';
import api from '../services/api';

export default function EmpleadosPage() {
  const [empleados, setEmpleados] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    nombre_completo: '', claves_presupuestales: '', horario: '08:00-15:00',
    adscripcion: '', numero_asistencia: '', tipo: 'Apoyo y Asistencia',
    nombramiento: 'Base', fecha_ingreso: '', email: '', telefono: '',
  });
  const [error, setError] = useState('');

  const fetchEmpleados = () => {
    api.get('/api/empleados').then(r => setEmpleados(r.data)).catch(() => {});
  };

  useEffect(() => { fetchEmpleados(); }, []);

  const handleSubmit = async () => {
    setError('');
    try {
      if (editing) {
        await api.put(`/api/empleados/${editing}`, form);
      } else {
        await api.post('/api/empleados', form);
      }
      setShowForm(false);
      setEditing(null);
      setForm({ nombre_completo: '', claves_presupuestales: '', horario: '08:00-15:00', adscripcion: '', numero_asistencia: '', tipo: 'Apoyo y Asistencia', nombramiento: 'Base', fecha_ingreso: '', email: '', telefono: '' });
      fetchEmpleados();
    } catch (e) {
      setError(e.response?.data?.detail || 'Error');
    }
  };

  const handleEdit = (emp) => {
    setEditing(emp.id);
    setForm({
      nombre_completo: emp.nombre_completo, claves_presupuestales: emp.claves_presupuestales,
      horario: emp.horario, adscripcion: emp.adscripcion, numero_asistencia: emp.numero_asistencia,
      tipo: emp.tipo, nombramiento: emp.nombramiento, fecha_ingreso: emp.fecha_ingreso,
      email: emp.email || '', telefono: emp.telefono || '',
    });
    setShowForm(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Empleados</h2>
        <button onClick={() => { setEditing(null); setShowForm(true); }} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> Nuevo Empleado
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-700">{editing ? 'Editar' : 'Nuevo'} Empleado</h3>
            <button onClick={() => { setShowForm(false); setEditing(null); }}><X size={20} className="text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label>
              <input type="text" value={form.nombre_completo} onChange={e => setForm({...form, nombre_completo: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">No. Asistencia</label>
              <input type="text" value={form.numero_asistencia} onChange={e => setForm({...form, numero_asistencia: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Claves Presupuestales</label>
              <input type="text" value={form.claves_presupuestales} onChange={e => setForm({...form, claves_presupuestales: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Horario</label>
              <input type="text" value={form.horario} onChange={e => setForm({...form, horario: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Adscripcion</label>
              <input type="text" value={form.adscripcion} onChange={e => setForm({...form, adscripcion: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="Apoyo y Asistencia">Apoyo y Asistencia</option>
                <option value="Docente">Docente</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombramiento</label>
              <select value={form.nombramiento} onChange={e => setForm({...form, nombramiento: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="Base">Base</option>
                <option value="Interino">Interino</option>
                <option value="Limitado">Limitado</option>
                <option value="Gravidez">Gravidez</option>
                <option value="Prejubilatorio">Prejubilatorio</option>
                <option value="Honorarios">Honorarios</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Ingreso</label>
              <input type="date" value={form.fecha_ingreso} onChange={e => setForm({...form, fecha_ingreso: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telefono</label>
              <input type="text" value={form.telefono} onChange={e => setForm({...form, telefono: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
          </div>
          {error && <div className="mt-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
          <button onClick={handleSubmit} className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            {editing ? 'Guardar Cambios' : 'Crear Empleado'}
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Nombre</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Adscripcion</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Tipo</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Horario</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Antiguedad</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map(e => (
              <tr key={e.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium">{e.nombre_completo}</td>
                <td className="px-4 py-3 text-sm">{e.adscripcion}</td>
                <td className="px-4 py-3 text-sm">{e.tipo}</td>
                <td className="px-4 py-3 text-sm">{e.horario}</td>
                <td className="px-4 py-3 text-sm">{e.antiguedad_meses} meses</td>
                <td className="px-4 py-3 text-sm">
                  <button onClick={() => handleEdit(e)} className="text-blue-600 hover:text-blue-700"><Edit2 size={16} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
