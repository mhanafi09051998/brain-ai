import json
import os
import datetime

index_file = "learning/NEURON_INDEX.json"
with open(index_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Ensure N056 is registered properly with rich connections
connections = ["N001", "N004", "N007", "N009", "N010", "N013", "N015", "N028", "N032", "N051", "N053", "N054"]

# Check if N056 is in neurons
found = False
for n in data["neurons"]:
    if n["id"] == "N056":
        n["label"] = "Neuron N056: Strategic SWOT, TOWS Matrix, PESTLE & Porter's 5 Forces Architecture Mastery"
        n["file"] = "N056_strategic_swot_and_tows_matrix_mastery.md"
        n["connections"] = connections
        n["synapse_count"] = len(connections)
        found = True
        break

if not found:
    entry = {
        "id": "N056",
        "label": "Neuron N056: Strategic SWOT, TOWS Matrix, PESTLE & Porter's 5 Forces Architecture Mastery",
        "file": "N056_strategic_swot_and_tows_matrix_mastery.md",
        "connections": connections,
        "synapse_count": len(connections)
    }
    data["neurons"].append(entry)

data["total_neurons"] = len(data["neurons"])
data["total_synapses"] = sum(len(n.get("connections", [])) for n in data["neurons"])
data["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(index_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"[+] NEURON_INDEX updated successfully: {data['total_neurons']} neurons, {data['total_synapses']} synapses.")

# Update memory.md
mem_file = "memory.md"
if os.path.exists(mem_file):
    with open(mem_file, "r", encoding="utf-8") as f:
        mem = f.read()
    if "N056_strategic_swot_and_tows_matrix_mastery.md" not in mem:
        new_line = "56. **[`N056_strategic_swot_and_tows_matrix_mastery.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N056_strategic_swot_and_tows_matrix_mastery.md)** — **Strategic Intelligence & SWOT/TOWS Matrix Mastery**: Quantitative Internal-External Posture Vectors, Mathematical TOWS Cross-Synthesizer, Porter's 5 Forces Risk Scorer & PESTLE Macro-Environment Architecture.\n"
        if "## 🧠 Active Memory Neurons" in mem:
            parts = mem.split("## 🧠 Active Memory Neurons\n")
            mem = parts[0] + "## 🧠 Active Memory Neurons\n" + new_line + parts[1]
            with open(mem_file, "w", encoding="utf-8") as f:
                f.write(mem)
            print("[+] memory.md updated with N056 Master Neuron.")
