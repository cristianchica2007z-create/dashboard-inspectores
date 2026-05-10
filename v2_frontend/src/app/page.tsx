"use client";

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  LayoutDashboard, 
  Users, 
  AlertTriangle, 
  TrendingUp,
  Search,
  Settings,
  Bell
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [inspections, setInspections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // NOTA: En un entorno de producción, estos valores vendrían de variables de entorno o login
  const REPO = "cristianchica2007z-create/dashboard-inspectores";
  const TOKEN = "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";

  useEffect(() => {
    setMounted(true);
    fetchData();
    const interval = setInterval(fetchData, 60000); // Actualizar cada minuto
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Intentamos obtener el token de los secrets si es posible, sino usamos el backend configurado
      const summaryRes = await fetch(`http://localhost:8000/summary?repo=${REPO}&token=${TOKEN}`);
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      const inspRes = await fetch(`http://localhost:8000/inspections?repo=${REPO}&token=${TOKEN}`);
      const inspData = await inspRes.json();
      setInspections(inspData);
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <div className="flex min-h-screen font-sans text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 glass border-r border-white/5 hidden md:flex flex-col p-6 fixed h-full">
        <div className="flex items-center gap-3 mb-10 px-2">
          <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center glow-green">
            <TrendingUp className="text-white w-6 h-6" />
          </div>
          <span className="font-extrabold text-xl tracking-tight text-white">E&C <span className="text-emerald-400">V2</span></span>
        </div>

        <nav className="space-y-2 flex-1">
          <NavItem icon={<LayoutDashboard size={20} />} label="Dashboard" active />
          <NavItem icon={<Users size={20} />} label="Inspectores" />
          <NavItem icon={<MapPin size={20} />} label="Zonas" />
          <NavItem icon={<BarChart3 size={20} />} label="Reportes" />
        </nav>

        <div className="pt-6 border-t border-white/5">
          <NavItem icon={<Settings size={20} />} label="Configuración" />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 p-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-black text-white mb-1">Seguimiento Operativo</h1>
            <p className="text-slate-400">Control de inspecciones en tiempo real</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input 
                type="text" 
                placeholder="Buscar contrato..." 
                className="bg-slate-900/50 border border-white/10 rounded-full py-2 pl-10 pr-4 w-64 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
              />
            </div>
            <button className="p-2 glass rounded-full hover:bg-white/10 transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-slate-950"></span>
            </button>
            <div className="flex items-center gap-3 glass px-4 py-2 rounded-full border-white/10">
              <div className="w-8 h-8 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-400 font-bold text-xs">
                CC
              </div>
              <span className="text-sm font-medium text-slate-200">Cristian C.</span>
            </div>
          </div>
        </header>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <KPICard 
            icon={<LayoutDashboard className="text-emerald-400" />} 
            label="Total Inspecciones" 
            value={loading ? "..." : summary?.total_inspecciones || "0"} 
            trend={loading ? "" : `Carga del día: ${summary?.fecha || ""}`}
            delay={0.1}
          />
          <KPICard 
            icon={<CheckCircle2 className="text-emerald-400" />} 
            label="Efectivas" 
            value={loading ? "..." : summary?.efectivas || "0"} 
            trend={loading ? "" : `${summary?.pct_efectividad || "0"}% efectividad`}
            delay={0.2}
          />
          <KPICard 
            icon={<Clock className="text-blue-400" />} 
            label="Prom. Recorrido" 
            value={loading ? "..." : summary?.promedio_recorrido || "—"} 
            trend="Rendimiento logístico"
            delay={0.3}
          />
          <KPICard 
            icon={<AlertTriangle className="text-amber-400" />} 
            label="Zonas Activas" 
            value={loading ? "..." : "7"} 
            trend="Cobertura total"
            delay={0.4}
          />
        </div>

        {/* Table Mockup */}
        <div className="glass rounded-3xl overflow-hidden border-white/5">
          <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/5">
            <h2 className="text-xl font-bold text-white">Inspecciones del Día</h2>
            <button className="text-sm text-emerald-400 font-semibold hover:underline">Ver todo</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="text-slate-500 text-xs uppercase tracking-wider">
                  <th className="px-6 py-4">Inspector</th>
                  <th className="px-6 py-4">Contrato</th>
                  <th className="px-6 py-4">Hora Inicio</th>
                  <th className="px-6 py-4">Estado</th>
                  <th className="px-6 py-4">Puntualidad</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-slate-500">Cargando datos operativos...</td>
                  </tr>
                ) : inspections.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-slate-500">No hay inspecciones registradas hoy.</td>
                  </tr>
                ) : (
                  inspections.map((item, idx) => (
                    <TableRow 
                      key={idx}
                      name={item.inspector} 
                      contract={item.contrato} 
                      time={item["hora inicio"]} 
                      status={item.estado} 
                      punctuality={item.estado_puntualidad}
                      color={item.estado_puntualidad === 'Puntual' ? 'emerald' : 'amber'}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) {
  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all ${
      active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:text-white hover:bg-white/5'
    }`}>
      {icon}
      <span className="font-semibold text-sm">{label}</span>
    </div>
  );
}

function KPICard({ icon, label, value, trend, delay, warning = false }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="glass p-6 rounded-3xl relative overflow-hidden group hover:border-white/20 transition-all"
    >
      <div className={`absolute top-0 right-0 w-24 h-24 blur-3xl -mr-12 -mt-12 transition-all ${
        warning ? 'bg-amber-500/10 group-hover:bg-amber-500/20' : 'bg-emerald-500/10 group-hover:bg-emerald-500/20'
      }`}></div>
      <div className="flex justify-between items-start mb-4">
        <div className="p-3 bg-slate-900/50 rounded-2xl border border-white/5 group-hover:scale-110 transition-transform">
          {icon}
        </div>
      </div>
      <div>
        <p className="text-slate-400 text-sm font-medium mb-1">{label}</p>
        <h3 className="text-3xl font-black text-white">{value}</h3>
        <p className={`text-xs mt-2 font-bold ${warning ? 'text-amber-400' : 'text-emerald-400'}`}>{trend}</p>
      </div>
    </motion.div>
  );
}

function TableRow({ name, contract, time, status, punctuality, color }: any) {
  return (
    <tr className="hover:bg-white/5 transition-colors cursor-pointer group">
      <td className="px-6 py-4">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 bg-${color}-500/10 rounded-full flex items-center justify-center text-${color}-400 font-bold text-xs`}>
            {name.split(' ')[0][0]}{name.split(' ')[1]?.[0]}
          </div>
          <span className="font-bold text-white text-sm">{name}</span>
        </div>
      </td>
      <td className="px-6 py-4 text-slate-400 font-mono text-sm">{contract}</td>
      <td className="px-6 py-4 text-slate-400 text-sm">{time}</td>
      <td className="px-6 py-4">
        <span className="px-3 py-1 bg-white/5 rounded-full text-xs font-bold text-slate-300">
          {status}
        </span>
      </td>
      <td className="px-6 py-4">
        <div className={`flex items-center gap-2 text-${color}-400 font-bold text-xs`}>
          <div className={`w-1.5 h-1.5 bg-${color}-400 rounded-full animate-pulse`}></div>
          {punctuality}
        </div>
      </td>
    </tr>
  );
}
