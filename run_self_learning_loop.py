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

print("🧠 [CLAUDIA AUTONOMOUS SELF-LEARNING ENGINE: ALGORITHMS & CODING]")
print("================================================================")

now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

new_learnings = [
    {
        "id": "N060",
        "title": "Advanced Algorithmic Mastery & Dynamic Graph Automata",
        "category": "Algorithms & Competitive Programming",
        "file": "N060_advanced_algorithmic_mastery.md",
        "invariant": """1. Tree DP with $O(N)$ Rerooting: Hitung agregasi pohon secara global dalam 2 kali DFS traversal (DFS 1: bottom-up subtree DP, DFS 2: top-down parent contribution broadcast) tanpa re-kalkulasi $O(N^2)$.
2. 2D Range Point-Update & Range-Query via Fenwick Tree (BIT): Reduksi memori dari 2D Segment Tree $O(N^2 \\log^2 N)$ ke 2D Binary Indexed Tree $O(N^2)$ dengan operasi bitwise `i += i & (-i)` dan `i -= i & (-i)`.
3. Li Chao Segment Tree (Dynamic Convex Hull Trick): Optimasi DP linear $O(N^2) \\to O(N \\log C)$ untuk evaluasi persamaan garis dinamis $y = mx + c$ tanpa syarat gradien terurut monotonik.
4. Strongly Connected Components (Tarjan $O(V+E)$): Traversal DFS tunggal menggunakan `lowlink` dan `dfn` stack untuk identifikasi directed cycles & condensation DAG.
5. Invariant Eksekusi: Hindari rekursi dalam yang memicu stack overflow; ubah ke iterasi eksplisit dengan bounded stack pada input $N \\ge 10^5$.""",
        "root_cause": "Pemecahan masalah graf berskala besar sering kali mengalami TLE karena rekursi unoptimized atau komputasi berulang. Ditetapkan invarian Tree Rerooting dan Li Chao Tree sebagai standar reduksi kompleksitas waktu linear-logaritmik."
    },
    {
        "id": "N061",
        "title": "Lock-Free Concurrency, Memory Barriers & Cache-Oblivious Architecture",
        "category": "Systems & Concurrency Engineering",
        "file": "N061_lock_free_concurrency_and_cache.md",
        "invariant": """1. SPSC & MPMC Lock-Free Ring Buffer: Terapkan memory ordering `std::memory_order_release` pada producer dan `std::memory_order_acquire` pada consumer untuk menjamin visibilitas data tanpa mutex overhead.
2. Pencegahan False Sharing: Seluruh atomic head/tail pointers wajib dialokasikan dengan 64-byte / 128-byte cache line alignment (`alignas(64)` / `#[repr(align(64))]`) untuk mencegah bus contention antar core CPU.
3. ABA Prevention: Solusikan masalah ABA pada Lock-Free Stack/Queue menggunakan Tagged Pointers (Pointer + 64-bit Monotonic Version Counter) atau Epoch-Based Memory Reclamation (EBR).
4. Arena Allocator & Cache-Oblivious Matrix Transposition: Alokasikan memori secara contiguous (SoA - Structure of Arrays) untuk memaksimalkan L1/L2 prefetcher throughput dan meminimalkan TLB misses.""",
        "root_cause": "Contention tinggi pada multithreaded systems sering kali disebabkan oleh false sharing pada atomic shared variables dan lock overhead. Dipecahkan dengan alignment cache-line eksplisit dan memory order release/acquire."
    },
    {
        "id": "N062",
        "title": "Distributed Consensus Invariants, Log Compaction & Idempotent SAGA",
        "category": "Distributed Systems & Reliability",
        "file": "N062_distributed_consensus_and_saga.md",
        "invariant": """1. Raft Term Monotonicity & Leader Election: Setiap RPC term harus strict monotonic; node yang menerima term lebih tinggi wajib langsung revert ke Follower state dan mengupdate local term.
2. Fencing Tokens & Split-Brain Immunity: Distribusi lock wajib menyertakan monotonic fencing token di storage layer agar mutasi dari mantan leader (zombie process) ditolak otomatis.
3. Snapshot Log Compaction: Segment log di-truncate hanya setelah snapshot state disk telah ter-fsync permanen untuk mencegah data loss saat sudden power failure.
4. Idempotent SAGA Compensation Flow: Setiap langkah transaksi terdistribusi wajib memiliki UUID Idempotency-Key dan kompensasi rollback deterministik yang aman dipanggil berulang kali (*idempotent replay*).""",
        "root_cause": "Inkonsistensi data transaksi terdistribusi kerap terjadi saat network partition dan dual-primary election. Dipecahkan dengan aturan fencing token di database layer dan replay kompensasi SAGA berbasis idempotency key."
    }
]

# 1. Update/Add Neurons
index_path = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")
with open(index_path, "r", encoding="utf-8-sig") as f:
    index_data = json.load(f)

neurons = index_data.get("neurons", [])
existing_ids = {n["id"] for n in neurons}

mem_file = os.path.join(WORKSPACE, "memory.md")
with open(mem_file, "r", encoding="utf-8") as f:
    mem_text = f.read()

for item in new_learnings:
    n_id = item["id"]
    n_file = item["file"]
    n_path = os.path.join(WORKSPACE, "learning", "neurons", n_file)
    
    # Write Neuron Markdown
    md_body = f"""# {n_id}: {item['title']}

- **Kategori:** {item['category']}
- **Tanggal Sintesis:** {now_iso}
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
{item['invariant']}

## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)
{item['root_cause']}

---
## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
"""
    with open(n_path, "w", encoding="utf-8") as f:
        f.write(md_body)
    print(f"  [✓] Neuron disintesis: learning/neurons/{n_file}")
    
    # Update Index
    if n_id not in existing_ids:
        neurons.append({
            "id": n_id,
            "label": f"Neuron {n_id}: {item['title']}",
            "file": n_file,
            "connections": ["N001", "N004", "N009", "N011"]
        })
        existing_ids.add(n_id)
        
        # Add to memory.md
        new_entry = f"{len(neurons)}. **[`{n_file}`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/{n_file})** — **{item['title']}**: {item['invariant'][:80]}...\n"
        if "## 🧠 Active Memory Neurons" in mem_text:
            parts = mem_text.split("## 🧠 Active Memory Neurons\n")
            mem_text = parts[0] + "## 🧠 Active Memory Neurons\n" + new_entry + parts[1]

index_data["neurons"] = neurons
index_data["total_neurons"] = len(neurons)
index_data["total_synapses"] = index_data.get("total_synapses", 227) + (len(new_learnings) * 4)
index_data["updated_at"] = now_iso

with open(index_path, "w", encoding="utf-8") as f:
    json.dump(index_data, f, indent=2, ensure_ascii=False)

with open(mem_file, "w", encoding="utf-8") as f:
    f.write(mem_text)

print(f"\n[✓] Total Active Neurons upgraded: {len(neurons)} Master Neurons.")

# 2. Run Pre-Flight Brain Integrity Check
print("\n[*] Menjalankan verifikasi mandiri integritas otak...")
res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "test_brain.py")], capture_output=True, text=True)
print(res.stdout.strip())
if res.returncode != 0:
    print("[!] Gagal verifikasi:", res.stderr.strip())
    sys.exit(1)

# 3. Auto-Sync to GitHub
print("\n[*] Menyinkronkan dan mem-push kecerdasan baru ke GitHub...")
sync_res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "auto_sync_github.py")], capture_output=True, text=True)
print(sync_res.stdout.strip())

print("\n✨ Self-Learning Loop Complete: Advanced Algorithms & Coding Mastery Synthesized & Pushed to GitHub!")
