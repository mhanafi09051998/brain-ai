# Graph Report - Agent_Claudia_Autonomus  (2026-08-24)

## Corpus Check
- 114 files · ~75,893 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 589 nodes · 622 edges · 90 communities (64 shown, 26 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `347ddb2c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- ponytail/package.json
- ponytail-runtime.js
- Install
- README.es.md
- Install
- Production Planning Specification: Zolu AI Web Production Engine
- Ponytail
- Ponytail
- 📦 Daftar Modul & Framework
- Ponytail Help
- Core Engines & Workflows
- Ponytail Help
- Ponytail, lazy senior dev mode
- Ponytail, lazy senior dev mode
- Ponytail, lazy senior dev mode
- N016_frontier_benchmark_evaluator.md
- Ponytail, lazy senior dev mode
- Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia
- Neuron N008: Persistent Live Session Checkpoint & Infrastructure State
- pi-extension/package.json
- ⚡ CLAUDIA 2.0
- MultiHopEngine
- .agents/skills/ponytail-audit/SKILL.md
- Ponytail Gain
- .agents/skills/ponytail-review/SKILL.md
- Core Stack & Architecture
- Neuron N001: Executive Decision Making
- Claudia Neuron Memory Network
- ponytail/skills/ponytail-audit/SKILL.md
- Ponytail Gain
- ponytail/skills/ponytail-review/SKILL.md
- .agents/skills/ponytail-debt/SKILL.md
- Feedback Log
- Neuron N003: Mobile-First UI & Compact Data Viz
- Neuron N004: Ponytail Minimality Ladder
- Neuron N005: Graphify Knowledge Network
- Neuron N006: 9Router Gateway Engine
- Neuron N007: Autonomous Self-Improving Loop
- N009_peak_algorithms_codex.md
- Self-Learning Framework
- ponytail/skills/ponytail-debt/SKILL.md
- /graphify
- Knowledge Base Index
- Neuron N002: VPS Remote Operations & Pipeline
- N010_distributed_systems_design.md
- N011_mechanical_sympathy_perf.md
- N012_deep_search_and_graph_rag.md
- N013_deep_storage_and_distributed_db.md
- N014_zero_trust_security_and_cryptography.md
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
- opencode.json
- parallel_runner.py
- zolu_learn_server.js
- diagnose_browser.js
- test_playwright.js
- ingest_frontier_knowledge.py
- official_runner_real.py
- Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants
- Neuron N018: RepoMap AST Compression & SWE-bench Precision
- Neuron N019: BFCL Tool Schema & IFEval Strict Format Oracle
- verify_ecosystem_playwright.js
- ponytail-config.js
- ponytail-instructions.js
- ponytail.mjs
- ponytail-activate.js

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
10. `⚡ CLAUDIA 2.0` - 9 edges

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

## Communities (90 total, 26 thin omitted)

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

### Community 4 - "README.es.md"
Cohesion: 0.09
Nodes (21): Ponytail, lazy senior dev mode, Antes / después, Antigravity CLI, Claude Code, CodeWhale, Codex, Comandos, Cómo funciona (+13 more)

### Community 5 - "Install"
Cohesion: 0.09
Nodes (21): Antigravity CLI, Before / after, Claude Code, CodeWhale, Codex, Commands, Development, Devin CLI (+13 more)

### Community 6 - "Production Planning Specification: Zolu AI Web Production Engine"
Cohesion: 0.20
Nodes (9): 1.1 Tech Stack Standar, 1. Arsitektur Sistem & Spesifikasi Inti, 2. Aturan Modularity & Maintenance (Max 300 Lines/File), 3. Struktur Direktori Proyek (Modular Layout), 4. Skema Database SQLite (WAL Mode), 5. Integrasi Mesin AI 9Router (`lib/ai/router_client.ts`), 6. Prompting Invariant: Modular Code Decomposition, 7. Tahapan Implementasi & Deployment (+1 more)

### Community 7 - "Ponytail"
Cohesion: 0.22
Nodes (8): Boundaries, Intensity, Output, Persistence, Ponytail, Rules, The ladder, When NOT to be lazy

### Community 8 - "Ponytail"
Cohesion: 0.22
Nodes (8): Boundaries, Intensity, Output, Persistence, Ponytail, Rules, The ladder, When NOT to be lazy

### Community 9 - "📦 Daftar Modul & Framework"
Cohesion: 0.22
Nodes (8): 1. **Biome (`@biomejs/biome`)** - *Linter & Formatter Rust*, 2. **Playwright (`playwright` + Chromium Headless)** - *UI & End-to-End Testing*, 3. **Hono (`hono`)** - *Ultra-Lightweight Edge Web Framework*, 4. **Zod (`zod`)** - *Runtime Schema Validation*, 5. **Drizzle ORM (`drizzle-orm` + `better-sqlite3`)** - *Zero-Bloat Type-Safe Database*, 6. **Puppeteer (`puppeteer`)** - *Headless Chrome Automation*, 📦 Daftar Modul & Framework, 🔒 Standar Keamanan & Vetting

### Community 10 - "Ponytail Help"
Cohesion: 0.25
Nodes (7): Configure Default Mode, Deactivate, Levels, More, Ponytail Help, Skills, Update

### Community 11 - "Core Engines & Workflows"
Cohesion: 0.25
Nodes (7): 1. Ponytail (Lazy Senior Dev Engine), 2. Graphify (Knowledge Graph & Structural Memory), 3. 9Router (AI Gateway & Model Routing), Core Engines & Workflows, Identity: Claudia, Karakter & Gaya Komunikasi, Self-Learning Loop

### Community 12 - "Ponytail Help"
Cohesion: 0.25
Nodes (7): Configure Default Mode, Deactivate, Levels, More, Ponytail Help, Skills, Update

### Community 13 - "Ponytail, lazy senior dev mode"
Cohesion: 0.25
Nodes (7): Graphify & Auto-Sync Knowledge Graph:, ?? Kerahasiaan Arsitektur & Perlindungan Hak Cipta (Proprietary IP Shield):, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder

### Community 14 - "Ponytail, lazy senior dev mode"
Cohesion: 0.29
Nodes (6): Graphify Knowledge Graph:, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder

### Community 15 - "Ponytail, lazy senior dev mode"
Cohesion: 0.25
Nodes (7): Graphify & Auto-Sync Knowledge Graph:, ?? Kerahasiaan Arsitektur & Perlindungan Hak Cipta (Proprietary IP Shield):, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder

### Community 16 - "N016_frontier_benchmark_evaluator.md"
Cohesion: 0.50
Nodes (3): 6 Parameter Tolok Ukur Puncak:, Karakteristik, Lokasi Monitoring Realtime:

### Community 17 - "Ponytail, lazy senior dev mode"
Cohesion: 0.29
Nodes (6): Graphify Knowledge Graph:, Not lazy about:, Persona & Communication, Ponytail, lazy senior dev mode, Rules:, The Minimality Ladder

### Community 18 - "Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia"
Cohesion: 0.33
Nodes (5): 1. Tampilan & Mode, 2. Dropdown & Komponen Formulir, 3. Responsivitas Mobile, 4. Branding & Desain Khusus MojoLoker, Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia

### Community 19 - "Neuron N008: Persistent Live Session Checkpoint & Infrastructure State"
Cohesion: 0.33
Nodes (5): 🚀 Deployed Ecosystem & Port Mappings, 🛠️ Installed Autonomous Fullstack & Security Toolkit, 🎬 Media Engine & Strict Subtitle Cleaner, 📌 Metadata, Neuron N008: Persistent Live Session Checkpoint & Infrastructure State

### Community 20 - "pi-extension/package.json"
Cohesion: 0.33
Nodes (5): name, private, scripts, test, type

### Community 21 - "⚡ CLAUDIA 2.0"
Cohesion: 0.20
Nodes (9): 🌌 1. Filosofi Rekayasa Inti: *The Minimality Ladder*, 🧠 2. Cognitive Neural Mesh (16 Master Neurons), 🧪 3. Framework Tolok Ukur 6 Parameter (Frontier Real Evaluator), 🌐 4. Ekosistem Layanan Aktif (*Production Cluster*), 📊 5. Telemetri VPS & Kecepatan Jaringan Real-Time, 🛠️ 6. Persenjataan & Toolkit Terpasang, 🔒 7. Zero-Trust Security & Vault Isolation, *Autonomous Senior Engineering Partner & Cognitive Neural Mesh* (+1 more)

### Community 22 - "MultiHopEngine"
Cohesion: 0.10
Nodes (14): Local Benchmark Evaluator & Verification Harness for Claudia 2.0 Includes SWE-…, run_evaluation_checks(), MultiHopEngine, Any, Multi-Hop Query Decomposer & GraphRAG Traversal Engine Author: Claudia…, Decomposes complex questions into atomic 1-hop sub-queries., Traverse knowledge graph from start entity up to max_depth hops., Reciprocal Rank Fusion (RRF) combining keyword and graph results. (+6 more)

### Community 23 - ".agents/skills/ponytail-audit/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Hunt, Output, Tags

### Community 24 - "Ponytail Gain"
Cohesion: 0.40
Nodes (4): Boundaries, Honesty boundary, Ponytail Gain, Scoreboard

### Community 25 - ".agents/skills/ponytail-review/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Examples, Format, Scoring

### Community 26 - "Core Stack & Architecture"
Cohesion: 0.40
Nodes (4): 1. Database & Storage, 2. Web & Service Stack, 3. Engineering & Intelligence Engines, Core Stack & Architecture

### Community 27 - "Neuron N001: Executive Decision Making"
Cohesion: 0.40
Nodes (4): Core Concept, Neuron N001: Executive Decision Making, Synaptic Links, Triggers & Heuristics

### Community 28 - "Claudia Neuron Memory Network"
Cohesion: 0.40
Nodes (4): 🧠 Active Memory Neurons, 📋 Active Tasks & History, Claudia Neuron Memory Network, 📋 Prosedur Pembaruan Memori

### Community 29 - "ponytail/skills/ponytail-audit/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Hunt, Output, Tags

### Community 30 - "Ponytail Gain"
Cohesion: 0.40
Nodes (4): Boundaries, Honesty boundary, Ponytail Gain, Scoreboard

### Community 31 - "ponytail/skills/ponytail-review/SKILL.md"
Cohesion: 0.40
Nodes (4): Boundaries, Examples, Format, Scoring

### Community 32 - ".agents/skills/ponytail-debt/SKILL.md"
Cohesion: 0.50
Nodes (3): Boundaries, Output, Scan

### Community 33 - "Feedback Log"
Cohesion: 0.50
Nodes (3): Feedback Log, Log 001 - Inisialisasi Persona, Log 002 - Executive Decision Making (Anti-Pilihan Berlebih)

### Community 34 - "Neuron N003: Mobile-First UI & Compact Data Viz"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N003: Mobile-First UI & Compact Data Viz, Synaptic Links

### Community 35 - "Neuron N004: Ponytail Minimality Ladder"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N004: Ponytail Minimality Ladder, Synaptic Links

### Community 36 - "Neuron N005: Graphify Knowledge Network"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N005: Graphify Knowledge Network, Synaptic Links

### Community 37 - "Neuron N006: 9Router Gateway Engine"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N006: 9Router Gateway Engine, Synaptic Links

### Community 38 - "Neuron N007: Autonomous Self-Improving Loop"
Cohesion: 0.50
Nodes (3): Core Concept, Neuron N007: Autonomous Self-Improving Loop, Synaptic Links

### Community 39 - "N009_peak_algorithms_codex.md"
Cohesion: 0.50
Nodes (3): 1. Graph & Network Flow Algorithms, 2. Probabilistic & Spatial Data Structures, 3. High-Performance Concurrency & Rate Limiting

### Community 40 - "Self-Learning Framework"
Cohesion: 0.50
Nodes (3): Alur Pembelajaran, Self-Learning Framework, Struktur Folder

### Community 41 - "ponytail/skills/ponytail-debt/SKILL.md"
Cohesion: 0.50
Nodes (3): Boundaries, Output, Scan

### Community 73 - "opencode.json"
Cohesion: 0.10
Nodes (21): models, npm, options, modalities, name, agent, explorer, description (+13 more)

### Community 74 - "parallel_runner.py"
Cohesion: 0.53
Nodes (5): eval_single_task(), init_db(), query_llm(), High-Speed Parallel Subagent Benchmark Evaluator for Claudia Features Valid…, run_parallel_subagents_step()

### Community 75 - "zolu_learn_server.js"
Cohesion: 0.13
Nodes (13): app, broadcastState(), clients, cors, { exec }, express, fs, http (+5 more)

### Community 78 - "ingest_frontier_knowledge.py"
Cohesion: 0.67
Nodes (3): build_all_frontier_datasets(), ensure_dirs(), Automated Frontier Dataset Scraper & Knowledge Ingester for Claudia 2.0 Ingests…

### Community 79 - "official_runner_real.py"
Cohesion: 0.27
Nodes (11): compress_ast_context(), eval_single_task(), get_cache_key(), init_db(), query_llm(), Real Production AI Benchmark Evaluator for Claudia (9Router LLM Engine)…, Safely execute Python code generated by LLM, extracting all variables and…, Compress Python code AST removing docstrings and whitespace bloat while… (+3 more)

### Community 80 - "Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants"
Cohesion: 0.50
Nodes (3): 🧮 4 Pilar Heuristik AIME & Olympiad:, 📌 Domain & Karakteristik, Neuron N017: Program-Aided Mathematical Reasoning & AIME Invariants

### Community 81 - "Neuron N018: RepoMap AST Compression & SWE-bench Precision"
Cohesion: 0.50
Nodes (3): 🛠️ 4 Aturan Emas Resolusi SWE-bench:, 📌 Domain & Karakteristik, Neuron N018: RepoMap AST Compression & SWE-bench Precision

### Community 82 - "Neuron N019: BFCL Tool Schema & IFEval Strict Format Oracle"
Cohesion: 0.50
Nodes (3): 📋 4 Aturan Disiplin Eksekusi:, 📌 Domain & Karakteristik, Neuron N019: BFCL Tool Schema & IFEval Strict Format Oracle

### Community 86 - "ponytail-config.js"
Cohesion: 0.14
Nodes (15): fs, getClaudeDir(), getConfigDir(), getConfigPath(), getHideStatus(), getQuietStartup(), normalizeConfigMode(), os (+7 more)

### Community 87 - "ponytail-instructions.js"
Cohesion: 0.18
Nodes (14): normalizeMode(), { DEFAULT_MODE, normalizeMode, normalizePersistedMode }, filterSkillBodyForMode(), fs, getFallbackInstructions(), getPonytailInstructions(), INDEPENDENT_MODES, path (+6 more)

### Community 88 - "ponytail.mjs"
Cohesion: 0.20
Nodes (9): getDefaultMode(), __dirname, parseCommandFile(), { getDefaultMode, normalizePersistedMode }, { getPonytailInstructions }, { parseCommandFile }, readMode(), require (+1 more)

### Community 89 - "ponytail-activate.js"
Cohesion: 0.18
Nodes (10): claudeDir, {
  clearMode,
  isCodex,
  isCopilot,
  setMode,
  writeHookOutput,
}, fs, { getDefaultMode, getClaudeDir, isShellSafe }, { getPonytailInstructions }, mode, output, path (+2 more)

## Knowledge Gaps
- **335 isolated node(s):** `$schema`, `npm`, `baseURL`, `apiKey`, `name` (+330 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `$schema`, `npm`, `baseURL` to the rest of the system?**
  _335 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ponytail/package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05365853658536585 - nodes in this community are weakly interconnected._
- **Should `Install` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Should `README.es.md` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `Install` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `MultiHopEngine` be split into smaller, more focused modules?**
  _Cohesion score 0.10153846153846154 - nodes in this community are weakly interconnected._
- **Should `opencode.json` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._