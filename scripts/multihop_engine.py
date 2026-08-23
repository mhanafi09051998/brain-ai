"""
Multi-Hop Query Decomposer & GraphRAG Traversal Engine
Author: Claudia Autonomous AI (Gahar Inovasi Teknologi)
Strict Rule: Under 300 lines of code.
"""

import json
import re
from typing import List, Dict, Any, Set

class MultiHopEngine:
    def __init__(self, graph_path: str = "graphify-out/graph.json"):
        self.graph_path = graph_path
        self.nodes = {}
        self.edges = []
        self.adjacency = {}
        self._load_graph()

    def _load_graph(self):
        try:
            with open(self.graph_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                nodes_list = data.get("nodes", [])
                for n in nodes_list:
                    nid = n.get("id") or n.get("name")
                    if nid:
                        self.nodes[nid] = n
                        self.adjacency[nid] = set()
                
                self.edges = data.get("links", []) or data.get("edges", [])
                for e in self.edges:
                    src = e.get("source")
                    tgt = e.get("target")
                    if src in self.adjacency and tgt in self.adjacency:
                        self.adjacency[src].add(tgt)
        except Exception:
            self.nodes = {}
            self.adjacency = {}

    def decompose_query(self, query: str) -> List[str]:
        """
        Decomposes complex questions into atomic 1-hop sub-queries.
        """
        q = query.strip()
        # Look for conjunctions or multi-entity references
        if re.search(r'\b(and|lalu|kemudian|setelah|dan|serta|terhubung ke)\b', q, re.IGNORECASE):
            parts = re.split(r'\b(?:and|lalu|kemudian|setelah|dan|serta)\b', q, flags=re.IGNORECASE)
            sub_queries = [p.strip() for p in parts if len(p.strip()) > 3]
            if len(sub_queries) > 1:
                return sub_queries
        return [q]

    def traverse_multihop(self, start_entity: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Traverse knowledge graph from start entity up to max_depth hops.
        """
        if start_entity not in self.adjacency:
            # Fuzzy entity match
            matches = [k for k in self.adjacency if start_entity.lower() in k.lower()]
            if matches:
                start_entity = matches[0]
            else:
                return []

        visited: Set[str] = set([start_entity])
        queue = [(start_entity, 0, [start_entity])]
        hop_results = []

        while queue:
            curr, depth, path = queue.pop(0)
            node_data = self.nodes.get(curr, {})
            hop_results.append({
                "entity": curr,
                "depth": depth,
                "path": path,
                "label": node_data.get("label", curr)
            })

            if depth < max_depth:
                for neighbor in self.adjacency.get(curr, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1, path + [neighbor]))

        return hop_results

    def hybrid_rank_fuse(self, keyword_results: List[str], graph_results: List[str], k: int = 60) -> List[str]:
        """
        Reciprocal Rank Fusion (RRF) combining keyword and graph results.
        """
        rrf_scores = {}
        for rank, doc in enumerate(keyword_results):
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + (1.0 / (k + rank + 1))
        for rank, doc in enumerate(graph_results):
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + (1.0 / (k + rank + 1))

        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in sorted_docs]

if __name__ == "__main__":
    engine = MultiHopEngine()
    test_q = "Cari hubungan antara N009 dan N016 lalu verifikasi fungsinya"
    sub_qs = engine.decompose_query(test_q)
    print(f"[*] Original Query: {test_q}")
    print(f"[*] Sub-queries ({len(sub_qs)}): {sub_qs}")
    hops = engine.traverse_multihop("N009", max_depth=2)
    print(f"[*] Multi-Hop Traversal (N009): {len(hops)} connected nodes found.")
    for h in hops[:5]:
        print(f"    - Depth {h['depth']}: {' -> '.join(h['path'])}")
