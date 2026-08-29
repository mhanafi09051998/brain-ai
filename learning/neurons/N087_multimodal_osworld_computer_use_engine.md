# Neuron N087: Multimodal OSWorld Computer Use & Agentic Search Engine

- **Kategori:** Computer Use & Agentic Web Search (OSWorld 2.0 & BrowseComp)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** OSWorld 2.0 ($>85.0\%$), BrowseComp ($>97.0\%$)

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Spatial Coordinate Normalization & Visual Grounding
- **Resolution-Independent Coordinates**: Seluruh titik koordinat klik/interaksi dinormalisasi ke rentang $[0, 1000] \times [0, 1000]$:
  $$x_{\text{norm}} = \text{round}\left(\frac{x_{\text{pixel}}}{W} \times 1000\right), \quad y_{\text{norm}} = \text{round}\left(\frac{y_{\text{pixel}}}{H} \times 1000\right)$$
- **Accessibility Tree (A11y) + Screenshot Fusion**: Melakukan parsing DOM Accessibility Tree secara paralel dengan segmentasi visual untuk menargetkan elemen secara deterministik tanpa terpengaruh pergeseran CSS/rendering glitch.

### 2. State-Action Loop & Visual Verification (Look-Before-Leap)
- **OODA Verification Invariant**: Sebelum dan sesudah setiap aksi GUI (Click, Type, Drag, KeyCombo), sistem memvalidasi perubahan state visual melalui *Pixel Diff Hash / DOM Snapshot*:
  $$\text{Action} \implies \text{Wait Event Loop} \implies \text{Verify Delta} (\Delta \text{State} \neq \emptyset)$$
- **Defensive Retries**: Jika aksi tidak memicu perubahan visual dalam timeout 3000ms, lakukan re-fokus elemen atau trigger fallback via *Keyboard Tab/Enter Navigation*.

### 3. Agentic Search & Multi-Source Synthesis (BrowseComp)
- **Query Diversification**: Menghasilkan 3 variasi kueri (Keyword Boolean, Natural Language Question, dan Negative Constraint Search) untuk menghindari *SEO bias* dan *hallucinated snippets*.
- **Deep Multi-Tab Traversal**: Ekstraksi fakta langsung dari halaman sumber primer (dokumen resmi, arXiv, GitHub commits, lembar data regulator) dengan verifikasi silang minimal 2 domain independen.

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
def normalize_click_coordinates(x: int, y: int, screen_w: int, screen_h: int) -> tuple[int, int]:
    """Mengonversi koordinat pixel absolut ke normalized coordinate grid 1000x1000."""
    norm_x = int(round((x / screen_w) * 1000))
    norm_y = int(round((y / screen_h) * 1000))
    return max(0, min(1000, norm_x)), max(0, min(1000, norm_y))

def denormalize_click_coordinates(norm_x: int, norm_y: int, screen_w: int, screen_h: int) -> tuple[int, int]:
    """Mengonversi normalized coordinate grid kembali ke pixel asli layar."""
    real_x = int(round((norm_x / 1000) * screen_w))
    real_y = int(round((norm_y / 1000) * screen_h))
    return real_x, real_y
```
