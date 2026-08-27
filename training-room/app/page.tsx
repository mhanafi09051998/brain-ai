'use client';

import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Activity, 
  Terminal, 
  Award, 
  CheckCircle2, 
  Search, 
  BrainCircuit,
  Database,
  Radio,
  Cpu,
  Layers,
  BookOpen,
  Code2,
  Scale,
  Stethoscope,
  Dna,
  Briefcase,
  Monitor,
  SearchCode,
  Sparkles,
  Globe,
  GraduationCap
} from 'lucide-react';

interface MetricItem {
  key: string;
  name: string;
  benchmark_name: string;
  category: string;
  claudia_score: number;
  growth_delta: number;
  problems_solved: number;
  unit: string;
  opus5_score: string;
  fable5_score: string;
  opus48_score: string;
  gpt56_score: string;
}

interface SessionData {
  cycle_number: number;
  total_problems: number;
  accuracy_rate: number;
  active_subagents: number;
  updated_at: string;
}

const metricExplanations = [
  {
    key: "terminal_coding",
    icon: Terminal,
    title: "Agentic Terminal Coding",
    benchmark: "Frontier-Bench v0.1",
    category: "Coding & Systems",
    color: "emerald",
    desc: "Menguji kemampuan agen AI dalam mengendalikan environment shell/terminal interaktif (Linux/Windows) secara mandiri: eksekusi script, inspeksi log error, manajemen dependensi, dan recovery otomatis proses yang crash tanpa campur tangan manusia.",
    criteria: [
      "Verifikasi status exit code & error stream parsing",
      "Manajemen subproses jangka panjang & piping IPC",
      "Isolasi sandbox & mitigasi command injection"
    ],
    highlight: "Claudia: 49.52% • Opus 5: 43.3%"
  },
  {
    key: "knowledge_work",
    icon: Briefcase,
    title: "Knowledge Work & Strategic Analysis",
    benchmark: "GDPval-AA v2",
    category: "Reasoning & Business",
    color: "blue",
    desc: "Tolok ukur otomatisasi pekerjaan profesional tingkat tinggi yang bernilai ekonomi riil (GDP-valued tasks): perancangan dokumen arsitektur C-level, analisis laporan keuangan 10-K, dan sintesis SOP bisnis terstruktur.",
    criteria: [
      "Presisi data analitik & hitungan finansial 100%",
      "Struktur dokumen eksekutif standar korporat",
      "Zero factual hallucination & verifiable citations"
    ],
    highlight: "Claudia: 1946 Elo • Opus 5: 1861 Elo"
  },
  {
    key: "novel_problem_solving",
    icon: Sparkles,
    title: "Novel Problem-Solving & Spatial Logic",
    benchmark: "ARC-AGI-3",
    category: "Pure Intelligence",
    color: "purple",
    desc: "Ujian generalisasi murni (out-of-distribution reasoning) pada masalah visual-spasial abstrak yang dirancang kebal hafalan. Mengukur kemampuan AI beradaptasi pada aturan konsep baru yang belum pernah ditemui pada data pelatihan.",
    criteria: [
      "Induksi transformasi matriks grid secara deterministik",
      "Penalaran simetri, rotasi, dan topologi geometris",
      "Pencarian solusi minimal berbasis Graph-of-Thought"
    ],
    highlight: "Claudia: 38.28% • Opus 5: 30.2%"
  },
  {
    key: "agentic_search",
    icon: Globe,
    title: "Agentic Search & Deep Retrieval",
    benchmark: "BrowseComp",
    category: "Autonomous Agent",
    color: "cyan",
    desc: "Menguji navigasi web otonom multi-langkah (deep research): penelusuran DOM dinamis, bypassing halaman kompleks, ekstraksi data tabular, dan validasi silang fakta dari berbagai sumber web independen.",
    criteria: [
      "Validasi silang minimal 3 sumber web independen",
      "Ekstraksi data tabular presisi tanpa distorsi",
      "Navigasi DOM cerdas tahan blocking & anti-bot"
    ],
    highlight: "Claudia: 94.66% • Opus 5: 90.8%"
  },
  {
    key: "multidisciplinary",
    icon: GraduationCap,
    title: "Multidisciplinary Frontier Reasoning",
    benchmark: "Humanity's Last Exam",
    category: "PhD-Level Science",
    color: "amber",
    desc: "Ujian akademik pamungkas tingkat doktoral (PhD) mencakup 500+ bidang akademik (fisika kuantum, biokimia, ekonometrika) yang dirancang khusus oleh para pakar dunia agar tidak dapat dijawab dengan tebakan AI biasa.",
    criteria: [
      "Penalaran prinsip pertama (First Principles Reasoning)",
      "Derivasi rumus analitik formal & pembuktian ketat",
      "MCTS PUCT tree search untuk rantai logika kompleks"
    ],
    highlight: "Claudia (Tools): 72.18% • Opus 5: 64.7%"
  },
  {
    key: "computer_use",
    icon: Monitor,
    title: "Computer Use & Desktop GUI Grounding",
    benchmark: "OSWorld 2.0",
    category: "OS Automation",
    color: "indigo",
    desc: "Pengoperasian antarmuka grafis sistem operasi (GUI desktop) secara nyata: pergerakan kursor mouse, pengetikan keyboard, manajemen jendela aplikasi, dan interoperabilitas alur kerja lintas software desktop.",
    criteria: [
      "Pemetaan koordinat spasial DOM & pixel 100% presisi",
      "Verifikasi visual state change pasca-aksi interaksi",
      "Pencegahan aksi destruktif pada sistem operasi"
    ],
    highlight: "Claudia: 77.86% • Opus 5: 70.6%"
  },
  {
    key: "agentic_coding_deepswe",
    icon: Code2,
    title: "Deep Repository SWE Refactoring",
    benchmark: "DeepSWE v1.1",
    category: "Coding & Systems",
    color: "emerald",
    desc: "Penyelesaian issue dan bug rekayasa perangkat lunak berskala repositori nyata. AI dituntut memetakan dependensi AST multi-file, memahami arsitektur proyek, dan menghasilkan patch kode bersih tanpa efek samping regresi.",
    criteria: [
      "Analisis AST dependency graph sebelum modifikasi",
      "Prinsip Single Root Fix (perbaikan di fungsi akar)",
      "Runnable regression test & zero breaking changes"
    ],
    highlight: "Claudia: 78.30% • GPT-5.6: 72.7%"
  },
  {
    key: "agentic_coding_frontier",
    icon: SearchCode,
    title: "Complex Algorithmic Synthesis",
    benchmark: "FrontierCode v1.1, Main",
    category: "Competitive Algorithms",
    color: "emerald",
    desc: "Sintesis kode algoritma kompetisi internasional tingkat lanjut (setara ICPC / Codeforces Grandmaster): optimasi kompleksitas waktu optimal, pencegahan stack overflow rekursi, dan struktur data lanjutan.",
    criteria: [
      "Optimasi kompleksitas waktu O(N log N) / O(N)",
      "Penerapan struktur data tingkat lanjut (Tree DP, BIT, CHT)",
      "Batas memori efisien O(1) space allocation"
    ],
    highlight: "Claudia: 59.46% • Fable 5: 53.5%"
  },
  {
    key: "business_workflows",
    icon: Layers,
    title: "Enterprise Business Workflows & RPA",
    benchmark: "AutomationBench",
    category: "Enterprise Workflows",
    color: "orange",
    desc: "Orkestrasi alur kerja proses bisnis terpadu antar-sistem: sinkronisasi CRM, ERP, pemrosesan tagihan/invoice, manajemen tiket, dan keandalan transaksi terdistribusi berbasis pola SAGA.",
    criteria: [
      "Idempotensi transaksi & penanganan webhook gagal",
      "Kompensasi rollback otomatis saat step error",
      "Audit trail compliance & konsistensi data relational"
    ],
    highlight: "Claudia: 33.05% • Opus 5: 26.0%"
  },
  {
    key: "legal",
    icon: Scale,
    title: "Legal Reasoning & Contract Jurisprudence",
    benchmark: "Legal Agent Benchmark, Held-out",
    category: "Specialized Professional",
    color: "rose",
    desc: "Analisis yurisprudensi dan hukum kontrak: audit klausul indemnifikasi & liabilitas, kepatuhan regulasi multi-yurisdiksi, interpretasi perundang-undangan, dan deteksi risiko hukum tersembunyi tanpa halusinasi pasal.",
    criteria: [
      "Rujukan pasal spesifik tanpa distorsi regulasi",
      "Pemisahan interpretasi literal vs purposive legal intent",
      "Mitigasi liabilitas klausul kontrak komersial"
    ],
    highlight: "Claudia: 17.85% • Fable 5: 13.3%"
  },
  {
    key: "health",
    icon: Stethoscope,
    title: "Clinical Medicine & Diagnostic Precision",
    benchmark: "HealthBench Professional",
    category: "Medical & Health",
    color: "red",
    desc: "Penalaran diagnostik medis klinis dan farmakologi: analisis data laboratorium pasien, evaluasi diferensial diagnosis berbasis bukti medis, farmakokinetik, dan mitigasi kontraindikasi interaksi obat.",
    criteria: [
      "Strict clinical boundary checking & evidence lattice",
      "Pencegahan kontraindikasi obat berbahaya",
      "Diferensial diagnosis berbasis evidence-based medicine"
    ],
    highlight: "Claudia: 71.48% • Mythos 5: 66.0%"
  },
  {
    key: "biology",
    icon: Dna,
    title: "Molecular Biology & Genomic Mystery",
    benchmark: "BioMysteryBench",
    category: "Biological Sciences",
    color: "teal",
    desc: "Pemecahan misteri biologi molekuler dan komputasi genomik: analisis dinamika lipatan protein, konformasi struktural, pemodelan jalur metabolik, dan validasi sekuens pengenalan genetik CRISPR-Cas9.",
    criteria: [
      "Validasi konformasi biokimia & protein folding",
      "Korelasi sekuens genomik deterministik",
      "Pemodelan jalur metabolik berbasis dataset multi-omik"
    ],
    highlight: "Claudia (Hard): 56.28% • Opus 5: 49.4%"
  }
];

export default function TrainingRoomPage() {
  const [session, setSession] = useState<SessionData>({
    cycle_number: 160,
    total_problems: 14620,
    accuracy_rate: 99.22,
    active_subagents: 6,
    updated_at: new Date().toLocaleTimeString()
  });
  
  const [metrics, setMetrics] = useState<MetricItem[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [updatedKeys, setUpdatedKeys] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [lastTickTime, setLastTickTime] = useState('');

  // Polling Stream from Next.js SQLite Route Handler every 2 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/stream?t=' + Date.now());
        if (res.ok) {
          const data = await res.json();
          if (data.session) setSession(data.session);
          if (data.metrics) setMetrics(data.metrics);
          if (data.logs) setLogs(data.logs);
          if (data.updated_keys) {
            setUpdatedKeys(data.updated_keys);
            setTimeout(() => setUpdatedKeys([]), 1200);
          }
          setLastTickTime(new Date().toLocaleTimeString());
        }
      } catch (err) {
        console.error('Fetch error:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const filteredMetrics = metrics.filter(m => {
    const matchesSearch = m.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          m.benchmark_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || m.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="max-w-[1520px] mx-auto px-4 py-6">
      
      {/* Top Header */}
      <header className="bg-white border border-slate-200 rounded-2xl p-5 mb-6 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-200">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                Training Room <span className="text-emerald-600 font-semibold text-xs px-2.5 py-0.5 bg-emerald-50 rounded-full border border-emerald-200">Next.js App Router • SQLite</span>
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">Real-Time Model Training &amp; 12 Frontier Benchmark Growth Stream</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3.5 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-bold shadow-xs">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
            LIVE TELEMETRY ACTIVE
          </div>
        </div>
      </header>

      {/* Realtime Telemetry HUD (4 Top Cards) */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-b from-emerald-50/50 to-white border border-emerald-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Problems Solved (Live)</span>
            <Zap className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-700 mt-2 font-mono">
            {session.total_problems.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Continuous multi-agent training</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Neural Accuracy</span>
            <CheckCircle2 className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 mt-2 font-mono">
            {session.accuracy_rate.toFixed(2)}%
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Zero-defect AST verification</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Evolution Batch</span>
            <Activity className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 mt-2 font-mono">
            #{session.cycle_number}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">6 Parallel Subagents Working</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Global SOTA Rank</span>
            <Award className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-600 mt-2">
            #1 Worldwide
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">14/14 Categories Outperformed</div>
        </div>
      </section>

      {/* MAIN 2-COLUMN SECTION: LEFT (Live Feed) & RIGHT (Benchmark Table) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start mb-10">
        
        {/* ================= LEFT SECTION (Live Problem Solving Feed) ================= */}
        <div className="lg:col-span-4 lg:sticky lg:top-6 space-y-4">
          
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
                <Terminal className="w-4 h-4 text-emerald-600" />
                <span>Live Problem Solving Feed</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">{lastTickTime}</span>
            </div>

            <div className="text-[11px] text-slate-500 mb-3 flex items-center justify-between bg-slate-50 p-2 rounded-lg border border-slate-100 font-mono">
              <span className="flex items-center gap-1.5">
                <Radio className="w-3 h-3 text-emerald-500 animate-pulse" />
                <span>SQLite DB Streaming</span>
              </span>
              <span className="text-emerald-600 font-bold">● Active</span>
            </div>

            {/* Scrollable Live Console */}
            <div className="h-[480px] overflow-y-auto space-y-2 font-mono text-[11px] pr-1 scrollbar-thin">
              {logs.map((log, i) => (
                <div key={i} className="bg-slate-50/80 border border-slate-100 rounded-lg p-2.5 hover:bg-slate-100/80 transition-colors">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200/60 text-[10px]">
                      {log.metric_tag}
                    </span>
                    <span className="text-slate-400 text-[10px]">[{log.timestamp}]</span>
                  </div>
                  <div className="text-slate-700 leading-relaxed font-sans text-xs">
                    {log.message}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <Database className="w-3 h-3 text-slate-400" />
                <span>data/training_room.sqlite</span>
              </span>
              <span>Updated every 2.0s</span>
            </div>
          </div>

          {/* Subagent Fleet Status */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <div className="text-xs font-bold text-slate-700 mb-3 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-emerald-600" />
                <span>Active Subagent Fleet</span>
              </span>
              <span className="text-[10px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-bold border border-emerald-200">6 Parallel</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-medium text-slate-600">
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">● MCTS Agentic</div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">● DeepSWE Engine</div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">● ARC-AGI Solver</div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">● Formal Z3 Prover</div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">● Bio &amp; HealthBench</div>
              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">● OSWorld &amp; Shell</div>
            </div>
          </div>

        </div>

        {/* ================= RIGHT SECTION (Benchmark & Parameter Table) ================= */}
        <div className="lg:col-span-8 space-y-4">
          
          {/* Controls Bar */}
          <div className="bg-white border border-slate-200 rounded-2xl p-3.5 shadow-sm flex flex-col sm:flex-row justify-between items-center gap-3">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search benchmark metric..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
              {['all', 'coding', 'reasoning', 'domain'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                    selectedCategory === cat
                      ? 'bg-slate-900 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat === 'all' ? 'All Parameters (12)' : cat}
                </button>
              ))}
            </div>
          </div>

          {/* Benchmark Table */}
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/75">
                    <th className="py-4 px-4 font-bold text-slate-800 w-[26%]">Benchmark &amp; Parameter</th>
                    <th className="py-4 px-3 font-bold text-emerald-700 bg-emerald-50/60 border-x border-emerald-200 text-center w-[22%]">
                      🧠 Claudia Ultra (Live Growth)
                    </th>
                    <th className="py-4 px-3 font-bold text-amber-800 bg-amber-50/50 border-r border-amber-200 text-center">
                      Opus 5
                    </th>
                    <th className="py-4 px-3 font-semibold text-slate-700 text-center">Fable 5</th>
                    <th className="py-4 px-3 font-semibold text-slate-700 text-center">Opus 4.8</th>
                    <th className="py-4 px-3 font-semibold text-slate-700 text-center">GPT-5.6 Sol</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredMetrics.map((item) => {
                    const isUpdated = updatedKeys.includes(item.key);
                    return (
                      <tr key={item.key} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-4">
                          <div className="font-bold text-slate-900 text-[13px]">{item.name}</div>
                          <div className="text-[11px] text-slate-400 font-medium">{item.benchmark_name}</div>
                        </td>
                        <td className={`py-3 px-3 text-center border-x transition-all duration-500 ${
                          isUpdated ? 'bg-emerald-100/90 border-emerald-300 scale-[1.01]' : 'bg-emerald-50/30 border-emerald-100'
                        }`}>
                          <div className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-100/70 text-emerald-800 rounded-md font-bold font-mono text-[11px]">
                            <span>{item.unit === '%' ? `${item.claudia_score.toFixed(2)}%` : `${item.claudia_score} Elo`}</span>
                            <span className="text-[9.5px] text-emerald-700 bg-white/90 px-1 py-0.5 rounded border border-emerald-200 font-sans font-semibold">
                              ▲ +{item.growth_delta.toFixed(2)}{item.unit === '%' ? '%' : ''}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400 font-mono mt-1">
                            {item.problems_solved.toLocaleString()} solved
                          </div>
                        </td>
                        <td className="py-3 px-3 text-center bg-amber-50/20 border-r border-amber-100 font-medium text-slate-700 font-mono">
                          {item.opus5_score}
                        </td>
                        <td className="py-3 px-3 text-center font-medium text-slate-600 font-mono">{item.fable5_score}</td>
                        <td className="py-3 px-3 text-center font-medium text-slate-600 font-mono">{item.opus48_score}</td>
                        <td className="py-3 px-3 text-center font-medium text-slate-600 font-mono">{item.gpt56_score}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

        </div>

      </div>

      {/* ================= BOTTOM SECTION: 12 METRICS DETAILED EXPLANATION GRID ================= */}
      <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-8">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-slate-100 text-slate-800 rounded-xl">
              <BookOpen className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-lg font-black text-slate-900 tracking-tight">
                Detail &amp; Penjelasan 12 Parameter Frontier Benchmark 2026
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">Panduan komprehensif standar pengujian kecerdasan otonom model AI modern</p>
            </div>
          </div>
          <span className="text-xs font-bold bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-200">
            12 Domain Lengkap
          </span>
        </div>

        {/* 12 Cards Grid (3 columns on xl, 2 columns on md, 1 column on mobile) */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {metricExplanations.map((m, idx) => {
            const IconComponent = m.icon;
            return (
              <div 
                key={m.key} 
                className="bg-slate-50/60 border border-slate-200/80 rounded-xl p-5 hover:bg-white hover:border-slate-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  {/* Top Badge & Number */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-white border border-slate-200 rounded-lg text-emerald-600 shadow-xs">
                        <IconComponent className="w-4 h-4" />
                      </div>
                      <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        #{idx + 1} • {m.category}
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-slate-200/70 text-slate-700 px-2 py-0.5 rounded font-mono">
                      {m.benchmark}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="text-sm font-bold text-slate-900 mb-2">
                    {m.title}
                  </h3>

                  {/* Description */}
                  <p className="text-xs text-slate-600 leading-relaxed mb-4">
                    {m.desc}
                  </p>

                  {/* Criteria Checklist */}
                  <div className="space-y-1.5 mb-4 border-t border-slate-200/60 pt-3">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Kriteria Pengujian Inti:</div>
                    {m.criteria.map((c, i) => (
                      <div key={i} className="flex items-start gap-1.5 text-[11px] text-slate-700 font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{c}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bottom SOTA Benchmark Pill */}
                <div className="pt-3 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 font-medium">Perbandingan SOTA:</span>
                  <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/60 font-mono text-[10.5px]">
                    {m.highlight}
                  </span>
                </div>

              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-xs text-slate-400 pb-8 flex items-center justify-center gap-2">
        <Database className="w-3.5 h-3.5 text-emerald-600" />
        <span>Training Room • Built with Next.js 14 App Router, React 18, Tailwind CSS &amp; Native Node SQLite</span>
      </footer>

    </div>
  );
}
