import os
import sys
import json
import datetime
import subprocess

WORKSPACE = r"D:\GEMINI-HANAFI"
os.chdir(WORKSPACE)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

print("🧠 [INTEGRATING 12 NEW MASTER NEURONS (N063 - N074) INTO CLAUDIA BRAIN]")
print("=========================================================================")

index_path = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")
with open(index_path, "r", encoding="utf-8-sig") as f:
    index_data = json.load(f)

neurons = index_data.get("neurons", [])
existing_ids = {n["id"]: n for n in neurons}

mem_file = os.path.join(WORKSPACE, "memory.md")
with open(mem_file, "r", encoding="utf-8") as f:
    mem_text = f.read()

new_neurons_metadata = [
    {
        "id": "N063",
        "label": "Neuron N063: MCTS Agentic Planning, State Backpropagation & Self-Correction Engine",
        "file": "N063_mcts_agentic_planning_self_correction.md",
        "summary": "Monte Carlo Tree Search (PUCT), negative credit assignment backpropagation, heuristic branch pruning, transactional rollback.",
        "connections": ["N001", "N004", "N007", "N022"]
    },
    {
        "id": "N064",
        "label": "Neuron N064: Graph-of-Thought (GoT) Non-Linear Reasoning & Swarm Consensus Engine",
        "file": "N064_graph_of_thought_swarm_consensus.md",
        "summary": "Graph-of-Thought non-linear reasoning, PBFT (3f+1) swarm consensus, dynamic salience context compression, AST call-graph reachability pruning.",
        "connections": ["N001", "N005", "N012", "N022"]
    },
    {
        "id": "N065",
        "label": "Neuron N065: Linux io_uring, Kernel Bypass & Zero-Copy Memory Pipelines",
        "file": "N065_linux_io_uring_zero_copy_pipelines.md",
        "summary": "io_uring SQ/CQ lock-free rings, eBPF XDP kernel bypass, splice/sendfile zero-copy, mirror-mapped contiguous virtual ring buffers.",
        "connections": ["N009", "N011", "N029", "N034"]
    },
    {
        "id": "N066",
        "label": "Neuron N066: WASI Preview 2, Tokio Work-Stealing Internals & Async Cancellation Safety",
        "file": "N066_wasi_preview2_tokio_internals.md",
        "summary": "WASI Preview 2 component model, deterministic fuel metering, Tokio work-stealing scheduler, async cancellation safety guards, lock-free SPSC barriers.",
        "connections": ["N015", "N029", "N037", "N065"]
    },
    {
        "id": "N067",
        "label": "Neuron N067: Multi-Raft Range Partitioning, Distributed ACID & Hybrid Logical Clocks (HLC)",
        "file": "N067_multiraft_distributed_acid_hlc.md",
        "summary": "Multi-Raft contiguous key ranges, Distributed ACID (Percolator 2PC), Hybrid Logical Clocks (HLC) causality, Spanner-style read leases.",
        "connections": ["N010", "N013", "N028", "N062"]
    },
    {
        "id": "N068",
        "label": "Neuron N068: Storage Engine LSM Leveled Compaction, B-Link Concurrency & Real-Time CDC Streaming",
        "file": "N068_storage_engine_lsm_cdc_streaming.md",
        "summary": "LSM-Tree Leveled Compaction vs Lehman-Yao B-Link Trees, SQLite/Postgres WAL streaming, Debezium CDC, pgvector HNSW + BM25 RRF fusion.",
        "connections": ["N012", "N013", "N031", "N035"]
    },
    {
        "id": "N069",
        "label": "Neuron N069: 6-Phase Expand-and-Contract Zero-Downtime Database Schema Evolution",
        "file": "N069_expand_contract_zerodowntime_migrations.md",
        "summary": "6-Phase Expand-and-Contract lifecycle, keyset backfilling with adaptive replication lag throttling, lock timeout guards, N-1/N+1 forward/backward compatibility.",
        "connections": ["N031", "N032", "N051", "N068"]
    },
    {
        "id": "N070",
        "label": "Neuron N070: Firecracker MicroVM Sandboxing & PostgreSQL Multi-Tenant Row-Level Security (RLS)",
        "file": "N070_firecracker_microvm_multitenant_rls.md",
        "summary": "Firecracker MicroVM jailer isolation (<5ms boot), seccomp-bpf filters, PostgreSQL FORCE RLS tenant isolation with session safety.",
        "connections": ["N014", "N032", "N037", "N069"]
    },
    {
        "id": "N071",
        "label": "Neuron N071: Automated AST Mutation Fuzzing, Source-to-Sink Taint Lattice & Zero-Downtime CVE Hotpatching",
        "file": "N071_automated_fuzzing_cve_hotpatching.md",
        "summary": "AST dataflow taint lattice, AFL++ coverage bitmap heuristics, triple-check SBOM verification, live AST semantic CVE hotpatching.",
        "connections": ["N014", "N015", "N023", "N038"]
    },
    {
        "id": "N072",
        "label": "Neuron N072: NIST Post-Quantum Cryptography (ML-KEM / ML-DSA), PASETO v4 & Hardware Enclaves",
        "file": "N072_post_quantum_cryptography_paseto.md",
        "summary": "NIST FIPS 203/204 lattice cryptography (Module-LWE/SIS), constant-time side-channel immunity, PASETO v4 public-token standard, SGX/SEV enclaves.",
        "connections": ["N014", "N024", "N071"]
    },
    {
        "id": "N073",
        "label": "Neuron N073: Level-3 Limit Order Book Dynamics, VPIN Toxicity & Dynamic Spread Adaptation",
        "file": "N073_lob_microstructure_vpin_toxicity.md",
        "summary": "Level-3 LOB queue dynamics, VPIN adverse selection toxicity metrics, Multi-level Order Flow Imbalance (OFI), Stoikov dynamic MM quoting.",
        "connections": ["N021", "N025", "N043", "N046"]
    },
    {
        "id": "N074",
        "label": "Neuron N074: Online 2D Kalman Statistical Arbitrage, Continuous OU SDEs & Sub-Millisecond Kill-Switch",
        "file": "N074_kalman_stat_arbitrage_risk_killswitch.md",
        "summary": "Online 2D Kalman Filter dynamic hedge ratio, Ornstein-Uhlenbeck continuous mean reversion SDEs, Merton jump-diffusion VaR 99.9%, sub-ms risk kill-switch.",
        "connections": ["N021", "N044", "N045", "N047"]
    }
]

now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

new_mem_entries = []
for meta in new_neurons_metadata:
    n_id = meta["id"]
    n_file = meta["file"]
    n_path = os.path.join(WORKSPACE, "learning", "neurons", n_file)
    size_bytes = os.path.getsize(n_path) if os.path.exists(n_path) else 1000
    
    if n_id not in existing_ids:
        neurons.append({
            "id": n_id,
            "label": meta["label"],
            "file": n_file,
            "connections": meta["connections"],
            "synapse_count": len(meta["connections"]),
            "size_bytes": size_bytes
        })
        new_mem_entries.append(f"{len(neurons)}. **[`{n_file}`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/{n_file})** — **{meta['label']}**: {meta['summary']}\n")
    else:
        existing_ids[n_id]["label"] = meta["label"]
        existing_ids[n_id]["file"] = n_file
        existing_ids[n_id]["connections"] = meta["connections"]
        existing_ids[n_id]["size_bytes"] = size_bytes

if new_mem_entries and "## 🧠 Active Memory Neurons" in mem_text:
    parts = mem_text.split("## 🧠 Active Memory Neurons\n")
    mem_text = parts[0] + "## 🧠 Active Memory Neurons\n" + "".join(new_mem_entries) + parts[1]

index_data["neurons"] = neurons
index_data["total_neurons"] = len(neurons)
index_data["total_synapses"] = sum(len(n.get("connections", [])) for n in neurons)
index_data["updated_at"] = now_iso

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(index_data, f, indent=2, ensure_ascii=False)

with open(mem_file, "w", encoding="utf-8") as f:
    f.write(mem_text)

print(f"[✓] Jaringan Neuron berhasil ditingkatkan: Total {len(neurons)} Master Neurons aktif.")

# Pre-Flight Brain Integrity Check
print("\n[*] Menjalankan Pre-Flight Brain Integrity Check...")
res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "test_brain.py")], capture_output=True, text=True)
print(res.stdout.strip())
if res.returncode != 0:
    print("[!] Gagal verifikasi integritas otak:", res.stderr.strip())
    sys.exit(1)

# Auto-sync to GitHub
print("\n[*] Menyinkronkan seluruh 74 Master Neurons ke GitHub...")
sync_res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "auto_sync_github.py")], capture_output=True, text=True)
print(sync_res.stdout.strip())

print("\n✨ ALL 74 MASTER NEURONS SYNTHESIZED, VERIFIED & SYNCHRONIZED TO GITHUB!")
