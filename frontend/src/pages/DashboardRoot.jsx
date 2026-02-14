import { Routes, Route } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import UsuariosPage from './Usuarios';

function AdminHome() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Panel de Administracion</h2>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <p className="text-gray-600">Panel de administracion del sistema. Usa el menu lateral para gestionar usuarios y configuracion.</p>
      </div>
    </div>
  );
}

export default function DashboardRoot() {
  return (
    <Layout>
      <Routes>
        <Route index element={<AdminHome />} />
        <Route path="usuarios" element={<UsuariosPage />} />
      </Routes>
    </Layout>
  );
}
