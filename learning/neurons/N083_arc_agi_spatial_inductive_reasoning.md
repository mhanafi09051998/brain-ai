# Neuron N083: ARC-AGI-3 Spatial Inductive Reasoning & DSL Program Synthesis

- **Kategori:** Novel Problem-Solving & Abstract Reasoning (ARC-AGI-3)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** ARC-AGI-3 ($>45.0\%$), ARC-Prize Invariants

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Dekomposisi Objek Spasial (Connected-Component Labeling & Topology)
- **Object Extraction Invariant**: Representasi grid 2D diurai menjadi himpunan objek diskrit melalui *4-way/8-way Flood Fill* dan *Connected-Component Labeling (CCL)*.
- **Topological Invariants**: Properti geometri yang invarian terhadap translasi:
  - *Euler Characteristic* $\chi = V - E + F$ (deteksi lubang/enclosure).
  - *Bounding Box Geometry* (aspek rasio, pusat massa / centroid $\bar{x} = \frac{1}{A}\sum x$, $\bar{y} = \frac{1}{A}\sum y$).
  - *Color Palette Invariance* (abstraksi pemetaan warna ke relasi fungsional/simbolik).

### 2. Domain-Specific Language (DSL) Program Induction
- **Shortest Program (MDL Principle)**: Hipotesis transformasi terbaik adalah program DSL terpendek (*Minimum Description Length*) yang konsisten pada seluruh pasangan contoh *train*:
  $$\mathcal{L}(T) = \arg\min_{P \in \text{DSL}} \left( |P| + \lambda \sum_{i} \mathbb{I}(P(X_i) \neq Y_i) \right)$$
- **Primitive Transformations Hierarchy**:
  1. *Geometric Operators*: Rotasi ($90^\circ, 180^\circ, 270^\circ$), Refleksi horizontal/vertikal/diagonal, Translasi vector $(\Delta x, \Delta y)$.
  2. *Color & Mask Operators*: Color swap, Background fill, Convex hull infill, Boundary outline.
  3. *Gravity & Physics Projection*: Jatuh ke arah gravitasi hingga menabrak boundary/obstacle terdekat.
  4. *Pattern Periodicity & Tessellation*: Ekstrapolasi kisi periodik ($N \times M$ kernel repeat).

### 3. Cellular Automata & Constraint Propagation
- **Local Rule Synthesis**: Jika transformasi bersifat global homogen, sintesis aturan transisi lokal $3 \times 3$ kernel von Neumann / Moore neighborhood.
- **Deductive Forward Check**: Eksekusi program DSL pada input uji (*test input*) dengan validasi dimensi $(H_{out}, W_{out})$ dan konsistensi palet warna sebelum inferensi final.

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
def extract_connected_components(grid: list[list[int]], background: int = 0) -> list[dict]:
    """Mengekstraksi objek 2D terisolasi beserta bounding box dan luasnya."""
    H, W = len(grid), len(grid[0])
    visited = [[False] * W for _ in range(H)]
    components = []
    
    for r in range(H):
        for c in range(W):
            if grid[r][c] != background and not visited[r][c]:
                color = grid[r][c]
                coords = []
                queue = [(r, c)]
                visited[r][c] = True
                
                while queue:
                    curr_r, curr_c = queue.pop(0)
                    coords.append((curr_r, curr_c))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < H and 0 <= nc < W and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                
                min_r = min(p[0] for p in coords)
                max_r = max(p[0] for p in coords)
                min_c = min(p[1] for p in coords)
                max_c = max(p[1] for p in coords)
                
                components.append({
                    "color": color,
                    "pixels": coords,
                    "bbox": (min_r, min_c, max_r - min_r + 1, max_c - min_c + 1),
                    "area": len(coords)
                })
    return components
```
