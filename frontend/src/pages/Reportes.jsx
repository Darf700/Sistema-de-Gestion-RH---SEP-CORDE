import { useState, useEffect } from 'react';
import { BarChart3, Download, Search, Calendar, Users, FileText, AlertTriangle, Clock, PieChart } from 'lucide-react';
import api from '../services/api';

const TABS = [
  { key: 'ausentismo', label: 'Ausentismo', icon: Users },
  { key: 'dias-economicos', label: 'Dias Economicos', icon: Calendar },
  { key: 'permisos-horas', label: 'Permisos Horas', icon: Clock },
  { key: 'prestaciones', label: 'Prestaciones', icon: FileText },
  { key: 'justificantes', label: 'Justificantes', icon: FileText },
  { key: 'adeudos', label: 'Adeudos', icon: AlertTriangle },
  { key: 'extemporaneos', label: 'Extemporaneos', icon: AlertTriangle },
  { key: 'estadisticas-justificantes', label: 'Estadisticas', icon: PieChart },
];

const TIPOS_JUSTIFICANTE = [
  'Dia Economico', 'Permiso por Horas', 'ISSTEP',
  'Comision Todo el Dia', 'Comision Entrada', 'Comision Salida',
];

const TIPOS_PRESTACION = [
  'Licencia Medica', 'Cuidados Maternos/Paternos', 'Cuidados Medicos Familiares',
  'Fallecimiento de Familiar', 'Media Hora de Tolerancia', 'Licencia por Nupcias', 'Licencia por Paternidad',
];

const ESTADOS_PRESTACION = ['Pendiente', 'Aprobada', 'Rechazada'];
const ESTADOS_ADEUDO = ['Pendiente', 'Resuelto'];

const hoy = new Date();
const inicioAnio = `${hoy.getFullYear()}-01-01`;
const hoyStr = hoy.toISOString().split('T')[0];

export default function ReportesPage() {
  const [activeTab, setActiveTab] = useState('ausentismo');
  const [filtros, setFiltros] = useState({
    fecha_inicio: inicioAnio,
    fecha_fin: hoyStr,
    anio: hoy.getFullYear(),
    tipo: '',
    estado: '',
    empleado_id: '',
  });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [empleados, setEmpleados] = useState([]);

  useEffect(() => {
    api.get('/api/empleados').then(r => setEmpleados(r.data)).catch(() => {});
  }, []);

  const usaPeriodo = ['ausentismo', 'prestaciones', 'justificantes', 'extemporaneos', 'estadisticas-justificantes'].includes(activeTab);
  const usaAnio = ['dias-economicos', 'permisos-horas'].includes(activeTab);

  const handleConsultar = async () => {
    setLoading(true);
    setError('');
    setData(null);
    try {
      const params = {};
      if (usaPeriodo) {
        params.fecha_inicio = filtros.fecha_inicio;
        params.fecha_fin = filtros.fecha_fin;
      }
      if (usaAnio) {
        params.anio = filtros.anio;
      }
      if (filtros.tipo && ['prestaciones', 'justificantes'].includes(activeTab)) {
        params.tipo = filtros.tipo;
      }
      if (filtros.estado && ['prestaciones', 'adeudos'].includes(activeTab)) {
        params.estado = filtros.estado;
      }
      if (filtros.empleado_id && ['ausentismo', 'justificantes'].includes(activeTab)) {
        params.empleado_id = filtros.empleado_id;
      }

      const r = await api.get(`/api/reportes/${activeTab}`, { params });
      setData(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al consultar reporte');
    }
    setLoading(false);
  };

  const handleExport = async () => {
    try {
      const params = { reporte: activeTab };
      if (usaPeriodo) {
        params.fecha_inicio = filtros.fecha_inicio;
        params.fecha_fin = filtros.fecha_fin;
      }
      if (usaAnio) {
        params.anio = filtros.anio;
      }
      if (filtros.tipo && ['prestaciones', 'justificantes'].includes(activeTab)) {
        params.tipo = filtros.tipo;
      }
      if (filtros.estado && ['prestaciones', 'adeudos'].includes(activeTab)) {
        params.estado = filtros.estado;
      }
      if (filtros.empleado_id && ['ausentismo', 'justificantes'].includes(activeTab)) {
        params.empleado_id = filtros.empleado_id;
      }

      const r = await api.get('/api/reportes/export', { params, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([r.data]));
      const link = document.createElement('a');
      link.href = url;
      const disposition = r.headers['content-disposition'];
      const filename = disposition ? disposition.split('filename=')[1].replace(/"/g, '') : `${activeTab}.xlsx`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError('Error al exportar');
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setData(null);
    setError('');
  };

  const renderFiltros = () => (
    <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
      <div className="flex flex-wrap gap-3 items-end">
        {usaPeriodo && (
          <>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Fecha Inicio</label>
              <input type="date" value={filtros.fecha_inicio} onChange={e => setFiltros({ ...filtros, fecha_inicio: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Fecha Fin</label>
              <input type="date" value={filtros.fecha_fin} onChange={e => setFiltros({ ...filtros, fecha_fin: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </>
        )}
        {usaAnio && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Anio</label>
            <input type="number" value={filtros.anio} onChange={e => setFiltros({ ...filtros, anio: parseInt(e.target.value) || hoy.getFullYear() })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-24" />
          </div>
        )}
        {['ausentismo', 'justificantes'].includes(activeTab) && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Empleado</label>
            <select value={filtros.empleado_id} onChange={e => setFiltros({ ...filtros, empleado_id: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todos</option>
              {empleados.map(emp => <option key={emp.id} value={emp.id}>{emp.nombre_completo}</option>)}
            </select>
          </div>
        )}
        {activeTab === 'justificantes' && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Tipo</label>
            <select value={filtros.tipo} onChange={e => setFiltros({ ...filtros, tipo: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todos</option>
              {TIPOS_JUSTIFICANTE.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        )}
        {activeTab === 'prestaciones' && (
          <>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Tipo</label>
              <select value={filtros.tipo} onChange={e => setFiltros({ ...filtros, tipo: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Todos</option>
                {TIPOS_PRESTACION.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Estado</label>
              <select value={filtros.estado} onChange={e => setFiltros({ ...filtros, estado: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Todos</option>
                {ESTADOS_PRESTACION.map(e => <option key={e} value={e}>{e}</option>)}
              </select>
            </div>
          </>
        )}
        {activeTab === 'adeudos' && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Estado</label>
            <select value={filtros.estado} onChange={e => setFiltros({ ...filtros, estado: e.target.value })} className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todos</option>
              {ESTADOS_ADEUDO.map(e => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>
        )}
        <button onClick={handleConsultar} disabled={loading} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">
          <Search size={16} /> {loading ? 'Consultando...' : 'Consultar'}
        </button>
        <button onClick={handleExport} disabled={!data} className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm">
          <Download size={16} /> Exportar Excel
        </button>
      </div>
    </div>
  );

  const renderResumen = () => {
    if (!data) return null;

    const cards = [];
    if (activeTab === 'ausentismo') {
      cards.push({ label: 'Empleados', value: data.total_registros });
      const totalAus = data.datos.reduce((s, d) => s + d.total_ausencias, 0);
      cards.push({ label: 'Total Ausencias', value: totalAus });
    } else if (activeTab === 'dias-economicos') {
      cards.push({ label: 'Empleados', value: data.total_empleados });
      const totalUsados = data.datos.reduce((s, d) => s + d.dias_usados, 0);
      cards.push({ label: 'Dias Usados (total)', value: totalUsados });
    } else if (activeTab === 'permisos-horas') {
      cards.push({ label: 'Empleados', value: data.total_empleados });
      const totalPerm = data.datos.reduce((s, d) => s + d.total_permisos, 0);
      cards.push({ label: 'Total Permisos', value: totalPerm });
    } else if (activeTab === 'prestaciones') {
      cards.push({ label: 'Total Prestaciones', value: data.total_registros });
      Object.entries(data.por_estado || {}).forEach(([k, v]) => cards.push({ label: k, value: v }));
    } else if (activeTab === 'justificantes' || activeTab === 'extemporaneos') {
      cards.push({ label: 'Total Justificantes', value: data.total_registros });
      Object.entries(data.por_estado || {}).forEach(([k, v]) => cards.push({ label: k, value: v }));
    } else if (activeTab === 'adeudos') {
      cards.push({ label: 'Total Adeudos', value: data.total_registros });
      cards.push({ label: 'Total Dias Pendientes', value: data.total_dias_pendientes || 0 });
    } else if (activeTab === 'estadisticas-justificantes') {
      cards.push({ label: 'Total Justificantes', value: data.total_justificantes });
    }

    if (cards.length === 0) return null;

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        {cards.map((c, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{c.label}</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{c.value}</p>
          </div>
        ))}
      </div>
    );
  };

  const TABLE_CONFIGS = {
    'ausentismo': {
      headers: ['Empleado', 'Total Ausencias', 'Dias Eco.', 'Permisos Hrs.', 'ISSTEP', 'Comisiones'],
      row: d => [d.nombre_completo, d.total_ausencias, d.dias_economicos, d.permisos_horas, d.isstep, d.comisiones],
    },
    'dias-economicos': {
      headers: ['Empleado', 'Dias Usados', 'Dias Disponibles', 'Solicitudes', 'Ultima Solicitud'],
      row: d => [d.nombre_completo, d.dias_usados, d.dias_disponibles, d.solicitudes, d.fecha_ultima_solicitud || '-'],
    },
    'permisos-horas': {
      headers: ['Empleado', 'Permisos Q1', 'Permisos Q2', 'Total'],
      row: d => [d.nombre_completo, d.permisos_q1, d.permisos_q2, d.total_permisos],
    },
    'prestaciones': {
      headers: ['Empleado', 'Tipo', 'Fecha Inicio', 'Fecha Fin', 'Dias', 'Estado', 'Fecha Solicitud'],
      row: d => [d.nombre_completo, d.tipo, d.fecha_inicio, d.fecha_fin, d.dias_solicitados || '-', d.estado, d.fecha_solicitud],
    },
    'justificantes': {
      headers: ['Empleado', 'Tipo', 'Fecha Inicio', 'Fecha Fin', 'Dias', 'Estado', 'Fecha Gen.'],
      row: d => [d.nombre_completo, d.tipo, d.fecha_inicio, d.fecha_fin, d.dias_solicitados || '-', d.estado, d.fecha_generacion || '-'],
    },
    'adeudos': {
      headers: ['Empleado', 'Tipo', 'Descripcion', 'Dias', 'Estado', 'Fecha'],
      row: d => [d.nombre_completo, d.tipo, d.descripcion, d.dias_debe || 0, d.estado, new Date(d.fecha_marcado).toLocaleDateString()],
    },
    'extemporaneos': {
      headers: ['Empleado', 'Tipo', 'Fecha Inicio', 'Fecha Fin', 'Dias', 'Fecha Gen.'],
      row: d => [d.nombre_completo, d.tipo, d.fecha_inicio, d.fecha_fin, d.dias_solicitados || '-', d.fecha_generacion || '-'],
    },
    'estadisticas-justificantes': {
      headers: ['Categoria', 'Valor', 'Conteo'],
      row: d => [d.categoria, d.valor, d.conteo],
    },
  };

  const renderTabla = () => {
    if (!data) return null;

    const config = TABLE_CONFIGS[activeTab];
    const items = data.datos || [];

    return (
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {config.headers.map((h, i) => (
                  <th key={i} className="text-left px-4 py-3 text-sm font-medium text-gray-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => {
                const cells = config.row(item);
                return (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    {cells.map((cell, ci) => (
                      <td key={ci} className="px-4 py-3 text-sm text-gray-700">{cell}</td>
                    ))}
                  </tr>
                );
              })}
              {items.length === 0 && (
                <tr>
                  <td colSpan={config.headers.length} className="px-4 py-8 text-center text-gray-400">
                    No hay datos para mostrar
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <BarChart3 size={28} className="text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">Reportes</h2>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1 mb-4 bg-gray-100 rounded-xl p-1">
        {TABS.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => handleTabChange(tab.key)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {renderFiltros()}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      {renderResumen()}
      {renderTabla()}
    </div>
  );
}
