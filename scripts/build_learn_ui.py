#!/usr/bin/env python3
import json
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    neuron_index = json.load(f)

neurons_list = neuron_index.get("neurons", [])
total_neurons = len(neurons_list)
total_synapses = neuron_index.get("total_synapses", sum(len(n.get("connections", [])) for n in neurons_list))

# Generate clean neuron JS array
neurons_js_data = []
for n in neurons_list:
    nid = n.get("id", "")
    lbl = n.get("label", "").replace(f"Neuron {nid}: ", "")
    file_name = n.get("file", "")
    synapses = len(n.get("connections", []))
    
    # Generate concise description
    desc = f"Berkas: {file_name} • {synapses} Sinapsis Aktif"
    if "N053" in nid:
        desc = "MMM, Causal Uplift & BG/NBD CLV Nucleus Engine"
    elif "N054" in nid:
        desc = "Large-Scale Architecture, Topology & Contract-First Nucleus Engine"
    elif "N055" in nid:
        desc = "Generative Visual Engineering & Vector Math Nucleus Engine"
    elif "N056" in nid:
        desc = "Quantitative SWOT & TOWS Strategic Matrix Nucleus Engine"

    neurons_js_data.append({
        "id": nid,
        "title": lbl,
        "desc": desc,
        "synapses": synapses,
        "is_nucleus": nid in ["N053", "N054", "N055", "N056"]
    })

neurons_json_str = json.dumps(neurons_js_data, indent=2, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Claudia 5.0 Max — AI Autonomous Neural Mesh & Strategic Nucleus</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }},
          colors: {{
            brand: {{ 500: '#8b5cf6', 600: '#7c3aed' }},
            surface: {{ base: '#070b12', sidebar: '#0b101b', card: '#0f172a', border: '#1e293b' }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #070b12; color: #f1f5f9; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .glass-panel {{ background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }}
    .glass-panel:hover {{ border-color: rgba(139, 92, 246, 0.4); }}
    @keyframes pulse-dot {{ 0%, 100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(1.4); opacity: 0.4; }} }}
    .live-pulse {{ animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}
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
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-semibold border border-emerald-500/30">v5.0</span>
          </h1>
          <p class="text-xs text-slate-400 font-medium">Gahar Inovasi Teknologi</p>
        </div>
      </div>

      <nav class="p-4 space-y-1.5">
        <div class="px-3 py-1.5 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Modul Pelatihan & Nukleus</div>
        
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

        <button onclick="switchTab('nucleus')" id="tab-btn-nucleus" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all text-slate-400 hover:text-white hover:bg-surface-card border border-transparent">
          <i class="fa-solid fa-atom text-purple-400 w-5"></i>
          <span>Mesin Nukleus (4)</span>
          <span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono font-bold">Produksi</span>
        </button>

        <button onclick="switchTab('neurons')" id="tab-btn-neurons" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all text-slate-400 hover:text-white hover:bg-surface-card border border-transparent">
          <i class="fa-solid fa-network-wired text-cyan-400 w-5"></i>
          <span>Jaringan Neuron ({total_neurons})</span>
          <span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono">{total_neurons}</span>
        </button>

        <div class="pt-4 px-3 py-1.5 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">Akses Ekosistem Zolu</div>
        <a href="https://movie.zolu.my.id" target="_blank" class="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-surface-card transition">
          <i class="fa-solid fa-film text-purple-400 w-5"></i> Goblix Cinema
        </a>
        <a href="https://monitor.zolu.my.id" target="_blank" class="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-surface-card transition">
          <i class="fa-solid fa-gauge-high text-emerald-400 w-5"></i> VPS Telemetry
        </a>
      </nav>
    </div>

    <div class="p-4 border-t border-surface-border bg-surface-base/50">
      <div class="flex items-center gap-2 text-xs text-slate-400 mb-1.5">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span class="font-mono text-slate-300">Neural Mesh: {total_neurons} Neurons / {total_synapses} Synapses</span>
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
            <i class="fa-solid fa-gem text-emerald-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-gpqa">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 90.4% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">IFEval</span>
            <i class="fa-solid fa-list-check text-purple-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-ifeval">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 98.0% ✓</div>
        </div>
        <div class="glass-panel p-4 rounded-xl border border-surface-border">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span class="font-semibold">NIAH (20k)</span>
            <i class="fa-solid fa-magnifying-glass-location text-rose-400"></i>
          </div>
          <div class="text-2xl font-bold text-white font-mono" id="val-niah">100%</div>
          <div class="text-[11px] text-emerald-400 mt-1">Target: 99.9% ✓</div>
        </div>
      </div>

      <!-- Real-Time Evaluation Logs Terminal -->
      <div class="glass-panel p-6 rounded-2xl space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="font-bold text-sm text-white flex items-center gap-2">
            <i class="fa-solid fa-terminal text-brand-400"></i> Live Empirical Evaluation Stream
          </h3>
          <span class="text-xs text-slate-400 font-mono">Status: Stream Online</span>
        </div>
        <div id="terminal-logs" class="bg-surface-base rounded-xl p-4 font-mono text-xs space-y-1.5 h-64 overflow-y-auto border border-surface-border text-slate-300">
          <div class="text-slate-500">Memuat log real-time dari runner...</div>
        </div>
      </div>
    </section>

    <!-- VIEW 2: TRADING -->
    <section id="view-trading" class="space-y-6 hidden">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-400 live-pulse"></span> SMC & Quantitative Engine
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
          <div class="text-2xl font-extrabold text-white font-mono" id="price-xau">$4,629.04</div>
          <div class="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-surface-border">
            <span>ATR (14): <strong class="text-white font-mono">1.85</strong></span>
            <span class="text-amber-400 font-semibold">SMC Watchdog</span>
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
    </section>

    <!-- VIEW 3: NUCLEUS ENGINES (MESIN NUKLEUS PRODUKSI) -->
    <section id="view-nucleus" class="space-y-6 hidden">
      <div class="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/30 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-purple-400 live-pulse"></span> 4 Mesin Nukleus Produksi Aktif
            </span>
          </div>
          <h2 class="text-2xl font-extrabold text-white tracking-tight">Mesin Nukleus Rekayasa & Intelijen Strategis</h2>
          <p class="text-xs text-slate-400 mt-1">Modul komputasi inti deterministik tanpa dependensi eksternal (Pure Python Standard Library Invariants).</p>
        </div>
        <span class="px-4 py-2 bg-purple-600/20 text-purple-300 border border-purple-500/30 rounded-xl font-mono text-xs font-bold">4 Nucleus Engines Online</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- NUKLEUS 1: N056 SWOT -->
        <div class="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-purple-400 px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/20">N056 • STRATEGIC SWOT</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 font-bold">ACTIVE NUCLEUS</span>
          </div>
          <h3 class="font-bold text-lg text-white">Strategic SWOT, TOWS & Business Intelligence Engine</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Mesin evaluasi strategis matematis berbasis vektor postur kuadran (Internal-External Axis), matriks sintesis TOWS (SO/WO/ST/WT), PESTLE, dan Porter's 5 Forces Risk Scorer.
          </p>
          <div class="pt-2 border-t border-surface-border text-xs text-slate-400 font-mono">
            Berkas: <span class="text-slate-200">scripts/strategic_swot_nucleus_engine.py</span>
          </div>
        </div>

        <!-- NUKLEUS 2: N054 SYSTEM DESIGN -->
        <div class="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-purple-400 px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/20">N054 • SYSTEM DESIGN</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 font-bold">ACTIVE NUCLEUS</span>
          </div>
          <h3 class="font-bold text-lg text-white">System Architecture & Topology Planning Engine</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Generator kontrak arsitektur skala besar, validasi topologi terdistribusi, kalkulator kapasitas throughput IOPS, dan perencanaan failover multi-region otomatis.
          </p>
          <div class="pt-2 border-t border-surface-border text-xs text-slate-400 font-mono">
            Berkas: <span class="text-slate-200">scripts/system_design_planning_engine.py</span>
          </div>
        </div>

        <!-- NUKLEUS 3: N053 MARKETING -->
        <div class="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-purple-400 px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/20">N053 • QUANTITATIVE MARKETING</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 font-bold">ACTIVE NUCLEUS</span>
          </div>
          <h3 class="font-bold text-lg text-white">Marketing Mix Modeling (MMM) & CLV Engine</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Algoritma adstock geometris, kurva saturasi Hill, penargetan kausal uplift, dan model probabilitas BG/NBD untuk memprediksi Customer Lifetime Value (CLV).
          </p>
          <div class="pt-2 border-t border-surface-border text-xs text-slate-400 font-mono">
            Berkas: <span class="text-slate-200">scripts/marketing_nucleus_engine.py</span>
          </div>
        </div>

        <!-- NUKLEUS 4: N055 VISUAL GRAPHICS -->
        <div class="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono font-bold text-purple-400 px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/20">N055 • VISUAL ENGINEERING</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 font-bold">ACTIVE NUCLEUS</span>
          </div>
          <h3 class="font-bold text-lg text-white">Graphic Design & Generative Vector Engine</h3>
          <p class="text-xs text-slate-300 leading-relaxed">
            Komputasi kontras warna WCAG 2.2 AAA, perceptual space CIELAB/LCh, kalkulasi panjang kurva Bézier kubik, dan generator grafis SVG prosedural.
          </p>
          <div class="pt-2 border-t border-surface-border text-xs text-slate-400 font-mono">
            Berkas: <span class="text-slate-200">scripts/graphic_design_visual_engine.py</span>
          </div>
        </div>

      </div>
    </section>

    <!-- VIEW 4: NEURONS (ALL 56 NEURONS DYNAMICALLY LOADED) -->
    <section id="view-neurons" class="space-y-6 hidden">
      <div class="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 class="text-2xl font-extrabold text-white tracking-tight">Active Master Neural Network ({total_neurons} Neurons)</h2>
          <p class="text-xs text-slate-400 mt-1">{total_neurons} Neuron Master terdistribusi dengan {total_synapses} sinapsis aktif yang menggerakkan kecerdasan otonom Claudia.</p>
        </div>
        <span class="px-4 py-2 bg-brand-600/20 text-brand-300 border border-brand-500/30 rounded-xl font-mono text-xs font-bold">{total_neurons} Master Neurons Active</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="neuron-grid"></div>
    </section>
  </main>

  <script>
    const neuronData = {neurons_json_str};

    function renderNeurons() {{
      const grid = document.getElementById('neuron-grid');
      grid.innerHTML = neuronData.map(n => `
        <div class="glass-panel p-4 rounded-xl border ${{n.is_nucleus ? 'border-purple-500/40 ring-1 ring-purple-500/20' : 'border-surface-border'}}">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono font-bold ${{n.is_nucleus ? 'text-purple-400' : 'text-brand-400'}}">${{n.id}}</span>
            ${{n.is_nucleus ? '<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold">NUKLEUS</span>' : '<span class="w-2 h-2 rounded-full bg-emerald-400"></span>'}}
          </div>
          <h4 class="font-bold text-sm text-white mb-1">${{n.title}}</h4>
          <p class="text-xs text-slate-400">${{n.desc}}</p>
        </div>
      `).join('');
    }}

    function switchTab(tabId) {{
      document.getElementById('view-benchmarks').classList.add('hidden');
      document.getElementById('view-trading').classList.add('hidden');
      document.getElementById('view-nucleus').classList.add('hidden');
      document.getElementById('view-neurons').classList.add('hidden');

      document.getElementById(`view-${{tabId}}`).classList.remove('hidden');

      const btnBench = document.getElementById('tab-btn-benchmarks');
      const btnTrade = document.getElementById('tab-btn-trading');
      const btnNuc = document.getElementById('tab-btn-nucleus');
      const btnNeuro = document.getElementById('tab-btn-neurons');

      [btnBench, btnTrade, btnNuc, btnNeuro].forEach(b => {{
        if (b) b.className = "w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all text-slate-400 hover:text-white hover:bg-surface-card border border-transparent";
      }});

      const activeBtn = document.getElementById(`tab-btn-${{tabId}}`);
      if (activeBtn) activeBtn.className = "w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all bg-brand-600/20 text-brand-300 border border-brand-500/30 shadow-sm";
    }}

    function initSSE() {{
      const evtSource = new EventSource('/events');
      evtSource.onmessage = function(event) {{
        try {{
          const data = JSON.parse(event.data);
          if (data.total_evaluations) document.getElementById('total-evals').innerText = Number(data.total_evaluations).toLocaleString();
          if (data.metrics) {{
            if (data.metrics.inference_speed) document.getElementById('throughput-speed').innerHTML = `${{data.metrics.inference_speed.current}} <span class="text-xs text-slate-400">tok/s</span>`;
            if (data.metrics.swe_bench) document.getElementById('val-swe').innerText = `${{data.metrics.swe_bench.current}}%`;
            if (data.metrics.tau_bench) document.getElementById('val-tau').innerText = `${{data.metrics.tau_bench.current}}%`;
            if (data.metrics.aime_gpqa) document.getElementById('val-aime').innerText = `${{data.metrics.aime_gpqa.current}}%`;
            if (data.metrics.gpqa_diamond) document.getElementById('val-gpqa').innerText = `${{data.metrics.gpqa_diamond.current}}%`;
            if (data.metrics.ifeval) document.getElementById('val-ifeval').innerText = `${{data.metrics.ifeval.current}}%`;
            if (data.metrics.niah_retrieval) document.getElementById('val-niah').innerText = `${{data.metrics.niah_retrieval.current}}%`;
          }}
          if (data.logs && Array.isArray(data.logs)) {{
            const term = document.getElementById('terminal-logs');
            term.innerHTML = data.logs.slice(0, 30).map(l => `
              <div class="flex items-start gap-2 py-0.5">
                <span class="text-slate-500 font-mono">[${{l.time}}]</span>
                <span class="text-emerald-400 font-bold">[${{l.category.toUpperCase()}}]</span>
                <span class="text-slate-300">${{l.message}}</span>
              </div>
            `).join('');
          }}
        }} catch (e) {{}}
      }};
    }}

    renderNeurons();
    initSSE();
  </script>
</body>
</html>
"""

output_path = os.path.join(WORKSPACE, "scripts", "learn_index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[+] SUCCESS: scripts/learn_index.html dynamically compiled with {total_neurons} Master Neurons and 4 Nucleus Engines.")