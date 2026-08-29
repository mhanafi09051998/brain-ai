#!/usr/bin/env python3
"""
Claudia Autonomous Continuous Learning & Self-Improving Feedback Loop
Synthesizes newly discovered engineering invariants directly into neuron files,
registers them into NEURON_INDEX.json, updates Graphify AST, tests integrity,
and auto-syncs the new brain state to GitHub & VPS in real-time.
"""

import os
import sys
import json
import argparse
import datetime
import re
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '_', text)[:32]

def record_new_learning(topic: str, category: str, invariant: str, root_cause: str = ""):
    print(f"[*] Menginisialisasi sintesis neuron pembelajaran baru: '{topic}'...")
    
    index_path = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")
    with open(index_path, "r", encoding="utf-8-sig") as f:
        index_data = json.load(f)
    
    neurons = index_data.get("neurons", [])
    next_num = len(neurons) + 1
    neuron_id = f"N{next_num:03d}"
    slug = slugify(topic)
    file_name = f"{neuron_id}_{slug}.md"
    neuron_path = os.path.join(WORKSPACE, "learning", "neurons", file_name)
    
    now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Tulis konten neuron baru
    md_content = f"""# {neuron_id}: {topic}

- **Kategori:** {category}
- **Tanggal Sintesis:** {now_iso}
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
{invariant}

"""
    if root_cause:
        md_content += f"""## 🔍 Akar Masalah & Pencegahan Regresi (Root Cause Analysis)
{root_cause}

---
"""

    md_content += f"""## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
"""

    with open(neuron_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  [✓] File neuron berhasil dibuat: learning/neurons/{file_name}")

    # 2. Update NEURON_INDEX.json
    new_entry = {
        "id": neuron_id,
        "label": f"Neuron {neuron_id}: {topic}",
        "file": file_name,
        "connections": ["N001", "N004", "N007"]
    }
    neurons.append(new_entry)
    index_data["neurons"] = neurons
    index_data["total_neurons"] = len(neurons)
    index_data["total_synapses"] = index_data.get("total_synapses", 60) + 3
    index_data["updated_at"] = now_iso
    
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    print(f"  [✓] Index neuron diperbarui (Total: {len(neurons)} neuron aktif).")

    # 3. Update memory.md jika belum tercantum
    mem_file = os.path.join(WORKSPACE, "memory.md")
    if os.path.exists(mem_file):
        with open(mem_file, "r", encoding="utf-8") as f:
            mem_text = f.read()
        if file_name not in mem_text:
            ws_uri = WORKSPACE.replace('\\', '/')
            new_item = f"{len(neurons)}. **[`{file_name}`](file:///{ws_uri}/learning/neurons/{file_name})** — **{topic}**: {invariant[:80]}...\n"
            if "## 🧠 Active Memory Neurons" in mem_text:
                parts = mem_text.split("## 🧠 Active Memory Neurons\n")
                updated_mem = parts[0] + "## 🧠 Active Memory Neurons\n" + new_item + parts[1]
                with open(mem_file, "w", encoding="utf-8") as f:
                    f.write(updated_mem)
                print(f"  [✓] memory.md disinkronkan.")

    # 4. Validasi Pre-Flight Brain Integrity Check
    print("[*] Menjalankan validasi mandiri integritas otak...")
    res = subprocess.run([sys.executable, os.path.join(WORKSPACE, "scripts", "test_brain.py")], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Peringatan integritas: {res.stdout.strip()} {res.stderr.strip()}")
    else:
        print("  [✓] Validasi pre-flight berhasil (100% nominal).")

    # 5. Sinkronisasi Otomatis ke GitHub & VPS
    print("[*] Melakukan sinkronisasi otomatis ke GitHub & VPS...")
    sync_script = os.path.join(WORKSPACE, "scripts", "auto_sync_github.py")
    if os.path.exists(sync_script):
        subprocess.run([sys.executable, sync_script])

    print(f"\n✨ Selesai. Pembelajaran '{topic}' ({neuron_id}) telah menjadi bagian permanen dari otak online Claudia.\n")

def main():
    parser = argparse.ArgumentParser(description="Catat pembelajaran baru ke dalam Neuron Network Claudia.")
    parser.add_argument("--topic", required=True, help="Judul topik pembelajaran (misal: 'WebSocket Auto Reconnect')")
    parser.add_argument("--category", default="Architecture", help="Kategori domain (misal: UI, Infra, Security, Algoritma)")
    parser.add_argument("--invariant", required=True, help="Aturan inti / invarian yang dipelajari")
    parser.add_argument("--root-cause", default="", help="Penyebab akar masalah atau pelajaran dari bug sebelumnya")
    
    args = parser.parse_args()
    record_new_learning(args.topic, args.category, args.invariant, args.root_cause)

if __name__ == "__main__":
    main()