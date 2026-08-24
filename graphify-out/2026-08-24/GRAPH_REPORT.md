# Graph Report - Agent_Claudia_Autonomus  (2026-08-24)

## Corpus Check
- 124 files · ~88,681 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 636 nodes · 685 edges · 88 communities (67 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b9560dd0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- ponytail/package.json
- ponytail-runtime.js
- Install
- MultiHopEngine
- README.es.md
- Install
- zolu_learn_server.js
- Ponytail, lazy senior dev mode
- official_runner_real.py
- ⚡ CLAUDIA 2.0 (v5.0.0 Apex)
- claudiacode_server.js
- Ponytail
- Ponytail
- Ponytail Help
- Core Engines & Workflows
- N022_multi_agent_consensus.md
- Ponytail Help
- test_brain.py
- Ponytail, lazy senior dev mode
- train_trading_engine.py
- Ponytail, lazy senior dev mode
- Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia
- Neuron N008: Persistent Live Session Checkpoint & Infrastructure State
- pi-extension/package.json
- parallel_runner.py
- .agents/skills/ponytail-audit/SKILL.md
- Ponytail Gain
- .agents/skills/ponytail-review/SKILL.md
- Core Stack & Architecture
- ponytail-config.js
- ponytail/skills/ponytail-audit/SKILL.md
- Ponytail Gain
- ponytail/skills/ponytail-review/SKILL.md
- .agents/skills/ponytail-debt/SKILL.md
- Feedback Log
- Neuron N003: Mobile-First UI & Compact Data Viz
- ponytail-instructions.js
- Neuron N005: Graphify Knowledge Network
- Neuron N006: 9Router Gateway Engine
- ponytail.mjs
- N009_peak_algorithms_codex.md
- ponytail-activate.js
- Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants
- Neuron N018: RepoMap AST Compression & SWE-bench Precision
- ? 4 Pilar Mikrostruktur & Eksekusi Kuantitatif
- Self-Learning Framework
- ponytail/skills/ponytail-debt/SKILL.md
- ingest_frontier_knowledge.py
- masterpiece_completer.py
- record_learning.py
- /graphify
- Knowledge Base Index
- Neuron N002: VPS Remote Operations & Pipeline
- 🧭 5 Aturan Emas Spatial Reasoning & DOM Geometry
- N011_mechanical_sympathy_perf.md
- N012_deep_search_and_graph_rag.md
- N013_deep_storage_and_distributed_db.md
- Neuron N024: Post-Quantum Cryptography & ML-KEM/ML-DSA (FIPS 203/204)
- N015_compiler_ast_and_system_profiling.md
- Playbook: Graphify Workflow
- Playbooks
- Playbook: Self-Improving Mechanism
- grow_neurons.py
- auto_sync_github.py
- rules/graphify.md
- workflows/graphify.md
- reflections/README.md
- ai_engine_9router.md
- mojoloker_brand.md
- ui_ux_design_rules.md
- user_profile.md
- vps_infrastructure.md
- ponytail-statusline.sh script
- 🎯 Invarian Inti Perdagangan Kuantitatif (Trading Invariants)
- Neuron N028: Autonomous System Self-Healing & Distributed Chaos Invariants
- N027_tensor_simd_vectorization.md

## God Nodes (most connected - your core abstractions)
1. `Install` - 15 edges
2. `getPonytailInstructions()` - 13 edges
3. `ponytailExtension()` - 13 edges
4. `Install` - 12 edges
5. `normalizePersistedMode()` - 11 edges
6. `files` - 11 edges
7. `Instalación` - 11 edges
8. `getDefaultMode()` - 9 edges
9. `finish()` - 9 edges
10. `⚡ CLAUDIA 2.0 (v5.0.0 Apex)` - 9 edges

## Surprising Connections (you probably didn't know these)
- `readMode()` --calls--> `normalizePersistedMode()`  [EXTRACTED]
  ponytail/.opencode/plugins/ponytail.mjs → ponytail/hooks/ponytail-config.js
- `parsePonytailCommand()` --calls--> `normalizeMode()`  [EXTRACTED]
  ponytail/pi-extension/index.js → ponytail/hooks/ponytail-config.js
- `getPonytailInstructions()` --calls--> `normalizePersistedMode()`  [EXTRACTED]
  ponytail/hooks/ponytail-instructions.js → ponytail/hooks/ponytail-config.js
- `ponytailExtension()` --calls--> `isDeactivationCommand()`  [EXTRACTED]
  ponytail/pi-extension/index.js → ponytail/hooks/ponytail-config.js
- `finish()` --calls--> `getDefaultMode()`  [EXTRACTED]
  ponytail/hooks/ponytail-mode-tracker.js → ponytail/hooks/ponytail-config.js

## Import Cycles
- None detected.

## Communities (88 total, 21 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.18
Nodes (11): normalizePersistedMode(), {
  DEFAULT_MODE,
  RUNTIME_MODES,
  getDefaultMode,
  getQuietStartup,
  getHideStatus,
  normalizeMode,
  normalizePersistedMode,
  isDeactivationCommand,
  writeDefaultMode,
}, { getPonytailInstructions, filterSkillBodyForMode }, parsePonytailCommand(), ponytailExtension(), readDefaultMode, readQuietStartup, require (+3 more)

### Community 1 - "ponytail/package.json"
Cohesion: 0.05
Nodes (40): author, name, url, bugs, url, description, exports, ./plugin (+32 more)

### Community 2 - "ponytail-runtime.js"
Cohesion: 0.16
Nodes (17): isDeactivationCommand(), writeDefaultMode(), { clearMode, isQoder, readMode, setMode, writeHookOutput }, finish(), { getDefaultMode, isDeactivationCommand, writeDefaultMode }, { getPonytailInstructions }, clearMode(), fs (+9 more)

### Community 3 - "Install"
Cohesion: 0.07
Nodes (25): Ponytail, lazy senior dev mode, Antigravity CLI, Before / after, Claude Code, CodeWhale, Codex, Commands, Development (+17 more)

### Community 4 - "MultiHopEngine"
Cohesion: 0.10
Nodes (14): Local Benchmark Evaluator & Verification Harness for Claudia 2.0 Includes SWE-…, run_evaluation_checks(), MultiHopEngine, Any, Multi-Hop Query Decomposer & GraphRAG Traversal Engine Author: Claudia…, Decomposes complex questions into atomic 1-hop sub-queries., Traverse knowledge graph from start entity up to max_depth hops., Reciprocal Rank Fusion (RRF) combining keyword and graph results. (+6 more)

### Community 5 - "README.es.md"
Cohesion: 0.09
Nodes (21): Ponytail, lazy senior dev mode, Antes / después, Antigravity CLI, Claude Code, CodeWhale, Codex, Comandos, Cómo funciona (+13 more)

### Community 6 - "Install"
Cohesion: 0.09
Nodes (21): Antigravity CLI, Before / after, Claude Code, CodeWhale, Codex, Commands, Development, Devin CLI (+13 more)

### Community 7 - "zolu_learn_server.js"
Cohesion: 0.12
Nodes (14): app, broadcastState(), clients, cors, { exec }, express, fs, https (+6 more)

### Community 8 - "Ponytail, lazy senior dev mode"
Cohesion: 0.14
Nodes (11): Graphify, Brain Verification & Continuous Learning Loop:, ?? Kerahasiaan Arsitektur & Perlindungan Hak Cipta (Proprietary IP Shield):, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder, 🧠 Active Memory Neurons (+3 more)

### Community 9 - "official_runner_real.py"
Cohesion: 0.27
Nodes (11): compress_ast_context(), eval_single_task(), get_cache_key(), init_db(), query_llm(), Real Production AI Benchmark Evaluator for Claudia (9Router LLM Engine)…, Safely execute Python code generated by LLM, extracting all variables and…, Compress Python code AST removing docstrings and whitespace bloat while… (+3 more)

### Community 10 - "⚡ CLAUDIA 2.0 (v5.0.0 Apex)"
Cohesion: 0.20
Nodes (9): 🌌 1. Filosofi Rekayasa Inti: *The Minimality Ladder*, 🧠 2. Cognitive Neural Mesh (16 Master Neurons), 🧪 3. Framework Tolok Ukur 6 Parameter (Frontier Real Evaluator), 🌐 4. Ekosistem Layanan Aktif (*Production Cluster*), 📊 5. Telemetri VPS & Kecepatan Jaringan Real-Time, 🛠️ 6. Persenjataan & Toolkit Terpasang, 🔒 7. Zero-Trust Security & Vault Isolation, *Autonomous Senior Engineering Partner & Cognitive Neural Mesh* (+1 more)

### Community 11 - "claudiacode_server.js"
Cohesion: 0.20
Nodes (9): app, compression, cors, Database, db, DB_PATH, express, fs (+1 more)

### Community 12 - "Ponytail"
Cohesion: 0.22
Nodes (8): Boundaries, Intensity, Output, Persistence, Ponytail, Rules, The ladder, When NOT to be lazy

### Community 13 - "Ponytail"
Cohesion: 0.22
Nodes (8): Boundaries, Intensity, Output, Persistence, Ponytail, Rules, The ladder, When NOT to be lazy

### Community 14 - "Ponytail Help"
Cohesion: 0.25
Nodes (7): Configure Default Mode, Deactivate, Levels, More, Ponytail Help, Skills, Update

### Community 15 - "Core Engines & Workflows"
Cohesion: 0.25
Nodes (7): 1. Ponytail (Lazy Senior Dev Engine), 2. Graphify (Knowledge Graph & Structural Memory), 3. 9Router (AI Gateway & Model Routing), Core Engines & Workflows, Identity: Claudia, Karakter & Gaya Komunikasi, Self-Learning Loop

### Community 16 - "N022_multi_agent_consensus.md"
Cohesion: 0.05
Nodes (35): Core Concept, Neuron N001: Executive Decision Making, Synaptic Links, Triggers & Heuristics, Core Concept, Neuron N004: Ponytail Minimality Ladder, Synaptic Links, Core Concept (+27 more)

### Community 17 - "Ponytail Help"
Cohesion: 0.25
Nodes (7): Configure Default Mode, Deactivate, Levels, More, Ponytail Help, Skills, Update

### Community 18 - "test_brain.py"
Cohesion: 0.46
Nodes (7): run_all(), test_ide_bridges(), test_identity_tamper_lock(), test_knowledge_graph(), test_memory_layer(), test_neuron_network(), test_security_and_secrets()

### Community 19 - "Ponytail, lazy senior dev mode"
Cohesion: 0.29
Nodes (6): Graphify Knowledge Graph:, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder

### Community 20 - "train_trading_engine.py"
Cohesion: 0.52
Nodes (6): calculate_atr(), calculate_ema(), calculate_rsi(), detect_smc_fair_value_gaps(), fetch_binance_klines(), train_and_synthesize_neuron()

### Community 21 - "Ponytail, lazy senior dev mode"
Cohesion: 0.29
Nodes (6): Graphify Knowledge Graph:, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder

### Community 22 - "Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia"
Cohesion: 0.33
Nodes (5): 1. Tampilan & Mode, 2. Dropdown & Komponen Formulir, 3. Responsivitas Mobile, 4. Branding & Desain Khusus MojoLoker, Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia

### Community 23 - "Neuron N008: Persistent Live Session Checkpoint & Infrastructure State"
Cohesion: 0.33
Nodes (5): 🚀 Deployed Ecosystem & Port Mappings, 🛠️ Installed Autonomous Fullstack & Security Toolkit, 🎬 Media Engine & Strict Subtitle Cleaner, 📌 Metadata, Neuron N008: Persistent Live Session Checkpoint & Infrastructure State

### Community 24 - "pi-extension/package.json"
Cohesion: 0.33
Nodes (5): name, private, scripts, test, type

### Community 25 - "parallel_runner.py"
Cohesion: 0.53
Nodes (5): eval_single_task(), init_db(), query_llm(), High-Speed Parallel Subagent Benchmark Evaluator for Claudia Features Valid…, run_parallel_subagents_step()

### Community 26 - ".agents/skills/ponytail-audit/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Hunt, Output, Tags

### Community 27 - "Ponytail Gain"
Cohesion: 0.40
Nodes (4): Boundaries, Honesty boundary, Ponytail Gain, Scoreboard

### Community 28 - ".agents/skills/ponytail-review/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Examples, Format, Scoring

### Community 29 - "Core Stack & Architecture"
Cohesion: 0.40
Nodes (4): 1. Database & Storage, 2. Web & Service Stack, 3. Engineering & Intelligence Engines, Core Stack & Architecture

### Community 30 - "ponytail-config.js"
Cohesion: 0.14
Nodes (15): fs, getClaudeDir(), getConfigDir(), getConfigPath(), getHideStatus(), getQuietStartup(), normalizeConfigMode(), os (+7 more)

### Community 31 - "ponytail/skills/ponytail-audit/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Hunt, Output, Tags

### Community 32 - "Ponytail Gain"
Cohesion: 0.40
Nodes (4): Boundaries, Honesty boundary, Ponytail Gain, Scoreboard

### Community 33 - "ponytail/skills/ponytail-review/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Examples, Format, Scoring

### Community 34 - ".agents/skills/ponytail-debt/SKILL.md"
Cohesion: 0.50
Nodes (3): Boundaries, Output, Scan

### Community 35 - "Feedback Log"
Cohesion: 0.50
Nodes (3): Feedback Log, Log 001 - Inisialisasi Persona, Log 002 - Executive Decision Making (Anti-Pilihan Berlebih)

### Community 36 - "Neuron N003: Mobile-First UI & Compact Data Viz"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N003: Mobile-First UI & Compact Data Viz, Synaptic Links

### Community 37 - "ponytail-instructions.js"
Cohesion: 0.18
Nodes (14): normalizeMode(), { DEFAULT_MODE, normalizeMode, normalizePersistedMode }, filterSkillBodyForMode(), fs, getFallbackInstructions(), getPonytailInstructions(), INDEPENDENT_MODES, path (+6 more)

### Community 38 - "Neuron N005: Graphify Knowledge Network"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N005: Graphify Knowledge Network, Synaptic Links

### Community 39 - "Neuron N006: 9Router Gateway Engine"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N006: 9Router Gateway Engine, Synaptic Links

### Community 40 - "ponytail.mjs"
Cohesion: 0.20
Nodes (9): getDefaultMode(), __dirname, parseCommandFile(), { getDefaultMode, normalizePersistedMode }, { getPonytailInstructions }, { parseCommandFile }, readMode(), require (+1 more)

### Community 41 - "N009_peak_algorithms_codex.md"
Cohesion: 0.50
Nodes (3): 1. Graph & Network Flow Algorithms, 2. Probabilistic & Spatial Data Structures, 3. High-Performance Concurrency & Rate Limiting

### Community 42 - "ponytail-activate.js"
Cohesion: 0.18
Nodes (10): claudeDir, {
  clearMode,
  isCodex,
  isCopilot,
  setMode,
  writeHookOutput,
}, fs, { getDefaultMode, getClaudeDir, isShellSafe }, { getPonytailInstructions }, mode, output, path (+2 more)

### Community 43 - "Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants"
Cohesion: 0.50
Nodes (3): 🧮 4 Pilar Heuristik AIME & Olympiad:, 📌 Domain & Karakteristik, Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants

### Community 44 - "Neuron N018: RepoMap AST Compression & SWE-bench Precision"
Cohesion: 0.50
Nodes (3): 🛠️ 4 Aturan Emas Resolusi SWE-bench:, 📌 Domain & Karakteristik, Neuron N018: RepoMap AST Compression & SWE-bench Precision

### Community 45 - "? 4 Pilar Mikrostruktur & Eksekusi Kuantitatif"
Cohesion: 0.20
Nodes (9): 1. L2/L3 Orderbook Delta & Micro-Price Dynamics, 2. Gold (XAU/USD) & DEX Cross-Venue Arbitrage, 3. Fractional Kelly Criterion & Risk of Ruin, 4. Dynamic Slippage & Almgren-Chriss Market Impact, ? 4 Pilar Mikrostruktur & Eksekusi Kuantitatif, ?? Domain & Arsitektur, ?? Invariant Ringkas, Neuron N025: High-Frequency Orderbook Microstructure & HFT Quant Engine (+1 more)

### Community 46 - "Self-Learning Framework"
Cohesion: 0.50
Nodes (3): Alur Pembelajaran, Self-Learning Framework, Struktur Folder

### Community 47 - "ponytail/skills/ponytail-debt/SKILL.md"
Cohesion: 0.50
Nodes (3): Boundaries, Output, Scan

### Community 48 - "ingest_frontier_knowledge.py"
Cohesion: 0.67
Nodes (3): build_all_frontier_datasets(), ensure_dirs(), Automated Frontier Dataset Scraper & Knowledge Ingester for Claudia 2.0 Ingests…

### Community 49 - "masterpiece_completer.py"
Cohesion: 0.83
Nodes (3): fetch_tmdb_poster(), main(), search_apibay()

### Community 50 - "record_learning.py"
Cohesion: 0.83
Nodes (3): main(), record_new_learning(), slugify()

### Community 54 - "🧭 5 Aturan Emas Spatial Reasoning & DOM Geometry"
Cohesion: 0.20
Nodes (9): 1. Viewport Coordinate Normalization $[0, 1000]$, 2. Recursive Effective Clipping Rect & Visibility Pruning, 3. Z-Index & Stacking Context Occlusion, 4. OCR Token Alignment via Bounding Box Containment & Soft IoU, 🧭 5 Aturan Emas Spatial Reasoning & DOM Geometry, 5. Deterministic Click Action Dispatch, 📌 Domain & Invarian Arsitektur, 🛠️ Implementasi Referensi Stdlib Python: Spatial AST & OCR Grounding (+1 more)

### Community 58 - "Neuron N024: Post-Quantum Cryptography & ML-KEM/ML-DSA (FIPS 203/204)"
Cohesion: 0.22
Nodes (8): 1. Ancaman Kuantum & Paradigma Baru Kriptografi, 2. Arsitektur Standar NIST PQC (FIPS 203 / 204), 3. Fondasi Aljabar Kisi (Lattice-Based Foundations), 4. Imunitas Timing Side-Channel & Disiplin Constant-Time, 5. Pertahanan Berlapis: Hybrid Post-Quantum Key Exchange, 6. Verifikasi Deterministik (Pure Python Stdlib Implementation), 7. Disiplin Integrasi & Operasional Claudia, Neuron N024: Post-Quantum Cryptography & ML-KEM/ML-DSA (FIPS 203/204)

### Community 85 - "🎯 Invarian Inti Perdagangan Kuantitatif (Trading Invariants)"
Cohesion: 0.29
Nodes (6): 1. Manajemen Risiko & Position Sizing (The Golden Law), 2. Logika Pasar Emas (XAU/USD Macro & Microstructure), 3. Logika Pasar Kripto & Smart Money Concepts (SMC), 💻 Algoritma Deterministik (Pure Python Implementation), 🎯 Invarian Inti Perdagangan Kuantitatif (Trading Invariants), N021: Quantitative Gold (XAU/USD) & Crypto Trading Systems

### Community 86 - "Neuron N028: Autonomous System Self-Healing & Distributed Chaos Invariants"
Cohesion: 0.29
Nodes (6): 🎯 1. Automated Node Recovery & Failure Detection, 🔄 2. Level-Triggered State Reconciliation Loop, ⚡ 3. Distributed Chaos Mesh Resilience, 🔒 Disiplin Eksekusi, Neuron N028: Autonomous System Self-Healing & Distributed Chaos Invariants, 💻 Pure Python Runnable Implementation (Stdlib Zero-Dependency)

### Community 87 - "N027_tensor_simd_vectorization.md"
Cohesion: 0.40
Nodes (4): 1. SIMD, Fused Multiply-Add (FMA) & Tensor Core Vectorization, 2. 64-Byte Cache Line Alignment & False Sharing, 3. Roofline Model & L1/L2/L3 Cache Tiling, 4. Invariant Self-Check (Stdlib Python)

## Knowledge Gaps
- **357 isolated node(s):** `__dirname`, `require`, `{ getPonytailInstructions }`, `{ getDefaultMode, normalizePersistedMode }`, `{ parseCommandFile }` (+352 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `__dirname`, `require`, `{ getPonytailInstructions }` to the rest of the system?**
  _357 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ponytail/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05365853658536585 - nodes in this community are weakly interconnected._
- **Should `Install` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Should `MultiHopEngine` be split into smaller, more focused modules?**
  _Cohesion score 0.10153846153846154 - nodes in this community are weakly interconnected._
- **Should `README.es.md` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `Install` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `zolu_learn_server.js` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._