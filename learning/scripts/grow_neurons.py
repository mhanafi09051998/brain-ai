"""
Autonomous Neural Growth Engine for Claudia
Harvests learnings, updates synaptic connections, and indexes the neural network.
"""

import os
import json
import glob
from datetime import datetime

LEARNING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEURONS_DIR = os.path.join(LEARNING_DIR, "neurons")
INDEX_PATH = os.path.join(LEARNING_DIR, "NEURON_INDEX.json")


def grow_neural_mesh():
    neurons = []
    neuron_files = sorted(glob.glob(os.path.join(NEURONS_DIR, "*.md")))

    total_synapses = 0
    for fpath in neuron_files:
        fname = os.path.basename(fpath)
        nid = fname.split("_")[0]
        
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        title = fname
        for line in content.splitlines():
            if line.startswith("# "):
                title = line.replace("# ", "").strip()
                break

        # Discover connections by referencing other neuron IDs
        connections = []
        for other_file in neuron_files:
            other_nid = os.path.basename(other_file).split("_")[0]
            if other_nid != nid and other_nid in content:
                connections.append(other_nid)

        total_synapses += len(connections)
        
        neurons.append({
            "id": nid,
            "label": title,
            "file": fname,
            "connections": connections,
            "synapse_count": len(connections),
            "size_bytes": os.path.getsize(fpath)
        })

    index_data = {
        "version": "1.1.0",
        "updated_at": datetime.now().isoformat(),
        "total_neurons": len(neurons),
        "total_synapses": total_synapses,
        "mesh_density": round(total_synapses / max(len(neurons) * (len(neurons) - 1), 1), 3),
        "neurons": neurons
    }

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

    print(f"[Neural Growth] Indexed {len(neurons)} neurons with {total_synapses} active synaptic connections.")
    print(f"[Neural Growth] Mesh Density: {index_data['mesh_density']}")


if __name__ == "__main__":
    grow_neural_mesh()
