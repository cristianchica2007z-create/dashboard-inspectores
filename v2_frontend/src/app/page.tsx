"use client";

import React, { useState, useEffect, useMemo, useRef } from 'react';
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
  Bell,
  Calendar,
  ShieldCheck,
  Package,
  ClipboardList,
  Target,
  Navigation,
  Moon,
  Sun,
  RefreshCw,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  ArrowUpDown,
  Check,
  Filter,
  Maximize2,
  Minimize2,
  X,
  FileText,
  AlertCircle,
  Activity,
  Trophy,
  TrendingDown,
  Car,
  Timer,
  Compass,
  UploadCloud,
  Briefcase,
  Factory,
  Pin,
  User,
  Home,
  FileSpreadsheet,
  CheckCircle,
  Loader2,
  Medal,
  Award,
  Zap,
  ListFilter,
  Eye,
  Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell,
  LabelList,
  LineChart,
  Line,
  CartesianGrid,
  Legend
} from 'recharts';

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [inspections, setInspections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // NAVIGATION STATE
  const [activeMainTab, setActiveMainTab] = useState('OPERACIÓN');
  const [activeSubTab, setActiveSubTab] = useState('Seguimiento Diario');
  const [expandedMainTabs, setExpandedMainTabs] = useState<string[]>(['OPERACIÓN', 'CARGAR DATOS']);
  
  const [darkMode, setDarkMode] = useState(true);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  
  const [performanceReport, setPerformanceReport] = useState<any>(null);
  const [inactiveInspectors, setInactiveInspectors] = useState<any[]>([]);
  
  const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' | null }>({ key: 'efectividad_pct', direction: 'desc' });
  
  const [config, setConfig] = useState<any>({ fechas: [], supervisores: [] });
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedSups, setSelectedSups] = useState<string[]>(['TODOS']);
  
  // MULTI-DATE STATE FOR MONTHLY
  const [selectedMonthlyDates, setSelectedMonthlyDates] = useState<string[]>([]);
  const [isMonthlyDateMenuOpen, setIsMonthlyDateMenuOpen] = useState(false);
  const monthlyDateMenuRef = useRef<HTMLDivElement>(null);

  const [isSupMenuOpen, setIsSupMenuOpen] = useState(false);
  const supMenuRef = useRef<HTMLDivElement>(null);

  // AGENDAS STATE
  const [agendasData, setAgendasData] = useState<any[]>([]);
  const [agendasKPIs, setAgendasKPIs] = useState<any>({ alerta: 0, proximas: 0, finalizadas: 0 });
  const [agendasZonas, setAgendasZonas] = useState<string[]>([]);
  const [selectedZona, setSelectedZona] = useState('TODAS');
  const [activeAgendasView, setActiveAgendasView] = useState('🚨 Alertas');
  const [selectedAgenda, setSelectedAgenda] = useState<any>(null);

  // UPLOAD STATE
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' });

  const REPO = "cristianchica2007z-create/dashboard-inspectores";
  const TOKEN = "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";

  useEffect(() => {
    setMounted(true);
    fetchConfig();
    
    const handleClickOutside = (event: MouseEvent) => {
      if (supMenuRef.current && !supMenuRef.current.contains(event.target as Node)) setIsSupMenuOpen(false);
      if (monthlyDateMenuRef.current && !monthlyDateMenuRef.current.contains(event.target as Node)) setIsMonthlyDateMenuOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (mounted) {
      if (activeSubTab === 'Seguimiento agendas') fetchAgendas();
      else if (selectedDate || selectedMonthlyDates.length > 0) fetchData();
    }
  }, [selectedDate, selectedMonthlyDates, selectedSups, activeMainTab, activeSubTab]);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`http://localhost:8000/config?repo=${REPO}&token=${TOKEN}`);
      if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
      const data = await res.json();
      setConfig(data);
      if (data.fechas.length > 0) {
        setSelectedDate(data.fechas[0]);
        setSelectedMonthlyDates(data.fechas.slice(0, 7));
      }
    } catch (e) { 
      console.error("❌ Error conectando al Backend (Puerto 8000). ¿Está encendido?", e);
      setLoading(false);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const supParam = selectedSups.includes('TODOS') ? 'TODOS' : selectedSups.join(',');
      const fechaParam = activeSubTab === 'Seguimiento Diario' ? selectedDate : selectedMonthlyDates.join(',');
      const queryParams = new URLSearchParams({ repo: REPO, token: TOKEN, fecha: fechaParam, supervisor: supParam }).toString();
      const baseUrl = `http://localhost:8000`;
      const [summaryRes, inspRes, reportRes, inactiveRes] = await Promise.all([
        fetch(`${baseUrl}/summary?${queryParams}`),
        fetch(`${baseUrl}/inspections_agregada?${queryParams}`),
        fetch(`${baseUrl}/performance_report?${queryParams}`),
        fetch(`${baseUrl}/inactive_inspectors?${queryParams}`)
      ]);
      setSummary(await summaryRes.json());
      setInspections(await inspRes.json());
      setPerformanceReport((await reportRes.json()).report);
      setInactiveInspectors(await inactiveRes.json());
      setLoading(false);
    } catch (error) { console.error("Error fetching data:", error); setLoading(false); }
  };

  const fetchAgendas = async (zona?: string) => {
    setLoading(true);
    try {
      const z = zona ?? selectedZona;
      const res = await fetch(`http://localhost:8000/agendas?repo=${REPO}&token=${TOKEN}&zona=${z}`);
      const data = await res.json();
      setAgendasData(data.agendas || []);
      setAgendasKPIs(data.kpis || { alerta: 0, proximas: 0, finalizadas: 0 });
      if (data.zonas && data.zonas.length > 0) setAgendasZonas(['TODAS', ...data.zonas]);
      setLoading(false);
    } catch (e) { console.error(e); setLoading(false); }
  };

  const handleZonaChange = (zona: string) => {
    setSelectedZona(zona);
    fetchAgendas(zona);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus({ type: null, message: '' });
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`http://localhost:8000/upload?repo=${REPO}&token=${TOKEN}`, { method: 'POST', body: formData });
      if (res.ok) {
        setUploadStatus({ type: 'success', message: '¡Archivo actualizado!' });
        setTimeout(() => { fetchConfig(); fetchData(); }, 3000);
      } else {
        const err = await res.json();
        setUploadStatus({ type: 'error', message: `Error: ${err.detail}` });
      }
    } catch (e: any) {
      console.error("Error al subir archivo:", e);
      setUploadStatus({ type: 'error', message: `Error de conexión con el backend: ${e.message || 'Servidor no disponible.'}` });
    }
    finally { setUploading(false); }
  };

  const toggleMainTab = (tab: string) => {
    if (expandedMainTabs.includes(tab)) setExpandedMainTabs(expandedMainTabs.filter(t => t !== tab));
    else setExpandedMainTabs([...expandedMainTabs, tab]);
  };

  const toggleMonthlyDate = (date: string) => {
    if (selectedMonthlyDates.includes(date)) setSelectedMonthlyDates(selectedMonthlyDates.filter(d => d !== date));
    else setSelectedMonthlyDates([...selectedMonthlyDates, date]);
  };

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'desc';
    if (sortConfig.key === key && sortConfig.direction === 'desc') direction = 'asc';
    setSortConfig({ key, direction });
  };

  const sortedInspections = useMemo(() => {
    if (!sortConfig.key || !sortConfig.direction) return inspections;
    return [...inspections].sort((a, b) => {
      let valA = a[sortConfig.key];
      let valB = b[sortConfig.key];
      if (valA === '—' || valA === null) return 1;
      if (valB === '—' || valB === null) return -1;
      if (typeof valA === 'string') { valA = valA.toLowerCase(); valB = valB.toLowerCase(); }
      if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
      if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [inspections, sortConfig]);

  const filteredAgendas = useMemo(() => {
    const ahora = new Date();
    if (activeAgendasView === '✅ Finalizadas') {
      return agendasData.filter(a => a.estado.toUpperCase().includes('FINALIZAD'));
    } else if (activeAgendasView === '⏳ Próximas') {
      return agendasData.filter(a => a.estado.toUpperCase().includes('ASIGNAD') && !a.fecha_de_ejecucion && new Date(a.fecha_de_visita) > ahora);
    } else {
      return agendasData.filter(a => a.estado.toUpperCase().includes('ASIGNAD') && a.estado_alerta === 'ALERTA');
    }
  }, [agendasData, activeAgendasView]);

  const toggleSupervisor = (sup: string) => {
    if (sup === 'TODOS') { setSelectedSups(['TODOS']); return; }
    let newSelected = selectedSups.filter(s => s !== 'TODOS');
    if (newSelected.includes(sup)) {
      newSelected = newSelected.filter(s => s !== sup);
      if (newSelected.length === 0) newSelected = ['TODOS'];
    } else { newSelected = [...newSelected, sup]; }
    setSelectedSups(newSelected);
  };

  if (!mounted) return null;

  const chartData = inspections.map(i => ({ name: i.inspector, total: i.ordenes_efectivas })).sort((a, b) => b.total - a.total);
  const themeClass = darkMode ? 'text-slate-200 bg-[#020617]' : 'text-slate-800 bg-[#f8fafc]';
  const glassClass = darkMode ? 'glass border-white/5' : 'bg-white border-slate-200 shadow-xl';
  const textTitle = darkMode ? 'text-white' : 'text-slate-900';
  const textMuted = darkMode ? 'text-slate-400' : 'text-slate-500';

  const menuConfig = [
    { id: 'OPERACIÓN', icon: <Activity size={20} />, subtabs: [
      { id: 'Seguimiento Diario', icon: <Clock size={14}/> },
      { id: 'Seguimiento Mensual', icon: <Calendar size={14}/> },
      { id: 'Seguimiento agendas', icon: <Briefcase size={14}/> },
      { id: 'SEGUIMIENTO ADICIONALES', icon: <Factory size={14}/> },
      { id: 'Órdenes Asignadas', icon: <Pin size={14}/> }
    ] },
    { id: 'INVENTARIO', icon: <Package size={20} />, subtabs: [{ id: 'Resumen Stock', icon: <Package size={14}/> }] },
    { id: 'SST', icon: <ShieldCheck size={20} />, subtabs: [{ id: 'Cumplimiento', icon: <ShieldCheck size={14}/> }] },
    { id: 'CARGAR DATOS', icon: <UploadCloud size={20} />, subtabs: [{ id: 'Subir Excel', icon: <UploadCloud size={14}/> }] }
  ];

  const isMonthly = activeSubTab === 'Seguimiento Mensual';
  const isAgendas = activeSubTab === 'Seguimiento agendas';

  return (
    <div className={`flex min-h-screen font-sans transition-colors duration-500 ${themeClass}`}>
      {/* SIDEBAR */}
      <motion.aside initial={false} animate={{ width: 280 }} className={`fixed h-full z-50 flex flex-col border-r transition-colors duration-500 overflow-hidden ${darkMode ? 'bg-[#020617] border-white/5' : 'bg-slate-900 border-slate-800 shadow-2xl'}`}>
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center border border-white/10 overflow-hidden"><User className="text-slate-400 w-6 h-6" /></div>
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-emerald-500 uppercase tracking-tighter">Director Operativo</span>
              <span className="text-sm font-bold text-white truncate max-w-[150px]">CRISTIAN ALBERTO CHICA RAMIREZ</span>
              <span className="text-[10px] text-slate-500 font-bold">E&C INGENIERIA</span>
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
          <div className="space-y-1"><div className="flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer text-slate-400 hover:bg-white/5"><Home size={20} /><span className="text-xs font-black uppercase tracking-widest">Principal</span></div></div>
          <div className="space-y-2">
            {menuConfig.map((main) => (
              <div key={main.id} className="space-y-1">
                <div onClick={() => toggleMainTab(main.id)} className={`flex items-center justify-between px-4 py-3 rounded-xl cursor-pointer transition-all ${activeMainTab === main.id ? 'bg-emerald-500/10 text-emerald-400' : 'text-slate-400 hover:bg-white/5'}`}><div className="flex items-center gap-3">{main.icon}<span className="text-xs font-black uppercase tracking-widest">{main.id}</span></div><motion.div animate={{ rotate: expandedMainTabs.includes(main.id) ? 180 : 0 }}><ChevronDown size={16} /></motion.div></div>
                <AnimatePresence>{expandedMainTabs.includes(main.id) && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden pl-10 space-y-1">
                    {main.subtabs.map((sub) => (
                      <div key={sub.id} onClick={() => {setActiveMainTab(main.id); setActiveSubTab(sub.id);}} className={`px-4 py-2 rounded-lg text-[11px] font-bold cursor-pointer transition-all ${activeSubTab === sub.id && activeMainTab === main.id ? 'text-emerald-500 bg-emerald-500/5' : 'text-slate-500 hover:text-slate-300'}`}>{sub.id}</div>
                    ))}
                  </motion.div>
                )}</AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </motion.aside>

      <main className="flex-1 ml-[280px] p-4 md:p-8 transition-all duration-300 overflow-x-hidden">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div><h1 className={`text-3xl font-black mb-1 tracking-tight ${textTitle}`}>{activeSubTab}</h1><p className={`${textMuted} text-sm uppercase font-bold tracking-widest`}>{activeMainTab} — {isMonthly ? 'Análisis Multi-Fecha' : isAgendas ? 'Control de Citas' : 'Control Operativo'}</p></div>
          <div className="flex flex-wrap items-center gap-3">
            <button onClick={() => setDarkMode(!darkMode)} className={`p-2.5 rounded-2xl border ${darkMode ? 'glass border-white/10 text-amber-400' : 'bg-white border-slate-200 text-indigo-600 shadow-sm'}`}>{darkMode ? <Sun size={20} /> : <Moon size={20} />}</button>
            
            {!isAgendas && (
              <>
                {isMonthly ? (
                  <div className="relative" ref={monthlyDateMenuRef}>
                    <button onClick={() => setIsMonthlyDateMenuOpen(!isMonthlyDateMenuOpen)} className={`flex items-center gap-2 px-4 py-2 rounded-2xl border ${darkMode ? 'glass border-white/10 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm'}`}>
                      <ListFilter size={16} className="text-emerald-500" />
                      <span className="text-sm font-bold">{selectedMonthlyDates.length} Días Seleccionados</span>
                      <ChevronDown size={14} className={isMonthlyDateMenuOpen ? 'rotate-180' : ''} />
                    </button>
                    <AnimatePresence>{isMonthlyDateMenuOpen && (
                      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`absolute right-0 mt-2 w-64 rounded-2xl border shadow-2xl z-[100] max-h-80 overflow-y-auto custom-scrollbar ${darkMode ? 'bg-[#0f172a] border-white/10' : 'bg-white border-slate-200'}`}>
                        <div className="p-2 space-y-1">
                          {config.fechas.map((f: string) => (
                            <button key={f} onClick={() => toggleMonthlyDate(f)} className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-[11px] font-bold ${selectedMonthlyDates.includes(f) ? 'bg-emerald-500/10 text-emerald-400' : 'text-slate-500 hover:bg-white/5'}`}>
                              <span>{f}</span>{selectedMonthlyDates.includes(f) && <Check size={14} />}
                            </button>
                          ))}
                        </div>
                      </motion.div>
                    )}</AnimatePresence>
                  </div>
                ) : (
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-2xl border ${darkMode ? 'glass border-white/10' : 'bg-white border-slate-200 shadow-sm'}`}>
                    <Calendar size={16} className="text-emerald-500" />
                    <select value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} className={`bg-transparent text-sm font-bold focus:outline-none cursor-pointer ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {config.fechas.map((f: string) => <option key={f} value={f} className={darkMode ? 'bg-slate-900' : ''}>{f}</option>)}
                    </select>
                  </div>
                )}

                <div className="relative" ref={supMenuRef}>
                  <button onClick={() => setIsSupMenuOpen(!isSupMenuOpen)} className={`flex items-center gap-2 px-4 py-2 rounded-2xl border ${darkMode ? 'glass border-white/10 text-white' : 'bg-white border-slate-200 shadow-sm'}`}>
                    <Users size={16} className="text-blue-500" /><span className="text-sm font-bold">{selectedSups.includes('TODOS') ? 'TODOS' : `${selectedSups.length} Sups.`}</span><ChevronDown size={14} />
                  </button>
                  <AnimatePresence>{isSupMenuOpen && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`absolute right-0 mt-2 w-64 rounded-2xl border shadow-2xl z-[100] max-h-80 overflow-y-auto custom-scrollbar ${darkMode ? 'bg-[#0f172a] border-white/10' : 'bg-white border-slate-200'}`}>
                      <div className="p-2 space-y-1">{config.supervisores.map((sup: string) => (<button key={sup} onClick={() => toggleSupervisor(sup)} className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium ${selectedSups.includes(sup) ? 'bg-blue-500/20 text-blue-400' : 'text-slate-500 hover:bg-white/5'}`}><span className="truncate uppercase">{sup}</span>{selectedSups.includes(sup) && <Check size={16} />}</button>))}</div>
                    </motion.div>
                  )}</AnimatePresence>
                </div>
              </>
            )}
            <button onClick={isAgendas ? fetchAgendas : fetchData} className={`p-2.5 rounded-2xl border ${darkMode ? 'glass border-white/10 text-emerald-400' : 'bg-white border-slate-200 text-emerald-600'}`}><RefreshCw size={20} className={loading ? 'animate-spin' : ''} /></button>
          </div>
        </header>

        <AnimatePresence mode="wait">
          {(activeSubTab === 'Seguimiento Diario' || activeSubTab === 'Seguimiento Mensual') && (
            <motion.div key={activeSubTab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
                <KPICard icon={<Calendar className="text-rose-500" />} label={isMonthly ? "Inicio Prom. (Mes)" : "Inicio Prom."} value={loading ? "..." : summary?.inicio_promedio || "—"} trend={isMonthly ? "Promedio Diario" : "Puntualidad"} delay={0.1} darkMode={darkMode} />
                <KPICard icon={<Calendar className="text-indigo-500" />} label={isMonthly ? "Fin Prom. (Mes)" : "Fin Prom."} value={loading ? "..." : summary?.fin_promedio || "—"} trend={isMonthly ? "Promedio Diario" : "Cierre jornada"} delay={0.2} darkMode={darkMode} />
                <KPICard icon={<Clock className="text-purple-500" />} label="T. Tarea Prom." value={loading ? "..." : summary?.promedio_tarea || "—"} trend="Eficiencia" delay={0.3} darkMode={darkMode} />
                <KPICard icon={<Navigation className="text-amber-500" />} label="Recorrido Prom." value={loading ? "..." : summary?.promedio_recorrido || "—"} trend="Logística" delay={0.4} darkMode={darkMode} />
                <KPICard icon={<ClipboardList className="text-emerald-500" />} label={isMonthly ? "Total Acumulado" : "Total Tareas"} value={loading ? "..." : summary?.total_inspecciones || "0"} trend="Volumen total" delay={0.5} darkMode={darkMode} />
                <KPICard icon={<CheckCircle2 className="text-emerald-500" />} label="Efectivas" value={loading ? "..." : summary?.efectivas || "0"} trend="Válidas" delay={0.6} darkMode={darkMode} />
                <TrendingUpCard value={loading ? "..." : `${summary?.pct_efectividad || "0"}%`} darkMode={darkMode} />
              </div>

              {isMonthly && (
                <div className={`p-4 rounded-3xl border flex items-center justify-between gap-4 ${darkMode ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-emerald-50 border-emerald-100'}`}>
                  <div className="flex items-center gap-3"><div className="p-2 bg-emerald-500 rounded-xl text-white"><UploadCloud size={20} /></div><div><p className={`text-sm font-black ${textTitle}`}>Cargar Bitácora Independiente</p><p className="text-[10px] text-slate-500">Este archivo actualizará los datos del seguimiento mensual.</p></div></div>
                  <label className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-black rounded-xl cursor-pointer transition-all shadow-lg shadow-emerald-500/20">SUBIR ARCHIVO <input type="file" accept=".xlsx" className="hidden" onChange={handleFileUpload} disabled={uploading} /></label>
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className={`lg:col-span-2 rounded-3xl p-6 border ${glassClass}`}><h3 className={`text-lg font-bold mb-4 flex items-center gap-2 ${textTitle}`}><FileText size={20} className="text-blue-500" />{isMonthly ? 'Informe de Desempeño Acumulado' : 'Informe de Desempeño del Día'}</h3>
                  {loading ? (<div className="flex items-center justify-center h-24 text-slate-500 italic">Procesando...</div>) : performanceReport ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8">
                      <ReportItem icon={<Trophy size={14} className="text-amber-500" />} label="Más órdenes efectivas" name={performanceReport.mas_efectivas.name} value={performanceReport.mas_efectivas.val} darkMode={darkMode} />
                      <ReportItem icon={<Clock size={14} className="text-slate-400" />} label="Inicio más tarde prom." name={performanceReport.inicio_mas_tarde.name} value={performanceReport.inicio_mas_tarde.val} darkMode={darkMode} />
                      <ReportItem icon={<TrendingDown size={14} className="text-rose-500" />} label="Menos órdenes efectivas" name={performanceReport.menos_efectivas.name} value={performanceReport.menos_efectivas.val} darkMode={darkMode} />
                      <ReportItem icon={<Compass size={14} className="text-blue-500" />} label="Promedio recorrido extenso" name={performanceReport.recorrido_mas_extenso.name} value={performanceReport.recorrido_mas_extenso.val} darkMode={darkMode} />
                      <ReportItem icon={<Car size={14} className="text-rose-400" />} label="Más órdenes sin recorrido" name={performanceReport.mas_sin_recorrido.name} value={performanceReport.mas_sin_recorrido.val} darkMode={darkMode} />
                      <ReportItem icon={<Timer size={14} className="text-purple-500" />} label="Más tiempo por tarea" name={performanceReport.mas_tiempo_tarea.name} value={performanceReport.mas_tiempo_tarea.val} darkMode={darkMode} />
                    </div>
                  ) : <div className="text-slate-500 italic text-sm p-4">Sin datos.</div>}
                </div>
                {!isMonthly ? (
                  <div className={`rounded-3xl p-6 border ${glassClass}`}><h3 className={`text-lg font-bold mb-4 flex items-center gap-2 ${textTitle}`}><AlertCircle size={20} className="text-rose-500" />Sin actividad hoy</h3>
                    <div className="max-h-[160px] overflow-y-auto custom-scrollbar space-y-2">
                      {loading ? <p className="text-xs text-slate-500 animate-pulse">Buscando...</p> : inactiveInspectors.length > 0 ? inactiveInspectors.map((ins, i) => (
                        <div key={i} className={`flex justify-between items-center p-2 rounded-xl text-[10px] ${darkMode ? 'bg-white/5' : 'bg-slate-50'}`}><span className="font-bold uppercase truncate max-w-[120px]">{ins.inspector}</span><span className="text-rose-500 font-black">SIN REGISTRO</span></div>
                      )) : <p className="text-xs text-emerald-500 font-bold">Todos activos.</p>}
                    </div>
                  </div>
                ) : (
                   <div className={`rounded-3xl p-6 border ${glassClass}`}><h3 className={`text-lg font-bold mb-4 flex items-center gap-2 ${textTitle}`}><Activity size={20} className="text-emerald-500" />Frecuencia de Carga</h3>
                    <p className="text-[10px] text-slate-500 leading-relaxed uppercase font-bold tracking-tighter">Este módulo procesa múltiples días para obtener una visión estratégica del desempeño. El promedio de inicio se calcula tomando el primer registro de cada día seleccionado.</p>
                   </div>
                )}
              </div>

              <div className={`rounded-3xl border flex flex-col overflow-hidden ${glassClass}`}>
                <div className="overflow-x-auto custom-scrollbar max-h-[400px] overflow-y-auto">
                  <table className="w-full text-left border-collapse min-w-[1000px]">
                    <thead className={`sticky top-0 z-10 ${darkMode ? 'bg-[#0f172a]' : 'bg-slate-50'}`}>
                      <tr className={`text-slate-500 text-[9px] uppercase font-black border-b ${darkMode ? 'border-white/5' : 'border-slate-100'}`}>
                        <SortHeader label="Inspector" id="inspector" config={sortConfig} onSort={handleSort} /><SortHeader label="H. Inicio Prom." id="hora_inicio" config={sortConfig} onSort={handleSort} center /><SortHeader label="H. Final Prom." id="hora_final" config={sortConfig} onSort={handleSort} center /><SortHeader label="Localidad" id="localidad" config={sortConfig} onSort={handleSort} /><SortHeader label="Estado" id="estado" config={sortConfig} onSort={handleSort} /><SortHeader label="Total" id="total_ordenes" config={sortConfig} onSort={handleSort} center /><SortHeader label="Efec." id="ordenes_efectivas" config={sortConfig} onSort={handleSort} center /><SortHeader label="Efec. %" id="efectividad_pct" config={sortConfig} onSort={handleSort} center /><SortHeader label="Prom. Tarea" id="promedio_tiempo_tarea" config={sortConfig} onSort={handleSort} center /><SortHeader label="Prom. Recor." id="promedio_tiempo_recorrido" config={sortConfig} onSort={handleSort} center />
                      </tr>
                    </thead>
                    <tbody className={`divide-y ${darkMode ? 'divide-white/5' : 'divide-slate-100'}`}>{loading ? (<tr><td colSpan={10} className="px-6 py-20 text-center text-slate-500 animate-pulse">Cargando datos agregados...</td></tr>) : sortedInspections.map((item, idx) => <TableRowAgregada key={idx} item={item} darkMode={darkMode} />)}</tbody>
                  </table>
                </div>
              </div>

              <div className="w-full relative"><div className={`rounded-3xl p-6 border overflow-hidden ${glassClass}`}><div className="flex justify-between items-center mb-6"><h2 className={`text-xl font-bold flex items-center gap-2 ${textTitle}`}><BarChart3 size={20} className="text-emerald-500" />{isMonthly ? 'Producción Acumulada del Periodo' : 'Producción del Día'}</h2></div><div style={{ height: `${Math.max(400, chartData.length * 28)}px` }}>
                <ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} layout="vertical" margin={{ left: 220, right: 60, top: 0, bottom: 0 }}><XAxis type="number" hide /><YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={200} interval={0} tick={{fill: darkMode ? '#94a3b8' : '#64748b', fontSize: 10, fontWeight: 'bold'}} /><Tooltip contentStyle={{backgroundColor: '#0f172a', border: 'none', borderRadius: '12px'}} /><Bar dataKey="total" radius={[0, 4, 4, 0]} barSize={14}><LabelList dataKey="total" position="right" style={{ fill: '#10b981', fontSize: '11px', fontWeight: '900' }} offset={10} />{chartData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.total >= (isMonthly ? 100 : 8) ? '#10b981' : entry.total >= (isMonthly ? 50 : 5) ? '#f59e0b' : '#ef4444'} />)}</Bar></BarChart></ResponsiveContainer>
              </div></div></div>
            </motion.div>
          )}

          {activeSubTab === 'Seguimiento agendas' && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* AGENDA SIDEBAR */}
              <div className="lg:col-span-1 space-y-6">
                {/* ZONA FILTER */}
                <div className={`p-5 rounded-[32px] border ${glassClass}`}>
                  <h3 className={`text-[10px] font-black uppercase tracking-widest mb-3 ${textMuted}`}>Filtrar por Zona</h3>
                  <div className="flex flex-col gap-2">
                    {(agendasZonas.length > 0 ? agendasZonas : ['TODAS', 'INSP-CALDAS', 'INSP-RIS']).map((z) => (
                      <button key={z} onClick={() => handleZonaChange(z)}
                        className={`w-full px-4 py-2.5 rounded-2xl text-[11px] font-black uppercase tracking-wide transition-all text-left ${selectedZona === z ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20' : 'text-slate-500 hover:bg-white/5'}`}>
                        {z === 'TODAS' ? '🌐 TODAS' : z === 'INSP-CALDAS' ? '📍 CALDAS' : z === 'INSP-RIS' ? '📍 RISARALDA' : z}
                      </button>
                    ))}
                  </div>
                </div>
                <div className={`p-6 rounded-[32px] border ${glassClass}`}>
                  <h3 className={`text-sm font-black uppercase tracking-widest mb-6 ${textTitle}`}>Estado Agendas</h3>
                  <div className="space-y-2">
                    {['🚨 Alertas', '⏳ Próximas', '✅ Finalizadas'].map((view) => (
                      <button key={view} onClick={() => setActiveAgendasView(view)} className={`w-full flex items-center justify-between px-4 py-3 rounded-2xl transition-all ${activeAgendasView === view ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'text-slate-500 hover:bg-white/5'}`}>
                        <span className="text-xs font-bold">{view}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-black ${activeAgendasView === view ? 'bg-white/20' : 'bg-slate-800'}`}>
                          {view.includes('Alertas') ? agendasKPIs.alerta : view.includes('Próximas') ? agendasKPIs.proximas : agendasKPIs.finalizadas}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
                <div className={`p-6 rounded-[32px] border ${glassClass}`}>
                  <h3 className={`text-sm font-black uppercase tracking-widest mb-4 ${textTitle}`}>Resumen</h3>
                  <div className="space-y-4">
                    <KPIMini label="En Alerta" value={agendasKPIs.alerta} color="rose" />
                    <KPIMini label="Próximas" value={agendasKPIs.proximas} color="amber" />
                    <KPIMini label="Finalizadas" value={agendasKPIs.finalizadas} color="emerald" />
                  </div>
                </div>
              </div>

              {/* AGENDA MAIN VIEW */}
              <div className="lg:col-span-3 space-y-6">
                <div className={`rounded-[40px] border overflow-hidden ${glassClass}`}>
                  <div className="p-6 border-b border-white/5 flex justify-between items-center">
                    <h2 className={`text-xl font-black ${textTitle}`}>{activeAgendasView}</h2>
                    <span className="text-[10px] font-black uppercase text-emerald-500 bg-emerald-500/10 px-3 py-1 rounded-full">Total: {filteredAgendas.length}</span>
                  </div>
                  <div className="overflow-x-auto custom-scrollbar max-h-[600px]">
                    <table className="w-full text-left border-collapse">
                      <thead className={`sticky top-0 z-10 ${darkMode ? 'bg-[#0f172a]' : 'bg-slate-50'}`}>
                        <tr className="text-slate-500 text-[9px] uppercase font-black border-b border-white/5">
                          <th className="px-6 py-4">Inspector</th>
                          <th className="px-6 py-4">Contrato</th>
                          <th className="px-6 py-4">Fecha Visita</th>
                          <th className="px-6 py-4">Localidad</th>
                          <th className="px-6 py-4 text-center">Acción</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {loading ? (
                          <tr><td colSpan={5} className="px-6 py-20 text-center animate-pulse text-slate-500">Cargando agendas...</td></tr>
                        ) : filteredAgendas.length === 0 ? (
                          <tr><td colSpan={5} className="px-6 py-20 text-center text-slate-500 italic">No hay registros para este filtro.</td></tr>
                        ) : filteredAgendas.map((ag, idx) => (
                          <tr key={idx} className="hover:bg-white/5 transition-colors group">
                            <td className="px-6 py-4"><span className="text-[10px] font-bold uppercase text-white">{ag.inspector}</span></td>
                            <td className="px-6 py-4"><span className="text-[10px] font-mono text-slate-400">{ag.contrato}</span></td>
                            <td className="px-6 py-4"><span className="text-[10px] font-bold text-emerald-500">{ag.fecha_visita_str}</span></td>
                            <td className="px-6 py-4"><span className="text-[10px] font-medium text-slate-400">{ag.localidad}</span></td>
                            <td className="px-6 py-4 text-center">
                              <button onClick={() => setSelectedAgenda(ag)} className="p-2 rounded-xl bg-white/5 text-slate-400 hover:text-emerald-500 hover:bg-emerald-500/10 transition-all"><Eye size={14}/></button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeMainTab === 'CARGAR DATOS' && (
             <motion.div key="upload-tab" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center justify-center min-h-[60vh]">
              <div className={`w-full max-w-2xl p-10 rounded-[40px] border text-center relative overflow-hidden ${glassClass}`}>
                <div className="mb-8"><div className={`w-24 h-24 rounded-3xl mx-auto flex items-center justify-center mb-6 bg-emerald-500/10`}><UploadCloud className="text-emerald-500 w-12 h-12" /></div><h2 className={`text-3xl font-black mb-2 ${textTitle}`}>Cargar Bitácora General</h2><p className={`${textMuted} text-sm`}>Actualiza la base de datos principal.</p></div>
                <div className="space-y-6"><label className="block w-full cursor-pointer group"><div className={`p-10 border-2 border-dashed rounded-[32px] flex flex-col items-center gap-4 ${darkMode ? 'border-white/10 hover:border-emerald-500/50' : 'border-slate-200'}`}><FileSpreadsheet size={48} className="text-slate-700" /><span className={`font-bold ${textTitle}`}>Seleccionar archivo</span></div><input type="file" accept=".xlsx" className="hidden" onChange={handleFileUpload} disabled={uploading} /></label>
                  {uploadStatus.type && (<motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`p-4 rounded-2xl flex items-center gap-3 text-sm font-bold ${uploadStatus.type === 'success' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>{uploadStatus.message}</motion.div>)}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* MODAL DETALLE AGENDA */}
        <AnimatePresence>
          {selectedAgenda && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSelectedAgenda(null)} className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" />
              <motion.div initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: 20 }} className={`relative w-full max-w-xl p-8 rounded-[40px] border shadow-2xl ${glassClass}`}>
                <button onClick={() => setSelectedAgenda(null)} className="absolute top-6 right-6 p-2 rounded-xl hover:bg-white/10 text-slate-400 transition-all"><X size={20}/></button>
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-500"><ClipboardList size={24}/></div>
                  <div><h3 className={`text-xl font-black ${textTitle}`}>Detalle de la Tarea</h3><p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Contrato: {selectedAgenda.contrato}</p></div>
                </div>
                <div className="grid grid-cols-2 gap-6 mb-8">
                  <DetailItem label="Inspector" value={selectedAgenda.inspector} />
                  <DetailItem label="Localidad" value={selectedAgenda.localidad} />
                  <DetailItem label="Fecha Visita" value={selectedAgenda.fecha_visita_str} />
                  <DetailItem label="Estado" value={selectedAgenda.estado} highlight={selectedAgenda.estado_alerta === 'ALERTA'} />
                </div>
                <div className={`p-6 rounded-3xl border ${darkMode ? 'bg-white/5 border-white/10' : 'bg-slate-50 border-slate-200'}`}>
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Descripción Detallada</p>
                  <p className={`text-sm leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{selectedAgenda.detalle_de_tarea || 'Sin descripción adicional.'}</p>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function DetailItem({ label, value, highlight = false }: any) {
  return (
    <div>
      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-xs font-bold uppercase ${highlight ? 'text-rose-500' : 'text-white'}`}>{value}</p>
    </div>
  );
}

function KPIMini({ label, value, color }: any) {
  const colors: any = { rose: 'text-rose-500 bg-rose-500/10', amber: 'text-amber-500 bg-amber-500/10', emerald: 'text-emerald-500 bg-emerald-500/10' };
  return (
    <div className="flex items-center justify-between">
      <span className="text-[10px] font-bold text-slate-500 uppercase">{label}</span>
      <span className={`text-[10px] px-2 py-0.5 rounded-lg font-black ${colors[color]}`}>{value}</span>
    </div>
  );
}

function ReportItem({ icon, label, name, value, darkMode }: any) {
  return (<div className="flex items-center gap-3"><div className={`p-1.5 rounded-lg ${darkMode ? 'bg-white/5' : 'bg-slate-100'}`}>{icon}</div><div className="flex flex-col"><span className={`text-[11px] font-medium ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{label}:</span><div className="flex items-center gap-2"><span className={`text-xs font-black uppercase ${darkMode ? 'text-white' : 'text-slate-900'}`}>{name}</span><span className="text-[11px] font-bold text-emerald-500">({value})</span></div></div></div>);
}

function SortHeader({ label, id, config, onSort, center = false }: any) {
  const active = config.key === id;
  return (<th className={`px-2 py-2 whitespace-nowrap cursor-pointer group ${center ? 'text-center' : 'text-left'}`} onClick={() => onSort(id)}><div className={`flex items-center gap-1 ${center ? 'justify-center' : ''}`}>{label}{active ? (config.direction === 'asc' ? <ChevronUp size={10} /> : <ChevronDown size={10} />) : (<ArrowUpDown size={8} className="opacity-0 group-hover:opacity-50" />)}</div></th>);
}

function KPICard({ icon, label, value, trend, delay, darkMode = true }: any) {
  return (<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }} className={`p-4 rounded-[28px] border ${darkMode ? 'glass border-white/5' : 'bg-white border-slate-200'}`}><div className="mb-2"><div className={`p-2 w-9 h-9 rounded-xl border flex items-center justify-center ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>{icon}</div></div><p className="text-slate-500 text-[8px] uppercase font-black mb-1">{label}</p><h3 className={`text-xl font-black ${darkMode ? 'text-white' : 'text-slate-900'}`}>{value}</h3><p className="text-[8px] mt-1 font-bold text-emerald-500">{trend}</p></motion.div>);
}

function TrendingUpCard({ value, darkMode }: any) {
  return (<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} className={`p-4 rounded-[28px] border ${darkMode ? 'glass border-white/5' : 'bg-white border-slate-200'}`}><div className="mb-2"><div className={`p-2 w-9 h-9 rounded-xl border flex items-center justify-center ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}><TrendingUp className="text-blue-500" /></div></div><p className="text-slate-500 text-[8px] uppercase font-black mb-1">% EFECTIVIDAD</p><h3 className={`text-xl font-black ${darkMode ? 'text-white' : 'text-slate-900'}`}>{value}</h3><p className="text-[8px] mt-1 font-bold text-emerald-500">RENDIMIENTO</p></motion.div>);
}

function TableRowAgregada({ item, darkMode = true }: any) {
  const color = item.estado === 'Puntual' ? 'emerald' : item.estado === 'Tarde' ? 'amber' : 'red';
  return (
    <tr className={`transition-colors border-b ${darkMode ? 'hover:bg-white/5 border-white/5' : 'hover:bg-slate-50 border-slate-100'}`}>
      <td className="px-3 py-1"><div className="flex items-center gap-2"><div className="w-6 h-6 rounded flex items-center justify-center font-bold text-[8px] border bg-slate-800 text-slate-400">{item.inspector[0]}</div><span className="font-bold text-[10px] uppercase text-white">{item.inspector}</span></div></td>
      <td className="px-3 py-1 text-center text-[9px] font-mono">{item.hora_inicio}</td>
      <td className="px-3 py-1 text-center text-[9px] font-mono">{item.hora_final}</td>
      <td className="px-3 py-1 text-[9px] font-bold">{item.localidad}</td>
      <td className="px-3 py-1"><div className={`flex items-center gap-2 text-${color}-500 font-black text-[8px] uppercase`}><div className={`w-1 h-1 bg-${color}-500 rounded-full`}></div>{item.estado}</div></td>
      <td className="px-2 py-1 text-center font-bold text-[10px]">{item.total_ordenes}</td>
      <td className="px-2 py-1 text-center text-emerald-500 font-bold text-[10px]">{item.ordenes_efectivas}</td>
      <td className="px-2 py-1 text-center text-emerald-500 font-black text-[10px]">{item.efectividad_pct}%</td>
      <td className="px-3 py-1 text-center text-[9px]">{item.promedio_tiempo_tarea}</td>
      <td className="px-3 py-1 text-center text-[9px]">{item.promedio_tiempo_recorrido}</td>
    </tr>
  );
}
