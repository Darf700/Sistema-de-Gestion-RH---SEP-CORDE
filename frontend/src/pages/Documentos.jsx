import { useEffect, useState } from 'react';
import { FolderOpen, Plus, X, Upload } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const TIPOS_EMPLEADO = ['Constancia laboral', 'Carta de recomendacion', 'Comprobante de percepciones', 'Constancia de antiguedad', 'Otro'];
const TIPOS_RH = ['Actualizacion de CURP', 'Comprobante domicilio', 'Acta nacimiento hijos', 'RFC actualizado', 'Certificados/diplomas', 'Otro'];

export default function DocumentosPage() {
  const { isAdmin } = useAuth();
  const [documentos, setDocumentos] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ tipo: '', descripcion: '', empleado_id: '' });
  const [empleados, setEmpleados] = useState([]);
  const [error, setError] = useState('');

  const fetchDocumentos = () => {
    api.get('/api/documentos').then(r => setDocumentos(r.data)).catch(() => {});
  };

  useEffect(() => {
    fetchDocumentos();
    if (isAdmin) {
      api.get('/api/empleados').then(r => setEmpleados(r.data)).catch(() => {});
    }
  }, [isAdmin]);

  const handleSolicitar = async () => {
    setError('');
    try {
      if (isAdmin) {
        await api.post('/api/documentos/solicitar-a-empleado', form);
      } else {
        await api.post('/api/documentos/solicitar-a-rh', { tipo: form.tipo, descripcion: form.descripcion });
      }
      setShowForm(false);
      setForm({ tipo: '', descripcion: '', empleado_id: '' });
      fetchDocumentos();
    } catch (e) {
      setError(e.response?.data?.detail || 'Error');
    }
  };

  const handleUpload = async (docId) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append('archivo', file);
      try {
        await api.post(`/api/documentos/${docId}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        fetchDocumentos();
      } catch (err) {
        alert(err.response?.data?.detail || 'Error al subir archivo');
      }
    };
    input.click();
  };

  const handleCambiarEstado = async (docId, estado) => {
    try {
      await api.put(`/api/documentos/${docId}/estado`, { estado });
      fetchDocumentos();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  const tipos = isAdmin ? TIPOS_RH : TIPOS_EMPLEADO;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Documentos</h2>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus size={18} /> {isAdmin ? 'Solicitar a Empleado' : 'Solicitar a RH'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-700">{isAdmin ? 'Solicitar Documento a Empleado' : 'Solicitar Documento a RH'}</h3>
            <button onClick={() => setShowForm(false)}><X size={20} className="text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {isAdmin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Empleado</label>
                <select value={form.empleado_id} onChange={e => setForm({...form, empleado_id: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                  <option value="">Seleccionar...</option>
                  {empleados.map(e => <option key={e.id} value={e.id}>{e.nombre_completo}</option>)}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Seleccionar...</option>
                {tipos.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Descripcion</label>
              <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
          </div>
          {error && <div className="mt-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}
          <button onClick={handleSolicitar} disabled={!form.tipo} className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
            Solicitar
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Tipo</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Origen</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Estado</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Fecha</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {documentos.map(d => (
              <tr key={d.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">{d.tipo}</td>
                <td className="px-4 py-3 text-sm">{d.origen === 'Empleado' ? 'Empleado a RH' : 'RH a Empleado'}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    d.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' :
                    d.estado === 'En Proceso' ? 'bg-blue-100 text-blue-700' :
                    d.estado === 'Listo' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>{d.estado}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(d.fecha_solicitud).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-sm">
                  <div className="flex gap-2">
                    <button onClick={() => handleUpload(d.id)} className="text-blue-600 hover:text-blue-700" title="Subir archivo"><Upload size={16} /></button>
                    {isAdmin && d.estado !== 'Entregado' && (
                      <select onChange={e => { if (e.target.value) handleCambiarEstado(d.id, e.target.value); e.target.value = ''; }} className="text-xs border rounded px-1 py-0.5">
                        <option value="">Cambiar estado</option>
                        <option value="En Proceso">En Proceso</option>
                        <option value="Listo">Listo</option>
                        <option value="Entregado">Entregado</option>
                      </select>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {documentos.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No hay documentos</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
