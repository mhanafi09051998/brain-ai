---
name: algorithms
description: High-precision guide and reference for battle-tested algorithmic design patterns, data structures, and optimal time-space complexity invariants.
---

# Algorithmic Mastery & Optimal Patterns

When designing or optimizing algorithms, identify the underlying invariant before writing code. Always minimize time and space complexity.

---

## 1. Algorithmic Decision Framework

| Input Constraints ($) | Target Time Complexity | Typical Applicable Approaches |
| :--- | :--- | :--- |
|  \le 10$ | (N!)$ or (2^N \cdot N)$ | Bitmask DP, Permutation Backtracking |
|  \le 20$ | (2^N)$ | Subset Generation, Meet-in-the-Middle |
|  \le 500$ | (N^3)$ | Floyd-Warshall, Matrix Multiplication, 3D DP |
|  \le 5,000$ | (N^2)$ | Dynamic Programming, Two Pointers, Greedy |
|  \le 2 \times 10^5$ | (N \log N)$ or (N)$ | Binary Search on Answer, Monotonic Stack/Queue, Heap, Segment Tree, Sliding Window |
|  \ge 10^9$ | (\log N)$ or (1)$ | Mathematical closed-form, Matrix Exponentiation, Binary Exponentiation |

---

## 2. Core Algorithmic Paradigms

### A. Monotonic Stack & Queue
* **Pattern**: Finding next/previous greater or smaller element, or maintaining min/max in a sliding window.
* **Invariant**: Maintain strictly increasing/decreasing indices or values in the deque/stack.
* **Complexity**: (N)$ amortized time, (N)$ space.

### B. Binary Search on Monotonic Predicate
* **Pattern**: Finding the minimum feasible value or maximum valid threshold across a bounded domain $[L, R]$.
* **Invariant**: Predicate (x)$ transitions monotonically from False -> True or True -> False.
* **Standard Implementation**:
  `python
  def binary_search(low: int, high: int) -> int:
      while low < high:
          mid = low + (high - low) // 2
          if condition(mid):
              high = mid
          else:
              low = mid + 1
      return low
  `

### C. Dynamic Programming (State Reduction & Memoization)
* **Pattern**: Optimal substructure and overlapping subproblems.
* **Steps**:
  1. Define minimal state variables (e.g., dp[i][mask]).
  2. Formulate the exact base cases.
  3. Formulate the recurrence relation.
  4. Optimize space by rolling arrays if state transitions only depend on previous step ((N)$ space).

### D. Graphs: Shortest Path & Topological Sort
* **Dijkstra**: Non-negative edge weights, min-heap priority queue (((V + E) \log V)$).
* **0-1 BFS**: Deque-based BFS for binary edge weights ((V + E)$).
* **Kahn's Algorithm**: Indegree tracking for DAG topological sort and cycle detection.
* **Tarjan's / Kosaraju's**: Strongly Connected Components (SCC) in directed graphs ((V + E)$).

### E. Advanced Data Structures
* **Disjoint Set Union (DSU)**: Path compression + union by rank for near (\alpha(N))$ connectivity queries.
* **Trie**: Prefix search, bitwise XOR maximization with binary tree representation.
* **Fenwick Tree (Binary Indexed Tree)**: (\log N)$ point updates and prefix range sum queries with (N)$ memory.

---

## 3. Engineering Invariants for Algorithmic Implementation
1. **Prevent Integer Overflow**: Use 64-bit integers for cumulative sums/products.
2. **Off-by-One Guard**: Use half-open intervals [start, end) consistently.
3. **Memory Footprint**: Prefer contiguous array allocations (vectors/typed arrays) over nested pointer nodes for cache locality.
