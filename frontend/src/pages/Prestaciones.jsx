import { useEffect, useState } from 'react';
import { Gift, Plus, X, Check, XCircle } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function PrestacionesPage() {
  const { isAdmin } = useAuth();
  const [prestaciones, setPrestaciones] = useState([]);
  const [catalogo, setCatalogo] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ tipo: '', fecha_inicio: '', fecha_fin: '', motivo: '' });
  const [validacion, setValidacion] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchPrestaciones = () => {
    api.get('/api/prestaciones').then(r => setPrestaciones(r.data)).catch(() => {});
  };

  useEffect(() => {
    fetchPrestaciones();
    api.get('/api/prestaciones/catalogo').then(r => setCatalogo(r.data)).catch(() => {});
  }, []);

  const selectedCatalogo = catalogo.find(c => c.tipo === form.tipo);

  const handleValidar = async () => {
    setValidacion(null);
    setError('');
    try {
      const r = await api.post('/api/prestaciones/validar', form);
      setValidacion(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al validar');
    }
  };

  const handleCrear = async () => {
    setError('');
    setLoading(true);
    try {
      await api.post('/api/prestaciones', form);
      setShowForm(false);
      setForm({ tipo: '', fecha_inicio: '', fecha_fin: '', motivo: '' });
      setValidacion(null);
      fetchPrestaciones();
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al crear prestacion');
    }
    setLoading(false);
  };

  const handleAprobar = async (id) => {
    try {
      await api.put(`/api/prestaciones/${id}/aprobar`);
      fetchPrestaciones();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  const handleRechazar = async (id) => {
    const motivo = prompt('Motivo de rechazo:');
    if (motivo === null) return;
    try {
      await api.put(`/api/prestaciones/${id}/rechazar`, { motivo_rechazo: motivo });
      fetchPrestaciones();
    } catch (e) {
      alert(e.response?.data?.detail || 'Error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Prestaciones</h2>
        {!isAdmin && (
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Plus size={18} /> Nueva Prestacion
          </button>
        )}
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-700">Solicitar Prestacion</h3>
            <button onClick={() => { setShowForm(false); setValidacion(null); setError(''); }}><X size={20} className="text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Prestacion</label>
              <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Seleccionar...</option>
                {catalogo.map(c => <option key={c.tipo} value={c.tipo}>{c.nombre}</option>)}
              </select>
            </div>

            {selectedCatalogo && (
              <div className="md:col-span-2 bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
                <p className="font-medium text-blue-700 mb-1">{selectedCatalogo.descripcion}</p>
                {selectedCatalogo.dias_maximos && <p className="text-blue-600">Max: {selectedCatalogo.dias_maximos} dias habiles</p>}
                <p className="text-blue-600 mt-1 font-medium">Documentos requeridos:</p>
                {selectedCatalogo.documentos_requeridos.map((d, i) => <p key={i} className="text-blue-600 ml-2">- {d}</p>)}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Inicio</label>
              <input type="date" value={form.fecha_inicio} onChange={e => setForm({...form, fecha_inicio: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Fin</label>
              <input type="date" value={form.fecha_fin} onChange={e => setForm({...form, fecha_fin: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
              <textarea value={form.motivo} onChange={e => setForm({...form, motivo: e.target.value})} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
          </div>

          {error && <div className="mt-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}

          {validacion && (
            <div className={`mt-3 px-4 py-3 rounded-lg text-sm ${validacion.valido ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>
              {validacion.valido ? (
                <p className="font-medium">Validacion exitosa. Puedes enviar la solicitud.</p>
              ) : (
                <div>
                  <p className="font-medium">No se puede solicitar:</p>
                  {validacion.errores.map((e, i) => <p key={i}>- {e}</p>)}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3 mt-4">
            <button onClick={handleValidar} disabled={!form.tipo || !form.fecha_inicio || !form.fecha_fin} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 disabled:opacity-50">
              Validar
            </button>
            <button onClick={handleCrear} disabled={loading || !form.tipo || !form.fecha_inicio || !form.fecha_fin} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Enviando...' : 'Enviar Solicitud'}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Tipo</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Periodo</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Dias</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Estado</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Fecha</th>
              {isAdmin && <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {prestaciones.map(p => (
              <tr key={p.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">{p.tipo}</td>
                <td className="px-4 py-3 text-sm">{p.fecha_inicio} - {p.fecha_fin}</td>
                <td className="px-4 py-3 text-sm">{p.dias_solicitados || '-'}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    p.estado === 'Pendiente' ? 'bg-amber-100 text-amber-700' :
                    p.estado === 'Aprobada' ? 'bg-green-100 text-green-700' :
                    'bg-red-100 text-red-700'
                  }`}>{p.estado}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(p.created_at).toLocaleDateString()}</td>
                {isAdmin && (
                  <td className="px-4 py-3 text-sm">
                    {p.estado === 'Pendiente' && (
                      <div className="flex gap-2">
                        <button onClick={() => handleAprobar(p.id)} className="text-green-600 hover:text-green-700" title="Aprobar"><Check size={18} /></button>
                        <button onClick={() => handleRechazar(p.id)} className="text-red-600 hover:text-red-700" title="Rechazar"><XCircle size={18} /></button>
                      </div>
                    )}
                  </td>
                )}
              </tr>
            ))}
            {prestaciones.length === 0 && (
              <tr><td colSpan={isAdmin ? 6 : 5} className="px-4 py-8 text-center text-gray-400">No hay prestaciones</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
