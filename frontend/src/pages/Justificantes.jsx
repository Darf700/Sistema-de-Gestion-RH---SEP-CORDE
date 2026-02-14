import { useEffect, useState } from 'react';
import { FileText, Plus, X } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const TIPOS = [
  { value: 'Dia Economico', label: 'Dia Economico' },
  { value: 'Permiso por Horas', label: 'Permiso por Horas' },
  { value: 'ISSTEP', label: 'ISSTEP' },
  { value: 'Comision Todo el Dia', label: 'Comision Todo el Dia' },
  { value: 'Comision Entrada', label: 'Comision Entrada' },
  { value: 'Comision Salida', label: 'Comision Salida' },
];

export default function JustificantesPage() {
  const { isAdmin } = useAuth();
  const [justificantes, setJustificantes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ tipo: '', fecha_inicio: '', fecha_fin: '', motivo: '', lugar: '' });
  const [validacion, setValidacion] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchJustificantes = () => {
    api.get('/api/justificantes').then(r => setJustificantes(r.data)).catch(() => {});
  };

  useEffect(() => { fetchJustificantes(); }, []);

  const handleValidar = async () => {
    setValidacion(null);
    setError('');
    try {
      const payload = { tipo: form.tipo, fecha_inicio: form.fecha_inicio };
      if (form.fecha_fin) payload.fecha_fin = form.fecha_fin;
      const r = await api.post('/api/justificantes/validar', payload);
      setValidacion(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al validar');
    }
  };

  const handleCrear = async () => {
    setError('');
    setLoading(true);
    try {
      const payload = { tipo: form.tipo, fecha_inicio: form.fecha_inicio };
      if (form.fecha_fin) payload.fecha_fin = form.fecha_fin;
      if (form.motivo) payload.motivo = form.motivo;
      if (form.lugar) payload.lugar = form.lugar;
      await api.post('/api/justificantes', payload);
      setShowForm(false);
      setForm({ tipo: '', fecha_inicio: '', fecha_fin: '', motivo: '', lugar: '' });
      setValidacion(null);
      fetchJustificantes();
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al crear justificante');
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Justificantes</h2>
        {!isAdmin && (
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Plus size={18} /> Nuevo Justificante
          </button>
        )}
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-gray-700">Nuevo Justificante</h3>
            <button onClick={() => { setShowForm(false); setValidacion(null); setError(''); }}><X size={20} className="text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Seleccionar...</option>
                {TIPOS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Inicio</label>
              <input type="date" value={form.fecha_inicio} onChange={e => setForm({...form, fecha_inicio: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
            {form.tipo && !['Dia Economico', 'Permiso por Horas'].includes(form.tipo) && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Fin</label>
                <input type="date" value={form.fecha_fin} onChange={e => setForm({...form, fecha_fin: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
              </div>
            )}
            {form.tipo?.includes('Comision') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Lugar</label>
                <input type="text" value={form.lugar} onChange={e => setForm({...form, lugar: e.target.value})} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
              </div>
            )}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
              <textarea value={form.motivo} onChange={e => setForm({...form, motivo: e.target.value})} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2" />
            </div>
          </div>

          {error && <div className="mt-3 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">{error}</div>}

          {validacion && (
            <div className={`mt-3 px-4 py-3 rounded-lg text-sm ${validacion.valido ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>
              {validacion.valido ? (
                <div>
                  <p className="font-medium">Validacion exitosa</p>
                  {validacion.fecha_inicio_calculada && <p>Periodo: {validacion.fecha_inicio_calculada} al {validacion.fecha_fin_calculada}</p>}
                </div>
              ) : (
                <div>
                  <p className="font-medium">No se puede generar:</p>
                  {validacion.errores.map((e, i) => <p key={i}>- {e}</p>)}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3 mt-4">
            <button onClick={handleValidar} disabled={!form.tipo || !form.fecha_inicio} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 disabled:opacity-50">
              Validar
            </button>
            <button onClick={handleCrear} disabled={loading || !form.tipo || !form.fecha_inicio} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Generando...' : 'Generar Justificante'}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Tipo</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Fecha Inicio</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Fecha Fin</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Estado</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Creado</th>
            </tr>
          </thead>
          <tbody>
            {justificantes.map(j => (
              <tr key={j.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">{j.tipo}</td>
                <td className="px-4 py-3 text-sm">{j.fecha_inicio}</td>
                <td className="px-4 py-3 text-sm">{j.fecha_fin}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    j.estado === 'Generado' ? 'bg-blue-100 text-blue-700' :
                    j.estado === 'Entregado' ? 'bg-green-100 text-green-700' :
                    'bg-amber-100 text-amber-700'
                  }`}>{j.estado}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(j.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {justificantes.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No hay justificantes</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
