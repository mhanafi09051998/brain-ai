import json
import os
import datetime

index_file = "learning/NEURON_INDEX.json"
with open(index_file, "r", encoding="utf-8") as f:
    data = json.load(f)

exists = any(n["id"] == "N054" for n in data["neurons"])
if not exists:
    size = os.path.getsize("learning/neurons/N054_system_design_planning_mastery.md")
    connections = ["N001", "N004", "N009", "N010", "N013", "N015", "N028", "N032", "N051"]
    entry = {
        "id": "N054",
        "label": "Neuron N054: Large-Scale System Design, Architecture Planning & Contract-First Engineering Mastery",
        "file": "N054_system_design_planning_mastery.md",
        "connections": connections,
        "synapse_count": len(connections),
        "size_bytes": size
    }
    data["neurons"].append(entry)
    data["total_neurons"] = len(data["neurons"])
    data["total_synapses"] = sum(len(n.get("connections", [])) for n in data["neurons"])
    data["updated_at"] = datetime.datetime.now().isoformat()
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"NEURON_INDEX updated (Total: {data['total_neurons']} neurons, Synapses: {data['total_synapses']}).")

mem_file = "memory.md"
if os.path.exists(mem_file):
    with open(mem_file, "r", encoding="utf-8") as f:
        mem = f.read()
    if "N054_system_design_planning_mastery.md" not in mem:
        new_line = "54. **[`N054_system_design_planning_mastery.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N054_system_design_planning_mastery.md)** — **Large-Scale System Design & Architecture Planning**: Capacity & Bandwidth Estimator, CAP/PACELC Trade-offs, Consistent Hashing Ring (vnodes), Automated ADR Lifecycle (MADR/Nygard), Contract-First OpenAPI 3.1 & C4 Architecture-as-Code.\n"
        if "## 🧠 Active Memory Neurons" in mem:
            parts = mem.split("## 🧠 Active Memory Neurons\n")
            mem = parts[0] + "## 🧠 Active Memory Neurons\n" + new_line + parts[1]
            with open(mem_file, "w", encoding="utf-8") as f:
                f.write(mem)
            print("memory.md updated with N054.")
