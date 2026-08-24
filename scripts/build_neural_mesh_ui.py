import os

html = """<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <title>Claudia 5.0 Max — Autonomous Neural Synapse Mesh</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <style>
    * { 
      margin: 0; 
      padding: 0; 
      box-sizing: border-box;
      -webkit-user-select: none !important;
      -moz-user-select: none !important;
      -ms-user-select: none !important;
      user-select: none !important;
      -webkit-user-drag: none !important;
      -webkit-touch-callout: none !important;
    }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #02040a;
      color: #f8fafc;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }
    .mono { font-family: 'JetBrains Mono', monospace; }
    canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .glass-card {
      background: rgba(8, 12, 24, 0.88);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
    }
    @keyframes pulse-ring {
      0% { transform: scale(0.95); opacity: 0.85; }
      50% { transform: scale(1.2); opacity: 0.25; }
      100% { transform: scale(0.95); opacity: 0.85; }
    }
    .pulse-indicator {
      animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* ANTI-SCREENSHOT & ANTI-PRINT DRM SHIELD */
    @media print {
      html, body, canvas, div, header, main {
        display: none !important;
        visibility: hidden !important;
      }
    }
    .shield-blur {
      filter: blur(25px) grayscale(100%) !important;
      transition: filter 0.2s ease;
    }
    .watermark-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 5;
      background: repeating-linear-gradient(
        45deg,
        rgba(255, 255, 255, 0.006) 0px,
        rgba(255, 255, 255, 0.006) 100px,
        rgba(139, 92, 246, 0.012) 100px,
        rgba(139, 92, 246, 0.012) 200px
      );
    }
  </style>
</head>
<body id="appBody" class="relative flex items-center justify-center select-none" oncontextmenu="return false;" onselectstart="return false;" ondragstart="return false;">

  <!-- Security Dynamic Watermark Texture -->
  <div class="watermark-overlay"></div>

  <!-- Interactive Neural Canvas -->
  <canvas id="neuralCanvas"></canvas>

  <!-- Floating Header HUD -->
  <header class="absolute top-6 left-6 right-6 z-10 flex items-center justify-between pointer-events-none">
    <div class="glass-card px-5 py-3.5 rounded-2xl flex items-center gap-3.5 pointer-events-auto border border-purple-500/20">
      <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-purple-500/30">
        <i class="fa-solid fa-brain text-white text-xl"></i>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-extrabold text-base tracking-tight text-white">Claudia 5.0 Max</h1>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-bold border border-emerald-500/30">Read-Only Shield</span>
        </div>
        <p class="text-[11px] text-slate-400 font-medium">Gahar Inovasi Teknologi &bull; 40 Master Neurons &bull; Protected IP</p>
      </div>
    </div>

    <!-- Live Telemetry Status Pills -->
    <div class="flex items-center gap-3 pointer-events-auto">
      <div class="glass-card px-3.5 py-2 rounded-xl flex items-center gap-2 text-xs font-mono text-emerald-400 border border-emerald-500/20">
        <i class="fa-solid fa-shield-halved"></i>
        <span>DRM Guard: <strong class="text-white">Active</strong></span>
      </div>
      <div class="glass-card px-4 py-2.5 rounded-xl flex items-center gap-2.5 text-xs font-mono text-slate-300">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 pulse-indicator"></span>
        <span>Throughput: <strong class="text-emerald-400" id="firing-rate">248 Hz</strong></span>
      </div>
      <div class="glass-card px-4 py-2.5 rounded-xl flex items-center gap-2.5 text-xs font-mono text-slate-300">
        <i class="fa-solid fa-bolt text-amber-400"></i>
        <span>Synapses: <strong class="text-amber-300">168 Pathways</strong></span>
      </div>
    </div>
  </header>

  <!-- Neuron Detail Inspector Modal (Bottom Right) -->
  <div id="inspector" class="absolute bottom-6 right-6 w-96 glass-card p-5 rounded-2xl z-10 border border-indigo-500/20 transition-all duration-300 transform translate-y-2 opacity-95">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-mono font-bold text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20" id="inspect-id">N040</span>
      <span class="text-[11px] font-mono text-emerald-400 flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Synapse Online
      </span>
    </div>
    <h3 class="font-bold text-sm text-white mb-1.5 tracking-tight" id="inspect-title">Meta-Cognitive Self-Reflection</h3>
    <p class="text-xs text-slate-400 leading-relaxed mb-3" id="inspect-desc">Reflexion loop, epistemic certainty evaluation, zero-hallucination guardrails & recursive reasoning.</p>
    <div class="pt-2.5 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-500">
      <span>Connected Synapses: <strong class="text-slate-300" id="inspect-conns">8 nodes</strong></span>
      <span class="text-purple-400">Hover / Drag node</span>
    </div>
  </div>

  <!-- Live Pulse Log Overlay (Bottom Left) -->
  <div class="absolute bottom-6 left-6 z-10 glass-card px-4 py-3 rounded-2xl pointer-events-none border border-slate-800 max-w-sm hidden md:block">
    <div class="text-[10px] uppercase font-mono tracking-wider text-slate-500 mb-1">Neuron Cognitive Stream</div>
    <div class="text-xs font-mono text-emerald-400 truncate flex items-center gap-2" id="feed-line">
      <i class="fa-solid fa-wave-square text-emerald-400 text-xs"></i>
      <span>Claudia 5.0 Max: 40 Master Neurons active</span>
    </div>
  </div>

  <script>
    // ==========================================
    // 🛡️ ENTERPRISE CLIENT-SIDE DEFENSE SHIELD
    // ==========================================
    (function initSecurityShield() {
      // 1. Disable Console Scraping & Override methods
      try {
        const noop = function() {};
        ['log', 'debug', 'info', 'warn', 'error', 'table', 'trace', 'dir'].forEach(fn => {
          window.console[fn] = noop;
        });
      } catch (e) {}

      // 2. Prevent Context Menu (Right Click)
      document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }, { capture: true });

      // 3. Prevent Copy, Cut, Paste, Selection, Drag
      ['copy', 'cut', 'paste', 'selectstart', 'dragstart'].forEach(evt => {
        document.addEventListener(evt, function(e) {
          e.preventDefault();
          e.stopPropagation();
          return false;
        }, { capture: true });
      });

      // 4. Block Keyboard Shortcuts (F12, DevTools, View Source, Print, Save, Screen Capture)
      document.addEventListener('keydown', function(e) {
        // F12 or PrintScreen
        if (e.keyCode === 123 || e.key === 'PrintScreen' || e.keyCode === 44) {
          e.preventDefault();
          triggerSecurityBlur();
          return false;
        }
        // Ctrl/Cmd + Shift + (I, J, C, K) [DevTools]
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && ['I','i','J','j','C','c','K','k'].includes(e.key)) {
          e.preventDefault();
          return false;
        }
        // Ctrl/Cmd + (U, S, P, A, C, X) [View Source, Save, Print, SelectAll, Copy, Cut]
        if ((e.ctrlKey || e.metaKey) && ['u','U','s','S','p','P','a','A','c','C','x','X'].includes(e.key)) {
          e.preventDefault();
          return false;
        }
      }, { capture: true });

      // 5. Anti-Screenshot & Tab Switch Blur Shield
      function triggerSecurityBlur() {
        const body = document.getElementById('appBody');
        if (body) {
          body.classList.add('shield-blur');
          setTimeout(() => body.classList.remove('shield-blur'), 2000);
        }
      }

      window.addEventListener('keyup', function(e) {
        if (e.key === 'PrintScreen' || e.keyCode === 44) {
          triggerSecurityBlur();
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText('Protected Content - Gahar Inovasi Teknologi');
          }
        }
      });

      window.addEventListener('blur', function() {
        const body = document.getElementById('appBody');
        if (body) body.classList.add('shield-blur');
      });

      window.addEventListener('focus', function() {
        const body = document.getElementById('appBody');
        if (body) body.classList.remove('shield-blur');
      });

      document.addEventListener('visibilitychange', function() {
        const body = document.getElementById('appBody');
        if (body) {
          if (document.hidden) body.classList.add('shield-blur');
          else body.classList.remove('shield-blur');
        }
      });
    })();

    // ==========================================
    // 🧠 INTERACTIVE NEURAL SYNAPSE CANVAS
    // ==========================================
    const canvas = document.getElementById('neuralCanvas');
    const ctx = canvas.getContext('2d');

    let width, height;
    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    // 40 Active Master Neurons Data
    const neuronsData = [
      { id: "N001", label: "Executive Decisions", category: "Core", desc: "Keputusan teknis cepat tanpa keraguan, root-cause first.", conns: ["N004", "N007", "N022"] },
      { id: "N002", label: "VPS Remote Ops", category: "Infra", desc: "SSH tunneling otomatis, supervisi PM2, isolasi port & deploy.", conns: ["N004", "N006", "N008", "N028", "N032"] },
      { id: "N003", label: "Mobile-First UI/UX", category: "Interface", desc: "Zero browser native popups, light mode default, max 300 LOC.", conns: ["N001", "N004", "N026", "N030"] },
      { id: "N004", label: "Ponytail Minimality", category: "Core", desc: "YAGNI, standard library first, eliminasi kode berlebih.", conns: ["N001", "N005", "N011", "N027", "N029"] },
      { id: "N005", label: "Graphify Knowledge", category: "Memory", desc: "AST code dependency mapper & modular graph RAG.", conns: ["N007", "N009", "N012", "N026"] },
      { id: "N006", label: "9Router Gateway", category: "Gateway", desc: "Low-latency LLM gateway & multi-provider routing.", conns: ["N002", "N010", "N014", "N024", "N030"] },
      { id: "N007", label: "Self-Improving Loop", category: "Core", desc: "Pencatatan invarian otomatis via record_learning.py.", conns: ["N001", "N004", "N008", "N015", "N028", "N040"] },
      { id: "N008", label: "Live Session State", category: "State", desc: "State persistensi ekosistem server, Jellyfin & Cloud NAS.", conns: ["N002", "N006", "N010", "N028", "N032"] },
      { id: "N009", label: "Peak Algorithms", category: "Math", desc: "Tarjan SCC, Segment Tree, Bloom Filter, Lock-Free.", conns: ["N004", "N005", "N011", "N013", "N017", "N025", "N029"] },
      { id: "N010", label: "Distributed Systems", category: "Infra", desc: "Raft/Paxos consensus, CQRS, 2PC & Saga transactions.", conns: ["N006", "N008", "N009", "N013", "N022", "N028", "N035"] },
      { id: "N011", label: "Mechanical Sympathy", category: "Perf", desc: "L1/L2 cache locality, Linux sendfile zero-copy, io_uring.", conns: ["N004", "N009", "N010", "N015", "N027", "N029"] },
      { id: "N012", label: "Deep Search GraphRAG", category: "Memory", desc: "BM25 + Dense vector semantic, RRF, multi-hop traversal.", conns: ["N005", "N009", "N015", "N018", "N026", "N031"] },
      { id: "N013", label: "Deep Storage & LSM", category: "Infra", desc: "MemTable/SSTable compaction, WAL, HNSW vector index.", conns: ["N009", "N010", "N011", "N031"] },
      { id: "N014", label: "Zero-Trust Security", category: "Security", desc: "PASETO tokens, constant-time crypto, tamper signature.", conns: ["N006", "N008", "N010", "N018", "N023", "N024", "N038"] },
      { id: "N015", label: "Compiler AST & Profiler", category: "Perf", desc: "Tree-Sitter AST visitors, WASM, CPU flamegraphs.", conns: ["N005", "N007", "N011", "N012", "N018", "N027", "N029", "N034"] },
      { id: "N016", label: "Benchmark Evaluator", category: "Eval", desc: "Framework pengujian empiris 6 parameter deterministik.", conns: ["N007", "N017", "N018", "N019", "N022", "N028"] },
      { id: "N017", label: "Program-Aided Math", category: "Math", desc: "Invariant proof, Diophantine modular parity, PAL.", conns: ["N009", "N016", "N024", "N025"] },
      { id: "N018", label: "RepoMap AST SWE-bench", category: "Eval", desc: "PageRank AST callgraph, root-cause patch precision.", conns: ["N012", "N015", "N016", "N023"] },
      { id: "N019", label: "BFCL Tool Schema Oracle", category: "Eval", desc: "Negative constraint checking, compensating rollback.", conns: ["N006", "N014", "N016", "N022"] },
      { id: "N020", label: "Session Continuity", category: "State", desc: "Multi-IDE state synchronization & connection resilience.", conns: ["N008", "N016", "N019"] },
      { id: "N021", label: "Quantitative Gold & Crypto", category: "Finance", desc: "Invarian trading XAU/USD & Kripto, SMC/FVG, ATR RRR 1:3.", conns: ["N001", "N009", "N010", "N016", "N025"] },
      { id: "N022", label: "Multi-Agent Consensus", category: "Swarm", desc: "MCTS swarm deliberation, voting DAG, Byzantine Fault Tolerance.", conns: ["N001", "N010", "N016", "N019", "N028"] },
      { id: "N023", label: "Zero-Day Kernel Defense", category: "Security", desc: "Shadow Stack CFI, eBPF telemetry, buffer overrun protection.", conns: ["N014", "N018", "N028", "N038"] },
      { id: "N024", label: "Post-Quantum Cryptography", category: "Security", desc: "NIST FIPS 203/204 ML-KEM/ML-DSA, Lattice Ring arithmetic.", conns: ["N006", "N014", "N017"] },
      { id: "N025", label: "HFT Orderbook Microstructure", category: "Finance", desc: "L2/L3 orderbook delta, Stoikov micro-price, Kelly criterion.", conns: ["N009", "N017", "N021", "N027"] },
      { id: "N026", label: "Vision-DOM Geometry AST", category: "Multimodal", desc: "Pixel-to-DOM layout tree, viewport coordinate bounds, OCR alignment.", conns: ["N003", "N005", "N012", "N036"] },
      { id: "N027", label: "Tensor SIMD Vectorization", category: "Perf", desc: "512-bit AVX-512 FMA registers, 64-byte cache alignment, SoA.", conns: ["N004", "N011", "N015", "N025"] },
      { id: "N028", label: "Autonomous Self-Healing", category: "Infra", desc: "Level-triggered state reconciliation, adaptive failure detection.", conns: ["N002", "N007", "N008", "N010", "N016", "N022", "N023"] },
      { id: "N029", label: "Modern Systems Rust & Go", category: "Stack", desc: "Rust 2024 async Tokio, lock-free SPSC, Go 1.23 iter.Seq.", conns: ["N004", "N009", "N011", "N015", "N027", "N037"] },
      { id: "N030", label: "Next-Gen Fullstack & Edge", category: "Stack", desc: "Next.js 15, React 19 Compiler, Bun 1.2, Hono v4, Tailwind v4.", conns: ["N003", "N006", "N026", "N031", "N032", "N036"] },
      { id: "N031", label: "Modern Data pgvector & ORM", category: "Stack", desc: "PostgreSQL 17 HNSW vector search, RRF, Drizzle ORM, SQLite WAL.", conns: ["N012", "N013", "N030", "N036"] },
      { id: "N032", label: "Cloud-Native Edge Infra", category: "Stack", desc: "Caddy 2.8+ HTTP/3 QUIC, Docker Distroless, PM2 cluster.", conns: ["N002", "N008", "N028", "N030", "N035"] },
      { id: "N033", label: "Python 3.12+ Concurrency", category: "Stack", desc: "Free-Threaded No-GIL, asyncio TaskGroups, Polars Arrow.", conns: ["N004", "N009", "N011", "N015", "N027"] },
      { id: "N034", label: "Runtime Profiler & Memory Oracle", category: "Diagnostics", desc: "eBPF zero-overhead profiling, CPU flamegraphs, pprof, leak detection.", conns: ["N011", "N015", "N028", "N033"] },
      { id: "N035", label: "Ultra-Scale Streaming CQRS", category: "Streaming", desc: "Kafka / Redpanda / NATS, Event Sourcing, Transactional Outbox, DLQ.", conns: ["N010", "N013", "N031", "N032"] },
      { id: "N036", label: "Fullstack Product Synthesizer", category: "Synthesis", desc: "0-to-1 fullstack generation, Playwright E2E assertion, Hono & Next.js 15.", conns: ["N003", "N026", "N030", "N031"] },
      { id: "N037", label: "WASM & Micro-VM Sandboxing", category: "Virtualization", desc: "Firecracker Micro-VMs, Wasmtime, V8 isolates, zero-trust plugin runtime.", conns: ["N006", "N023", "N029", "N032"] },
      { id: "N038", label: "Red Team & Auto-CVE Patching", category: "Security", desc: "OWASP Top 10 fuzzing, SAST/DAST AST analysis, automated vulnerability remediation.", conns: ["N014", "N023", "N034"] },
      { id: "N039", label: "WebRTC & Media DSP Streaming", category: "Media", desc: "Ultra-low latency <100ms, SFU mesh, Opus/AV1 hardware transcoding, jitter buffer.", conns: ["N011", "N027", "N030"] },
      { id: "N040", label: "Meta-Cognitive Self-Reflection", category: "Reasoning", desc: "Reflexion loop, Tree-of-Thoughts / MCTS meta-prompting, zero-hallucination.", conns: ["N001", "N007", "N016", "N022"] }
    ];

    const nodes = [];
    const centerX = width / 2;
    const centerY = height / 2;
    const radiusBase = Math.min(width, height) * 0.40;

    neuronsData.forEach((data, i) => {
      const angle = (i / neuronsData.length) * Math.PI * 2 + (Math.random() * 0.1);
      const r = radiusBase * (0.45 + Math.random() * 0.6);
      nodes.push({
        ...data,
        x: centerX + Math.cos(angle) * r,
        y: centerY + Math.sin(angle) * r,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: 8 + Math.random() * 4,
        baseRadius: 9,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.02 + Math.random() * 0.03,
        glowIntensity: 0.6,
        isHovered: false
      });
    });

    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = n);

    const signals = [];
    function spawnSignal() {
      const source = nodes[Math.floor(Math.random() * nodes.length)];
      if (source.conns && source.conns.length > 0) {
        const targetId = source.conns[Math.floor(Math.random() * source.conns.length)];
        const target = nodeMap[targetId];
        if (target) {
          signals.push({
            from: source,
            to: target,
            progress: 0,
            speed: 0.009 + Math.random() * 0.015,
            color: Math.random() > 0.35 ? '#a855f7' : (Math.random() > 0.5 ? '#10b981' : '#38bdf8'),
            size: 2.5 + Math.random() * 2
          });
        }
      }
    }

    let hoveredNode = null;
    let draggedNode = null;
    let mouse = { x: -1000, y: -1000 };

    window.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;

      let found = null;
      for (const node of nodes) {
        const dist = Math.hypot(node.x - mouse.x, node.y - mouse.y);
        if (dist < node.radius + 14) {
          found = node;
          break;
        }
      }

      if (found !== hoveredNode) {
        if (hoveredNode) hoveredNode.isHovered = false;
        hoveredNode = found;
        if (hoveredNode) {
          hoveredNode.isHovered = true;
          updateInspector(hoveredNode);
        }
      }

      if (draggedNode) {
        draggedNode.x = mouse.x;
        draggedNode.y = mouse.y;
      }
    });

    window.addEventListener('mousedown', () => {
      if (hoveredNode) draggedNode = hoveredNode;
    });

    window.addEventListener('mouseup', () => {
      draggedNode = null;
    });

    function updateInspector(n) {
      document.getElementById('inspect-id').innerText = n.id;
      document.getElementById('inspect-title').innerText = n.label;
      document.getElementById('inspect-desc').innerText = n.desc;
      document.getElementById('inspect-conns').innerText = `${n.conns ? n.conns.length : 0} synap links`;

      const feed = document.getElementById('feed-line');
      if (feed) {
        feed.innerHTML = `<i class="fa-solid fa-bolt text-amber-400 text-xs"></i> <span>Neuron ${n.id} active: ${n.label}</span>`;
      }
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      const bgGrad = ctx.createRadialGradient(width/2, height/2, 50, width/2, height/2, width * 0.7);
      bgGrad.addColorStop(0, 'rgba(124, 58, 237, 0.12)');
      bgGrad.addColorStop(0.5, 'rgba(16, 185, 129, 0.05)');
      bgGrad.addColorStop(1, 'rgba(2, 4, 10, 0)');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      if (Math.random() < 0.5) spawnSignal();

      nodes.forEach(node => {
        if (node !== draggedNode) {
          node.x += node.vx;
          node.y += node.vy;
          if (node.x < 70 || node.x > width - 70) node.vx *= -1;
          if (node.y < 70 || node.y > height - 70) node.vy *= -1;
        }
        node.pulse += node.pulseSpeed;
      });

      nodes.forEach(source => {
        if (source.conns) {
          source.conns.forEach(targetId => {
            const target = nodeMap[targetId];
            if (target) {
              ctx.beginPath();
              ctx.moveTo(source.x, source.y);
              ctx.lineTo(target.x, target.y);

              const isHighlighted = (source.isHovered || target.isHovered);
              ctx.strokeStyle = isHighlighted 
                ? 'rgba(167, 139, 250, 0.8)' 
                : 'rgba(99, 102, 241, 0.14)';
              ctx.lineWidth = isHighlighted ? 2.2 : 1;
              ctx.stroke();
            }
          });
        }
      });

      for (let i = signals.length - 1; i >= 0; i--) {
        const s = signals[i];
        s.progress += s.speed;
        if (s.progress >= 1) {
          signals.splice(i, 1);
          continue;
        }

        const currX = s.from.x + (s.to.x - s.from.x) * s.progress;
        const currY = s.from.y + (s.to.y - s.from.y) * s.progress;

        ctx.beginPath();
        ctx.arc(currX, currY, s.size, 0, Math.PI * 2);
        ctx.fillStyle = s.color;
        ctx.shadowColor = s.color;
        ctx.shadowBlur = 14;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      nodes.forEach(node => {
        const pulseFactor = Math.sin(node.pulse) * 2;
        const currentRadius = (node.isHovered ? node.baseRadius * 1.5 : node.baseRadius) + pulseFactor;

        const auraGrad = ctx.createRadialGradient(node.x, node.y, 2, node.x, node.y, currentRadius * 3.2);
        auraGrad.addColorStop(0, node.isHovered ? 'rgba(167, 139, 250, 0.95)' : 'rgba(124, 58, 237, 0.55)');
        auraGrad.addColorStop(1, 'rgba(124, 58, 237, 0)');
        ctx.fillStyle = auraGrad;
        ctx.beginPath();
        ctx.arc(node.x, node.y, currentRadius * 3.2, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, currentRadius, 0, Math.PI * 2);
        const nid = parseInt(node.id.replace('N',''));
        ctx.fillStyle = node.isHovered ? '#38bdf8' : (nid >= 34 ? '#f59e0b' : (nid >= 29 ? '#38bdf8' : (nid >= 22 ? '#10b981' : '#a855f7')));
        ctx.shadowColor = node.isHovered ? '#38bdf8' : '#a855f7';
        ctx.shadowBlur = 16;
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.font = '600 11px "JetBrains Mono", monospace';
        ctx.fillStyle = node.isHovered ? '#ffffff' : '#cbd5e1';
        ctx.textAlign = 'center';
        ctx.fillText(node.id, node.x, node.y - currentRadius - 6);
      });

      requestAnimationFrame(animate);
    }

    animate();

    setInterval(() => {
      const rate = 235 + Math.floor(Math.random() * 45);
      const el = document.getElementById('firing-rate');
      if (el) el.innerText = `${rate} Hz`;
    }, 1000);

    updateInspector(nodeMap["N040"] || nodes[0]);
  </script>
</body>
</html>
"""

with open('scripts/learn_index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS: 40-Neuron Synapse Canvas with Enterprise Anti-Screenshot & Copy Protection generated.")