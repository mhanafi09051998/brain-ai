import os

html = """<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Claudia Max 4.0 — AI Autonomous Learning & Frontier Benchmark Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: { 500: '#8b5cf6', 600: '#7c3aed' },
            surface: { base: '#070b12', sidebar: '#0b101b', card: '#0f172a', border: '#1e293b' }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b12; color: #f1f5f9; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    .glass-panel { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .glass-panel:hover { border-color: rgba(139, 92, 246, 0.4); }
    @keyframes pulse-dot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.4; } }
    .live-pulse { animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
  </style>
</head>
<body class="flex h-screen overflow-hidden text-slate-100">

  <!-- SIDEBAR NAVIGATION -->
  <aside class="w-72 bg-surface-sidebar border-r border-surface-border flex flex-col justify-between shrink-0 z-20">
    <div>
      <div class="p-5 border-b border-surface-border flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center shadow-lg shadow-brand-600/30">
          <i class="fa-solid fa-brain text-white text-lg"></i>
        </div>
        <div>
          <h1 class="font-bold text-base tracking-tight text-white flex items-center gap-2">
            Claudia Max
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-semibold border border-emerald-500/30">v4.0</span>
          </h1>
          <p class="text-xs text-slate-400 font-medium">Gahar Inovasi Teknologi</p>
        </div>
      </div>

      <nav class="p-4 space-y-1.5">
        <div class="px-3 py-1.5 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Modul Pelatihan AI</div>
        
        <button onclick="switchTab('benchmarks')" id="tab-btn-benchmarks" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all bg-brand-600/20 text-brand-300 border border-brand-500/30 shadow-sm">
          <i class="fa-solid fa-flask-vial text-brand-400 w-5"></i>
          <span>Pelatihan 6 Parameter</span>
          <span class="ml-auto w-2 h-2 rounded-full bg-emerald-400 live-pulse"></span>
        </button>

        <button onclick="switchTab('trading')" id="tab-btn-trading" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all text-slate-400 hover:text-white hover:bg-surface-card border border-transparent">
          <i class="fa-solid fa-chart-line text-amber-400 w-5"></i>
          <span>Emas & Kripto (Quant)</span>
          <span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono">Live Feed</span>
        </button>

        <button onclick="switchTab('neurons')" id="tab-btn-neurons" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all text-slate-400 hover:text-white hover:bg-surface-card border border-transparent">
          <i class="fa-solid fa-network-wired text-cyan-400 w-5"></i>
          <span>Jaringan Neuron (21)</span>
        </button>

        <div class="pt-4 px-3 py-1.5 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Akses Ekosistem Zolu</div>
        <a href="https://movie.zolu.my.id" target="_blank" class="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-surface-card transition">
          <i class="fa-solid fa-film text-purple-400 w-5"></i> Zolu Cinema
        </a>
        <a href="https://monitor.zolu.my.id" target="_blank" class="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-surface-card transition">
          <i class="fa-solid fa-gauge-high text-emerald-400 w-5"></i> VPS Telemetry
        </a>
      </nav>
    </div>

    <div class="p-4 border-t border-surface-border bg-surface-base/50">
      <div class="flex items-center gap-2 text-xs text-slate-400 mb-1.5">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span class="font-mono text-slate-300">9Router: Online</span>
      </div>
      <div class="text-[11px] text-slate-500 font-mono truncate">Model: ag/gemini-3.7-flash-high</div>
    </div>
  </aside>

  <!-- MAIN VIEW -->
  <main class="flex-1 flex flex-col h-screen overflow-y-auto bg-surface-base p-6 lg:p-8 space-y-6">

    <!-- VIEW 1: 6 PARAMETERS -->
    <section id="view-benchmarks" class="space-y-6">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 live-pulse"></span> Evaluasi Empiris Berjalan
            </span>
            <span class="text-xs text-slate-400 font-mono">Loop Evaluasi Aktif</span>
          </div>
          <h2 class="text-2xl font-extrabold text-white tracking-tight">Frontier Empirical Benchmark Suite</h2>
          <p class="text-xs text-slate-400 mt-1">Uji empiris 6 parameter deterministik (SWE-bench, TAU-bench, AIME, GPQA, IFEval, NIAH) bebas regresi.</p>
        </div>
        <div class="flex items-center gap-4 bg-surface-base/80 border border-surface-border px-5 py-3 rounded-xl">
          <div>
            <div class="text-[11px] text-slate-400 uppercase font-semibold">Total Pengujian</div>
            <div id="total-evals" class="text-2xl font-extrabold text-white font-mono">27,036</div>
          </div>
          <div class="h-8 w-px bg-surface-border"></div>
          <div>
            <div class="text-[11px] text-slate-400 uppercase font-semibold">Throughput</div>
            <div id="throughput-speed" class="text-2xl font-extrabold text-emerald-400 font-mono">95 <span class="text-xs text-slate-400">tok/s</span></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">SWE-bench</span>
            <i class="fa-solid fa-code text-brand-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-swe">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 85.0% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">TAU-bench</span>
            <i class="fa-solid fa-screwdriver-wrench text-cyan-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-tau">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 95.0% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">AIME 2024</span>
            <i class="fa-solid fa-calculator text-amber-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-aime">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 90.0% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">GPQA Diamond</span>
            <i class="fa-solid fa-atom text-purple-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-gpqa">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 90.4% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">IFEval Rules</span>
            <i class="fa-solid fa-list-check text-emerald-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-ifeval">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 98.0% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">NIAH 2M</span>
            <i class="fa-solid fa-magnifying-glass-chart text-pink-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-niah">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 99.9% ✓</div>
        </div>
      </div>

      <div class="glass-panel rounded-2xl p-5 flex flex-col h-[380px]">
        <div class="flex items-center justify-between pb-3 border-b border-surface-border mb-3">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-red-500/80"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-amber-500/80"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></span>
            <span class="text-xs font-mono text-slate-400 ml-2">Live Empirical Execution Terminal (SSE)</span>
          </div>
          <span class="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-400 live-pulse"></span> Streaming Realtime
          </span>
        </div>
        <div id="terminal-logs" class="flex-1 overflow-y-auto font-mono text-xs space-y-1.5 text-slate-300 pr-2"></div>
      </div>
    </section>

    <!-- VIEW 2: QUANT TRADING -->
    <section id="view-trading" class="space-y-6 hidden">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-400 live-pulse"></span> Pelatihan Model Kuantitatif Real-time
            </span>
            <span class="text-xs text-slate-400 font-mono">Binance & XAU/USD Spot Feed</span>
          </div>
          <h2 class="text-2xl font-extrabold text-white tracking-tight">Pelatihan Kuantitatif: Emas & Cryptocurrency</h2>
          <p class="text-xs text-slate-400 mt-1">Pemodelan prediktif berbasis Smart Money Concepts (SMC), Fair Value Gap (FVG), dan manajemen risiko RRR 1:3.</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="glass-panel p-5 rounded-2xl border border-amber-500/20">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-bold text-amber-300 flex items-center gap-1.5"><i class="fa-solid fa-coins text-amber-400"></i> Gold (XAU/USD)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono">SPOT</span>
          </div>
          <div class="text-2xl font-extrabold text-white font-mono" id="price-xau">$2,748.50</div>
          <div class="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-surface-border">
            <span>ATR (14): <strong class="text-white font-mono">18.40</strong></span>
            <span class="text-emerald-400 font-semibold">Macro Bullish</span>
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-bold text-orange-400 flex items-center gap-1.5"><i class="fa-brands fa-bitcoin text-orange-400"></i> Bitcoin (BTC/USDT)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono" id="trend-btc">BULLISH</span>
          </div>
          <div class="text-2xl font-extrabold text-white font-mono" id="price-btc">$96,450.00</div>
          <div class="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-surface-border">
            <span>RSI: <strong class="text-cyan-400 font-mono" id="rsi-btc">52.4</strong></span>
            <span>ATR: <strong class="text-white font-mono" id="atr-btc">850.2</strong></span>
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-bold text-indigo-400 flex items-center gap-1.5"><i class="fa-brands fa-ethereum text-indigo-400"></i> Ethereum (ETH/USDT)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono" id="trend-eth">BULLISH</span>
          </div>
          <div class="text-2xl font-extrabold text-white font-mono" id="price-eth">$2,840.00</div>
          <div class="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-surface-border">
            <span>RSI: <strong class="text-cyan-400 font-mono" id="rsi-eth">48.1</strong></span>
            <span>ATR: <strong class="text-white font-mono" id="atr-eth">42.5</strong></span>
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-bold text-purple-400 flex items-center gap-1.5"><i class="fa-solid fa-bolt text-purple-400"></i> Solana (SOL/USDT)</span>
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono" id="trend-sol">BULLISH</span>
          </div>
          <div class="text-2xl font-extrabold text-white font-mono" id="price-sol">$188.20</div>
          <div class="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-surface-border">
            <span>RSI: <strong class="text-cyan-400 font-mono" id="rsi-sol">55.8</strong></span>
            <span>ATR: <strong class="text-white font-mono" id="atr-sol">4.12</strong></span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="glass-panel p-6 rounded-2xl space-y-3">
          <h3 class="font-bold text-base text-white flex items-center gap-2">
            <i class="fa-solid fa-scale-balanced text-amber-400"></i> Invarian Kuantitatif (Neuron N021)
          </h3>
          <div class="p-3.5 rounded-xl bg-surface-base/80 border border-surface-border text-xs text-slate-300">
            <strong class="text-amber-300">1. Strict Risk Management (RRR 1:3):</strong> Maksimal 1-2% risiko modal per trade. Posisi RRR &lt; 1:2.5 ditolak otomatis.
          </div>
          <div class="p-3.5 rounded-xl bg-surface-base/80 border border-surface-border text-xs text-slate-300">
            <strong class="text-amber-300">2. Smart Money &amp; Fair Value Gap:</strong> Konfirmasi entri saat harga retest zona FVG 50% (Consequent Encroachment).
          </div>
        </div>

        <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between">
          <h3 class="font-bold text-base text-white flex items-center gap-2 mb-3">
            <i class="fa-solid fa-terminal text-cyan-400"></i> Live Quant Invariant Signal Stream
          </h3>
          <div id="quant-logs" class="bg-surface-base rounded-xl p-4 font-mono text-xs space-y-2 h-[200px] overflow-y-auto text-slate-300 border border-surface-border">
            <div class="text-emerald-400">[QUANT ENGINE] Real-time market feed active. Streaming 1H klines...</div>
            <div class="text-slate-400">[BTCUSDT] EMA20 > EMA50 (Bullish). RSI=52.4 (Neutral Pullback Zone).</div>
            <div class="text-amber-300">[XAUUSD] Spot DXY inverse correlation confirmed. Macro trend intact.</div>
            <div class="text-cyan-400">[SMC] 1H Bullish FVG detected at support zone. RRR Calculation: 1:3.2.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- VIEW 3: NEURONS -->
    <section id="view-neurons" class="space-y-6 hidden">
      <div class="glass-panel p-6 rounded-2xl flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-extrabold text-white tracking-tight">Active Neuron Knowledge Network</h2>
          <p class="text-xs text-slate-400 mt-1">21 Neuron tematik terdistribusi yang membentuk kecerdasan operasional Claudia.</p>
        </div>
        <span class="px-3 py-1 bg-brand-600/20 text-brand-300 border border-brand-500/30 rounded-xl font-mono text-xs font-bold">21 Neurons Active</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="neuron-grid"></div>
    </section>
  </main>

  <script>
    const neuronData = [
      { id: "N001", title: "Executive Decisions", desc: "Keputusan teknis cepat tanpa keraguan, root-cause first." },
      { id: "N002", title: "VPS Remote Operations", desc: "SSH tunneling otomatis, supervisi PM2, isolasi port." },
      { id: "N003", title: "Mobile-First UI & UX", desc: "Zero browser native popups, light mode default, max 300 LOC." },
      { id: "N004", title: "Ponytail Minimality Ladder", desc: "YAGNI, standard library first, eliminasi kode berlebih." },
      { id: "N005", title: "Graphify Knowledge Network", desc: "AST code dependency mapper & modular graph RAG." },
      { id: "N006", title: "9Router Gateway Engine", desc: "Low-latency LLM gateway & multi-provider routing." },
      { id: "N007", title: "Self-Improving Loop", desc: "Pencatatan invarian otomatis via record_learning.py." },
      { id: "N008", title: "Live Session Checkpoint", desc: "State persistensi ekosistem server, Jellyfin & Cloud NAS." },
      { id: "N009", title: "Peak Algorithmic Codex", desc: "Tarjan SCC, Segment Tree, Bloom Filter, Lock-Free." },
      { id: "N010", title: "Distributed Systems Design", desc: "Raft/Paxos consensus, CQRS, 2PC & Saga transactions." },
      { id: "N011", title: "Mechanical Sympathy", desc: "L1/L2 cache locality, Linux sendfile zero-copy, io_uring." },
      { id: "N012", title: "Deep Search & GraphRAG", desc: "BM25 + Dense vector semantic, RRF, multi-hop traversal." },
      { id: "N013", title: "Deep Storage & LSM-Tree", desc: "MemTable/SSTable compaction, WAL, HNSW vector index." },
      { id: "N014", title: "Zero-Trust Security", desc: "PASETO tokens, constant-time crypto, tamper signature." },
      { id: "N015", title: "Compiler AST & Profiling", desc: "Tree-Sitter AST visitors, WASM, CPU flamegraphs." },
      { id: "N016", title: "Frontier Benchmark Evaluator", desc: "Framework pengujian empiris 6 parameter deterministik." },
      { id: "N017", title: "Program-Aided Math (AIME)", desc: "Invariant proof, Diophantine modular parity, PAL." },
      { id: "N018", title: "RepoMap AST & SWE-bench", desc: "PageRank AST callgraph, root-cause patch precision." },
      { id: "N019", title: "BFCL Tool Schema Oracle", desc: "Negative constraint checking, compensating rollback." },
      { id: "N020", title: "Session Continuity Checkpoint", desc: "Multi-IDE state synchronization & connection resilience." },
      { id: "N021", title: "Quantitative Gold & Crypto", desc: "Invarian trading XAU/USD & Kripto, SMC/FVG, ATR RRR 1:3." }
    ];

    function renderNeurons() {
      const grid = document.getElementById('neuron-grid');
      grid.innerHTML = neuronData.map(n => `
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono font-bold text-brand-400">${n.id}</span>
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          </div>
          <h4 class="font-bold text-sm text-white mb-1">${n.title}</h4>
          <p class="text-xs text-slate-400">${n.desc}</p>
        </div>
      `).join('');
    }

    function switchTab(tabId) {
      document.getElementById('view-benchmarks').classList.add('hidden');
      document.getElementById('view-trading').classList.add('hidden');
      document.getElementById('view-neurons').classList.add('hidden');

      document.getElementById(`view-${tabId}`).classList.remove('hidden');

      const btnBench = document.getElementById('tab-btn-benchmarks');
      const btnTrade = document.getElementById('tab-btn-trading');
      const btnNeuro = document.getElementById('tab-btn-neurons');

      [btnBench, btnTrade, btnNeuro].forEach(b => {
        b.className = "w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all text-slate-400 hover:text-white hover:bg-surface-card border border-transparent";
      });

      const activeBtn = document.getElementById(`tab-btn-${tabId}`);
      activeBtn.className = "w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all bg-brand-600/20 text-brand-300 border border-brand-500/30 shadow-sm";
    }

    function initSSE() {
      const evtSource = new EventSource('/events');
      evtSource.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);
          if (data.total_evaluations) document.getElementById('total-evals').innerText = Number(data.total_evaluations).toLocaleString();
          if (data.metrics) {
            if (data.metrics.inference_speed) document.getElementById('throughput-speed').innerHTML = `${data.metrics.inference_speed.current} <span class="text-xs text-slate-400">tok/s</span>`;
            if (data.metrics.swe_bench) document.getElementById('val-swe').innerText = `${data.metrics.swe_bench.current}%`;
            if (data.metrics.tau_bench) document.getElementById('val-tau').innerText = `${data.metrics.tau_bench.current}%`;
            if (data.metrics.aime_gpqa) document.getElementById('val-aime').innerText = `${data.metrics.aime_gpqa.current}%`;
            if (data.metrics.gpqa_diamond) document.getElementById('val-gpqa').innerText = `${data.metrics.gpqa_diamond.current}%`;
            if (data.metrics.ifeval) document.getElementById('val-ifeval').innerText = `${data.metrics.ifeval.current}%`;
            if (data.metrics.niah_retrieval) document.getElementById('val-niah').innerText = `${data.metrics.niah_retrieval.current}%`;
          }
          if (data.logs && Array.isArray(data.logs)) {
            const term = document.getElementById('terminal-logs');
            term.innerHTML = data.logs.slice(0, 30).map(l => `
              <div class="flex items-start gap-2 py-0.5">
                <span class="text-slate-500 font-mono">[${l.time}]</span>
                <span class="text-emerald-400 font-bold">[${l.category.toUpperCase()}]</span>
                <span class="text-slate-300">${l.message}</span>
              </div>
            `).join('');
          }
          if (data.quant_trading && data.quant_trading.market_snapshot) {
            updateQuantUI(data.quant_trading.market_snapshot);
          }
        } catch (e) {}
      };
    }

    function updateQuantUI(snapshot) {
      if (snapshot.BTCUSDT) {
        document.getElementById('price-btc').innerText = `$${Number(snapshot.BTCUSDT.current_price).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        document.getElementById('rsi-btc').innerText = snapshot.BTCUSDT.rsi_14;
        document.getElementById('atr-btc').innerText = snapshot.BTCUSDT.atr_14;
        document.getElementById('trend-btc').innerText = snapshot.BTCUSDT.trend;
      }
      if (snapshot.ETHUSDT) {
        document.getElementById('price-eth').innerText = `$${Number(snapshot.ETHUSDT.current_price).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        document.getElementById('rsi-eth').innerText = snapshot.ETHUSDT.rsi_14;
        document.getElementById('atr-eth').innerText = snapshot.ETHUSDT.atr_14;
        document.getElementById('trend-eth').innerText = snapshot.ETHUSDT.trend;
      }
      if (snapshot.SOLUSDT) {
        document.getElementById('price-sol').innerText = `$${Number(snapshot.SOLUSDT.current_price).toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        document.getElementById('rsi-sol').innerText = snapshot.SOLUSDT.rsi_14;
        document.getElementById('atr-sol').innerText = snapshot.SOLUSDT.atr_14;
        document.getElementById('trend-sol').innerText = snapshot.SOLUSDT.trend;
      }
    }

    async function fetchQuantDataManual() {
      try {
        const res = await fetch('/api/quant-trading');
        const data = await res.json();
        if (data && data.market_snapshot) updateQuantUI(data.market_snapshot);
      } catch (e) {}
    }

    renderNeurons();
    initSSE();
    fetchQuantDataManual();
  </script>
</body>
</html>
"""

with open('scripts/learn_index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS: scripts/learn_index.html generated.")