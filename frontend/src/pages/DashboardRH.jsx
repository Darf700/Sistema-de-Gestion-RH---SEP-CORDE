import { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Users, FileText, Gift, AlertTriangle } from 'lucide-react';
import Layout from '../components/layout/Layout';
import api from '../services/api';
import EmpleadosPage from './Empleados';
import JustificantesPage from './Justificantes';
import PrestacionesPage from './Prestaciones';
import DocumentosPage from './Documentos';
import AdeudosPage from './Adeudos';
import NotificacionesPage from './Notificaciones';
import ReportesPage from './Reportes';

function DashboardRHHome() {
  const [stats, setStats] = useState({ empleados: 0, prestPendientes: 0, adeudos: 0 });

  useEffect(() => {
    Promise.all([
      api.get('/api/empleados').catch(() => ({ data: [] })),
      api.get('/api/prestaciones?estado=Pendiente').catch(() => ({ data: [] })),
      api.get('/api/adeudos?estado=Pendiente').catch(() => ({ data: [] })),
    ]).then(([emp, prest, ad]) => {
      setStats({
        empleados: emp.data.length,
        prestPendientes: prest.data.length,
        adeudos: ad.data.length,
      });
    });
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard RH</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-blue-100 p-2 rounded-lg"><Users size={20} className="text-blue-600" /></div>
            <h3 className="font-semibold text-gray-700">Empleados Activos</h3>
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.empleados}</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-amber-100 p-2 rounded-lg"><Gift size={20} className="text-amber-600" /></div>
            <h3 className="font-semibold text-gray-700">Prestaciones Pendientes</h3>
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.prestPendientes}</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-red-100 p-2 rounded-lg"><AlertTriangle size={20} className="text-red-600" /></div>
            <h3 className="font-semibold text-gray-700">Adeudos Pendientes</h3>
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.adeudos}</p>
        </div>
      </div>
    </div>
  );
}

export default function DashboardRH() {
  return (
    <Layout>
      <Routes>
        <Route index element={<DashboardRHHome />} />
        <Route path="empleados" element={<EmpleadosPage />} />
        <Route path="justificantes" element={<JustificantesPage />} />
        <Route path="prestaciones" element={<PrestacionesPage />} />
        <Route path="documentos" element={<DocumentosPage />} />
        <Route path="adeudos" element={<AdeudosPage />} />
        <Route path="reportes" element={<ReportesPage />} />
        <Route path="notificaciones" element={<NotificacionesPage />} />
      </Routes>
    </Layout>
  );
}
