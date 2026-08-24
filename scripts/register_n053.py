import json
import os
import datetime

index_file = "learning/NEURON_INDEX.json"
with open(index_file, "r", encoding="utf-8") as f:
    data = json.load(f)

exists = any(n["id"] == "N053" for n in data["neurons"])
if not exists:
    size = os.path.getsize("learning/neurons/N053_quantitative_marketing_growth_mastery.md")
    entry = {
        "id": "N053",
        "label": "Neuron N053: Quantitative Marketing, Growth Science & Causal AdTech Mastery",
        "file": "N053_quantitative_marketing_growth_mastery.md",
        "connections": ["N001", "N004", "N009", "N011", "N017", "N021", "N025", "N033", "N035", "N044", "N050"],
        "synapse_count": 11,
        "size_bytes": size
    }
    data["neurons"].append(entry)
    data["total_neurons"] = len(data["neurons"])
    data["total_synapses"] = sum(len(n.get("connections", [])) for n in data["neurons"])
    data["updated_at"] = datetime.datetime.now().isoformat()
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"NEURON_INDEX updated (Total: {data['total_neurons']} neurons).")

mem_file = "memory.md"
if os.path.exists(mem_file):
    with open(mem_file, "r", encoding="utf-8") as f:
        mem = f.read()
    if "N053_quantitative_marketing_growth_mastery.md" not in mem:
        new_line = "53. **[`N053_quantitative_marketing_growth_mastery.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N053_quantitative_marketing_growth_mastery.md)** — **Quantitative Marketing & AdTech**: Marketing Mix Modeling (Adstock & Hill Saturation), Causal Uplift Modeling, BG/NBD Customer Lifetime Value, Multi-Touch Attribution & Greedy Budget Allocator.\n"
        if "## 🧠 Active Memory Neurons" in mem:
            parts = mem.split("## 🧠 Active Memory Neurons\n")
            mem = parts[0] + "## 🧠 Active Memory Neurons\n" + new_line + parts[1]
            with open(mem_file, "w", encoding="utf-8") as f:
                f.write(mem)
            print("memory.md updated with N053.")
