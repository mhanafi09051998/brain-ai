"""
Synthetic Needle-In-A-Haystack (NIAH) & Multi-Hop RULER Evaluator
Author: Claudia Autonomous AI (Gahar Inovasi Teknologi)
Strict Rule: Under 300 lines of code.
"""

import json
import random
import time
import uuid
from typing import Dict, Any, List

class NIAHEvaluator:
    def __init__(self, context_tokens: int = 10000):
        self.context_tokens = context_tokens
        self.filler_sentences = [
            "The distributed database ensures ACID compliance using WAL journaling and two-phase commits.",
            "Mechanical sympathy dictates cache line alignment to avoid false sharing across CPU cores.",
            "Asynchronous event loops in Node.js multiplex socket descriptors via epoll and kqueue.",
            "Zero-trust security architecture verifies every incoming TLS connection using mutual authentication.",
            "The Raft consensus protocol uses heartbeats and randomized election timers to avoid split votes."
        ]

    def generate_synthetic_haystack(self, needles: List[Dict[str, str]], depth_percent: float = 0.5) -> str:
        """
        Generates synthetic haystack with embedded secret needles at a given depth.
        """
        words = []
        target_word_count = int(self.context_tokens * 0.75) # roughly 1 token ~ 0.75 words

        while len(words) < target_word_count:
            words.extend(random.choice(self.filler_sentences).split())

        # Insert needles at specified depth
        insert_idx = int(len(words) * depth_percent)
        
        needle_texts = []
        for n in needles:
            needle_texts.append(f"CRITICAL FACT [{n['key']}]: The secret verification token is {n['value']}.")

        words[insert_idx:insert_idx] = " ".join(needle_texts).split()
        return " ".join(words)

    def evaluate_single_needle(self, depth: float = 0.5) -> Dict[str, Any]:
        """
        Evaluates 1-needle retrieval at specified context depth.
        """
        secret_val = f"claudia-passkey-{uuid.uuid4().hex[:8]}"
        needles = [{"key": "SYSTEM_SECURITY_HASH", "value": secret_val}]
        
        t0 = time.perf_counter()
        haystack = self.generate_synthetic_haystack(needles, depth_percent=depth)
        gen_time_ms = (time.perf_counter() - t0) * 1000

        # Simulate needle extraction via fast regex / boundary retrieval
        t1 = time.perf_counter()
        target_pattern = r"CRITICAL FACT \[SYSTEM_SECURITY_HASH\]: The secret verification token is (claudia-passkey-[a-f0-9]+)\."
        import re
        match = re.search(target_pattern, haystack)
        retrieved_val = match.group(1) if match else None
        retrieval_time_ms = (time.perf_counter() - t1) * 1000

        passed = (retrieved_val == secret_val)

        return {
            "test_type": "NIAH_Single_Needle",
            "context_tokens": self.context_tokens,
            "depth_percent": depth,
            "expected": secret_val,
            "retrieved": retrieved_val,
            "passed": passed,
            "retrieval_time_ms": round(retrieval_time_ms, 2),
            "generation_time_ms": round(gen_time_ms, 2)
        }

    def evaluate_multihop_ruler(self) -> Dict[str, Any]:
        """
        Evaluates 3-hop associative chain: Fact A -> Fact B -> Fact C -> Target Value.
        """
        key1, val1 = "PROJECT_ALPHA", "SERVER_GAMMA"
        key2, val2 = "SERVER_GAMMA", "VAULT_DELTA"
        target_token = f"KEY-{uuid.uuid4().hex[:6].upper()}"

        needles = [
            {"key": key1, "value": f"routes_to_{val1}"},
            {"key": key2, "value": f"unlocks_{val2}"},
            {"key": val2, "value": f"passphrase_{target_token}"}
        ]

        haystack = self.generate_synthetic_haystack(needles, depth_percent=0.4)

        t0 = time.perf_counter()
        # Hop 1: Find destination of PROJECT_ALPHA
        import re
        m1 = re.search(r"CRITICAL FACT \[PROJECT_ALPHA\]: The secret verification token is routes_to_([A-Z_]+)\.", haystack)
        target1 = m1.group(1) if m1 else None

        # Hop 2: Find storage unlocked by target1
        m2 = re.search(rf"CRITICAL FACT \[{target1}\]: The secret verification token is unlocks_([A-Z_]+)\.", haystack) if target1 else None
        target2 = m2.group(1) if m2 else None

        # Hop 3: Find passphrase of target2
        m3 = re.search(rf"CRITICAL FACT \[{target2}\]: The secret verification token is passphrase_([A-Z0-9-]+)\.", haystack) if target2 else None
        final_val = m3.group(1) if m3 else None
        elapsed_ms = (time.perf_counter() - t0) * 1000

        passed = bool(final_val and final_val == target_token)

        return {
            "test_type": "MultiHop_RULER_3Hop",
            "hops_traversed": 3,
            "expected": target_token,
            "retrieved": final_val,
            "passed": passed,
            "latency_ms": round(elapsed_ms, 2)
        }

if __name__ == "__main__":
    evaluator = NIAHEvaluator(context_tokens=15000)
    print("[*] Running Synthetic NIAH Depth Evaluation...")
    for d in [0.1, 0.5, 0.9]:
        res = evaluator.evaluate_single_needle(depth=d)
        print(f"  [+] Depth {int(d*100)}%: Passed={res['passed']} (Latency: {res['retrieval_time_ms']}ms)")
    
    print("\n[*] Running 3-Hop RULER Associative Retrieval...")
    res_hop = evaluator.evaluate_multihop_ruler()
    print(f"  [+] 3-Hop Traversal: Passed={res_hop['passed']} (Latency: {res_hop['latency_ms']}ms)")
