import { BarChart3 } from 'lucide-react';

export default function ReportesPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Reportes</h2>
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
        <BarChart3 size={48} className="text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">Modulo de reportes - Se implementara en la Fase 4</p>
        <p className="text-sm text-gray-400 mt-2">Ausentismo, dias economicos, prestaciones, exportacion Excel/PDF</p>
      </div>
    </div>
  );
}
