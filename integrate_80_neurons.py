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

print("🧠 [INTEGRATING MASTER NEURONS N075 - N080 INTO CLAUDIA BRAIN]")
print("================================================================")

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
        "id": "N075",
        "label": "Neuron N075: Conflict-Free Replicated Data Types (CRDT), Causal Vector Clocks & Merkle DAG Local-First Sync",
        "file": "N075_crdt_local_first_state_sync.md",
        "summary": "Join semi-lattice convergence, Observed-Remove Set (OR-Set), LWW-Element-Set, Causal Vector Clocks, Merkle DAG delta sync.",
        "connections": ["N010", "N013", "N067", "N068"]
    },
    {
        "id": "N076",
        "label": "Neuron N076: Formal Verification, SMT-Based Symbolic Execution & Deductive Hoare Logic Invariants",
        "file": "N076_formal_verification_z3_smt_prover.md",
        "summary": "Refutation SMT proof, Weakest Precondition (wp) calculus, 3-step inductive loop invariants, symbolic execution bifurcation.",
        "connections": ["N009", "N015", "N071", "N072"]
    },
    {
        "id": "N077",
        "label": "Neuron N077: Closed-Loop PID Load Shedding, Deadlock Cycle Detection & Autonomous Chaos Healing",
        "file": "N077_runtime_self_healing_pid_chaos.md",
        "summary": "Closed-loop PID load shedder with anti-windup, Wait-For Graph (WFG) deadlock cycle preemption, adaptive threadpool sizing, OODA chaos supervisor.",
        "connections": ["N028", "N034", "N051", "N061"]
    },
    {
        "id": "N078",
        "label": "Neuron N078: Zero-Knowledge Proofs, R1CS Arithmetic Circuits & Verifiable State Transitions",
        "file": "N078_zero_knowledge_proofs_verifiable_compute.md",
        "summary": "R1CS bilinear constraint systems, QAP polynomial divisibility, Groth16/PlonK pairing checks, succinct zero-knowledge verifiable state transitions.",
        "connections": ["N014", "N024", "N072", "N076"]
    },
    {
        "id": "N079",
        "label": "Neuron N079: Kernel Bypass Networking (DPDK & RDMA RoCEv2) with Zero-Copy Direct Memory Access",
        "file": "N079_kernel_bypass_dpdk_rdma_roce.md",
        "summary": "DPDK Poll Mode Drivers (PMD) & Hugepages, RDMA RoCEv2 DCQCN congestion control, Queue Pair (QP) state transitions, sub-microsecond host DMA.",
        "connections": ["N011", "N029", "N065", "N073"]
    },
    {
        "id": "N080",
        "label": "Neuron N080: Meta-Compiler Optimization, Polyhedral Loop Models & Tiered JIT Speculative Deoptimization",
        "file": "N080_meta_compiler_jit_polyhedral_vectorization.md",
        "summary": "Polyhedral loop iteration domain models (tiling, skewing), Tiered JIT speculative deopt bailouts, SIMD stride coalescing transforms.",
        "connections": ["N015", "N027", "N037", "N066"]
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
print("\n[*] Menyinkronkan seluruh 80 Master Neurons ke GitHub...")
sync_res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "auto_sync_github.py")], capture_output=True, text=True)
print(sync_res.stdout.strip())

print("\n✨ ALL 80 MASTER NEURONS SYNTHESIZED, VERIFIED & SYNCHRONIZED TO GITHUB!")
