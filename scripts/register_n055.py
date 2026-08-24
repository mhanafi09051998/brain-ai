import json
import os
import datetime

index_file = "learning/NEURON_INDEX.json"
with open(index_file, "r", encoding="utf-8") as f:
    data = json.load(f)

exists = any(n["id"] == "N055" for n in data["neurons"])
if not exists:
    size = os.path.getsize("learning/neurons/N055_graphic_design_generative_visual_engineering.md")
    connections = ["N001", "N003", "N004", "N009", "N017", "N026", "N036", "N051", "N054"]
    entry = {
        "id": "N055",
        "label": "Neuron N055: Graphic Design, Generative Visual Engineering & Vector Math Mastery",
        "file": "N055_graphic_design_generative_visual_engineering.md",
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
else:
    # update size and info
    for n in data["neurons"]:
        if n["id"] == "N055":
            n["size_bytes"] = os.path.getsize("learning/neurons/N055_graphic_design_generative_visual_engineering.md")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("NEURON_INDEX N055 already exists, refreshed size.")

mem_file = "memory.md"
if os.path.exists(mem_file):
    with open(mem_file, "r", encoding="utf-8") as f:
        mem = f.read()
    if "N055_graphic_design_generative_visual_engineering.md" not in mem:
        new_line = "55. **[`N055_graphic_design_generative_visual_engineering.md`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N055_graphic_design_generative_visual_engineering.md)** — **Graphic Design & Generative Visual Engineering**: WCAG 2.2 AAA Contrast, CIELAB/LCh Perceptual Colors, Cubic Bézier Gauss-Legendre Arc Length, 24px Lucide/Penpot Grid SVG Icons & Lissajous Generative Posters.\n"
        if "## 🧠 Active Memory Neurons" in mem:
            parts = mem.split("## 🧠 Active Memory Neurons\n")
            mem = parts[0] + "## 🧠 Active Memory Neurons\n" + new_line + parts[1]
            with open(mem_file, "w", encoding="utf-8") as f:
                f.write(mem)
            print("memory.md updated with N055.")
