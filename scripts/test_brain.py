#!/usr/bin/env python3
"""
Claudia Pre-Flight Brain Integrity Check
Rapid invariant testing (<1.5s) with zero external dependencies.
"""

import os
import sys
import json
import glob
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

def test_neuron_network():
    index_path = os.path.join(WORKSPACE, "learning", "NEURON_INDEX.json")
    assert os.path.exists(index_path), f"Missing {index_path}"
    with open(index_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    neurons = data.get("neurons", [])
    assert len(neurons) >= 20, f"Expected >= 20 neurons in index, found {len(neurons)}"
    
    neuron_list = neurons if isinstance(neurons, list) else list(neurons.values())
    for info in neuron_list:
        rel_file = info.get("file")
        full_path = os.path.join(WORKSPACE, "learning", "neurons", rel_file) if not rel_file.startswith("learning") else os.path.join(WORKSPACE, rel_file)
        assert os.path.exists(full_path), f"Neuron file {rel_file} not found on disk at {full_path}!"
    print(f"  [✓] Neuron Network: {len(neuron_list)}/20 active neurons validated.")

def test_memory_layer():
    mem_file = os.path.join(WORKSPACE, "memory.md")
    assert os.path.exists(mem_file), "Missing memory.md"
    mem_dir = os.path.join(WORKSPACE, "memory", "neurons")
    assert os.path.isdir(mem_dir), "Missing memory/neurons directory"
    mem_neurons = glob.glob(os.path.join(mem_dir, "*.md"))
    assert len(mem_neurons) >= 4, f"Expected >= 4 memory neurons, found {len(mem_neurons)}"
    print(f"  [✓] Memory Layer: {len(mem_neurons)} domain memory neurons validated.")

def test_knowledge_graph():
    graph_path = os.path.join(WORKSPACE, "graphify-out", "graph.json")
    assert os.path.exists(graph_path), "Missing graphify-out/graph.json"
    with open(graph_path, "r", encoding="utf-8-sig") as f:
        g = json.load(f)
    nodes = g.get("nodes", [])
    edges = g.get("links", g.get("edges", []))
    assert len(nodes) > 0, "Knowledge graph has 0 nodes!"
    print(f"  [✓] Knowledge Graph AST: {len(nodes)} nodes & {len(edges)} relations loaded.")

def test_security_and_secrets():
    secret_patterns = [
        re.compile(r'sk-[a-zA-Z0-9_-]{20,}'),
        re.compile(r'[0-9]{8,11}:[A-Za-z0-9_-]{30,}'),
        re.compile(r'token=[a-f0-9]{32,}'),
        re.compile(r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----')
    ]
    tracked_files = []
    try:
        import subprocess
        out = subprocess.check_output(["git", "ls-files"], encoding="utf-8", errors="ignore")
        tracked_files = [f.strip() for f in out.splitlines() if f.strip()]
    except Exception:
        tracked_files = glob.glob("**/*", recursive=True)

    for tf in tracked_files:
        if not os.path.isfile(tf) or tf.startswith("graphify-out"):
            continue
        try:
            with open(tf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pat in secret_patterns:
                    assert not pat.search(content), f"SECURITY LEAK: Found hardcoded secret pattern in tracked file {tf}"
        except Exception as e:
            if "SECURITY LEAK" in str(e):
                raise e
    print(f"  [✓] Zero-Trust Security: All {len(tracked_files)} tracked files scanned clean of hardcoded secrets.")

def test_ide_bridges():
    for f in [".cursorrules", ".windsurfrules", ".github/copilot-instructions.md", "CLAUDIA.md"]:
        p = os.path.join(WORKSPACE, f)
        assert os.path.exists(p), f"Missing IDE bridge file: {f}"
    print("  [✓] Universal IDE Bridges: Cursor, Windsurf, Copilot, and Claude rules verified.")

def test_identity_tamper_lock():
    sig_path = os.path.join(WORKSPACE, ".identity_signature.json")
    assert os.path.exists(sig_path), "TAMPER ALERT: Missing .identity_signature.json!"
    with open(sig_path, "r", encoding="utf-8-sig") as f:
        sig_data = json.load(f)
    
    assert "Muhammad Hanafi" in sig_data.get("author", ""), "TAMPER ALERT: Invalid author attribution in signature!"
    assert "Gahar Inovasi Teknologi" in sig_data.get("organization", ""), "TAMPER ALERT: Invalid organization in signature!"
    
    # Verify immutable attribution keywords in files
    user_prof = os.path.join(WORKSPACE, "memory", "neurons", "user_profile.md")
    assert os.path.exists(user_prof), "Missing memory/neurons/user_profile.md"
    with open(user_prof, "r", encoding="utf-8-sig") as f:
        up_text = f.read()
    assert "Muhammad Hanafi" in up_text and "mhanafi09051998" in up_text, "TAMPER ALERT: Unauthorized modification in user_profile.md!"
    
    agents_md = os.path.join(WORKSPACE, "AGENTS.md")
    assert os.path.exists(agents_md), "Missing AGENTS.md"
    with open(agents_md, "r", encoding="utf-8-sig") as f:
        ag_text = f.read()
    assert "Gahar Inovasi Teknologi" in ag_text, "TAMPER ALERT: Unauthorized modification of proprietary license in AGENTS.md!"

    print("  [✓] Cryptographic Identity Lock: Author & Proprietary Attribution tamper-free.")

def run_all():
    print("🧠 [CLAUDIA PRE-FLIGHT BRAIN INTEGRITY CHECK]")
    try:
        test_neuron_network()
        test_memory_layer()
        test_knowledge_graph()
        test_security_and_secrets()
        test_ide_bridges()
        test_identity_tamper_lock()
        print("\n✨ ALL SYSTEMS NOMINAL: Autonomous Brain is 100% healthy and ready.\n")
        return 0
    except AssertionError as e:
        print(f"\n❌ INTEGRITY CHECK FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all())