import { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { FileText, Gift, AlertTriangle, Clock } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import PrestacionesPage from './Prestaciones';
import DocumentosPage from './Documentos';
import AdeudosPage from './Adeudos';
import NotificacionesPage from './Notificaciones';
import JustificantesPage from './Justificantes';

function DashboardHome() {
  const { user } = useAuth();
  const [contadores, setContadores] = useState(null);
  const [adeudos, setAdeudos] = useState([]);

  useEffect(() => {
    if (user?.empleado_id) {
      api.get(`/api/empleados/${user.empleado_id}/contadores`).then(r => setContadores(r.data)).catch(() => {});
      api.get('/api/adeudos?estado=Pendiente').then(r => setAdeudos(r.data)).catch(() => {});
    }
  }, [user]);

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Mi Dashboard</h2>

      {adeudos.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 text-amber-700 font-medium mb-2">
            <AlertTriangle size={20} />
            Tienes {adeudos.length} adeudo(s) pendiente(s)
          </div>
          {adeudos.map(a => (
            <p key={a.id} className="text-sm text-amber-600 ml-7">- {a.tipo}: {a.descripcion}</p>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-blue-100 p-2 rounded-lg"><FileText size={20} className="text-blue-600" /></div>
            <h3 className="font-semibold text-gray-700">Dias Economicos</h3>
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {contadores ? `${contadores.solicitudes_economicos}/3` : '--'}
          </p>
          <p className="text-sm text-gray-500 mt-1">solicitudes usadas este anio</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-green-100 p-2 rounded-lg"><Clock size={20} className="text-green-600" /></div>
            <h3 className="font-semibold text-gray-700">Permisos por Horas</h3>
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {contadores ? `${contadores.permisos_horas_q1 + contadores.permisos_horas_q2}` : '--'}
          </p>
          <p className="text-sm text-gray-500 mt-1">usados este anio</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-purple-100 p-2 rounded-lg"><Gift size={20} className="text-purple-600" /></div>
            <h3 className="font-semibold text-gray-700">Prestaciones</h3>
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {contadores ? `${contadores.cuidados_maternos_usados + contadores.cuidados_medicos_usados}` : '--'}
          </p>
          <p className="text-sm text-gray-500 mt-1">dias usados este anio</p>
        </div>
      </div>
    </div>
  );
}

export default function DashboardEmpleado() {
  return (
    <Layout>
      <Routes>
        <Route index element={<DashboardHome />} />
        <Route path="justificantes" element={<JustificantesPage />} />
        <Route path="prestaciones" element={<PrestacionesPage />} />
        <Route path="documentos" element={<DocumentosPage />} />
        <Route path="adeudos" element={<AdeudosPage />} />
        <Route path="notificaciones" element={<NotificacionesPage />} />
      </Routes>
    </Layout>
  );
}
