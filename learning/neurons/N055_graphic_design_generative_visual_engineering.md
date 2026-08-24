# Neuron N055: Graphic Design, Generative Visual Engineering & Vector Math Mastery

- **Kategori**: Graphic Design, Generative Art, Perceptually Uniform Color Spaces (CIELAB/LCh), WCAG 2.2 Accessibility, Cubic Bézier Geometry & 24px Vector Iconography
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Menguasai arsitektur grafis vektor murni berbasis SVG/CSS box-model (`penpot`), transformasi koordinat visual & seni generatif parametrik (`p5.js`), matematika warna perseptual seragam CIELAB/LCh & kalkulasi kontras WCAG 2.2 AAA (`chroma.js`), kalkulasi diferensial kurva Bézier kubik & kuadratur panjang busur Gauss-Legendre (`paper.js`), standardisasi ikon grid 24px (`lucide-icons`), dan sekuensing animasi kinetik timeline (`remotion`).
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N003`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N003_mobile_first_ui.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N017`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N017_program_aided_math.md), [`N026`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N026_vision_dom_spatial_reasoning.md), [`N036`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N036_fullstack_product_synthesizer.md), [`N051`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N051_system_architecture_devops_mastery.md), [`N054`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N054_system_design_planning_mastery.md)
- **Status**: Active Operational Invariant

---

## 1. Peta Repositori, Library & Standar Visual Engineering Terbaik Dunia

| Domain | Repositori / Standar Industri | Inti Algoritma / Metodologi | Kasus Penggunaan Kritis |
| :--- | :--- | :--- | :--- |
| **Vector Engine & Box Model** | **`penpot/penpot`** | SVG standard DOM tree, CSS Flexbox/Grid constraints, Path Boolean Ops (Union, Subtract, Intersect) | Rendering desain antarmuka berbasis vektor murni tanpa kehilangan ketajaman resolusi pada layar retina/4K. |
| **Generative Art & Coordinate Math** | **`processing/p5.js`** | Affine Matrix transformations ($T \cdot R \cdot S$), Parametric Curves (Lissajous, Rose, Superformula), Perlin Noise | Visualisasi data kinetik, artwork prosedural deterministik, dan pola partikel adaptif real-time. |
| **Perceptual Color & Accessibility** | **`gka/chroma.js`** & **W3C WCAG 2.2** | CIE XYZ $\to$ CIELAB $\to$ CIELCh transformations, Relative Luminance ($Y$), Contrast Ratio $(L_1+0.05)/(L_2+0.05)$ | Kalkulasi otomatis palet warna harmonis yang lolos sertifikasi aksesibilitas WCAG AA (4.5:1) dan AAA (7.0:1). |
| **Vector Geometry & Bézier Math** | **`paperjs/paper.js`** | De Casteljau subdivision, first/second parametric derivatives ($B'(t), B''(t)$), Gauss-Legendre quadrature length | Interpolasi kurva animasi halus, path offset, dynamic stroke generation, dan kalkulasi panjang garis vektor. |
| **Micro-Iconography & Kinetic Timelines** | **`lucide-icons/lucide`** & **`remotion-dev/remotion`** | 24x24 px grid snapping, 2px uniform stroke weight, spring physics ($F = -kx - cv$), keyframe interpolation | Desain sistem ikon terstandarisasi konsisten serta rendering video/animasi berbasis komponen web deterministik. |

---

## 2. Matematika Sains Warna Perseptual & Standar Aksesibilitas WCAG 2.2

```
                                COLOR SCIENCE CONVERSION PIPELINE
                                
   [ sRGB (0-255) ] ──(Linearization)──► [ Linear sRGB (0.0-1.0) ]
                                                   │
                                     (Matrix Transformation D65)
                                                   │
                                                   ▼
   [ CIELCh (L*, C*, h°) ] ◄──(Polar)── [ CIELAB (L*, a*, b*) ] ◄──(CIE XYZ)
           │                                                               │
   (Harmonies: Mono, Ana, Triad)                              (Relative Luminance Y)
                                                                           │
                                                                           ▼
                                                             [ WCAG 2.2 Contrast Ratio ]
                                                             - AA Normal:  >= 4.5:1
                                                             - AA Large:   >= 3.0:1
                                                             - AAA Normal: >= 7.0:1
```

### A. Linearitas sRGB dan Luminansi Relatif ($Y$)
Konversi kanal sRGB non-linear $C \in \{R, G, B\}$ terkompresi gamma ke nilai linear $C_{\text{linear}}$:

$$C_{\text{linear}} = \begin{cases} \frac{C / 255}{12.92}, & \text{jika } C / 255 \le 0.04045 \\ \left(\frac{(C / 255) + 0.055}{1.055}\right)^{2.4}, & \text{jika } C / 255 > 0.04045 \end{cases}$$

Kalkulasi luminansi relatif standar WCAG 2.2 (standar CIE 1931 D65 observer):

$$Y = 0.2126 \cdot R_{\text{linear}} + 0.7152 \cdot G_{\text{linear}} + 0.0722 \cdot B_{\text{linear}}$$

### B. Rasio Kontras WCAG ($\text{CR}$)
Diberikan dua luminansi $L_1$ dan $L_2$ dengan $L_1 \ge L_2$:

$$\text{CR} = \frac{L_1 + 0.05}{L_2 + 0.05} \in [1.0, 21.0]$$

| Ambang Batas WCAG 2.2 | Minimum Rasio Kontras | Kasus Penggunaan |
| :--- | :--- | :--- |
| **WCAG AA Normal Text** | $\text{CR} \ge 4.5 : 1$ | Teks paragraf biasa (< 18pt regular atau < 14pt bold) |
| **WCAG AA Large Text** | $\text{CR} \ge 3.0 : 1$ | Teks besar ($\ge 18\text{pt}$ atau $\ge 14\text{pt}$ bold) & UI icons/borders |
| **WCAG AAA Normal Text** | $\text{CR} \ge 7.0 : 1$ | Standar keterbacaan tinggi untuk konten kritis |
| **WCAG AAA Large Text** | $\text{CR} \ge 4.5 : 1$ | Teks judul besar standar aksesibilitas enterprise tinggi |

### C. Ruang Warna CIELAB dan CIELCh (Perceptually Uniform)
Transformasi dari CIE XYZ ke CIELAB dengan titik putih referensi D65 ($X_n = 0.95047, Y_n = 1.0, Z_n = 1.08883$):

$$L^* = 116 \cdot f\left(\frac{Y}{Y_n}\right) - 16, \quad a^* = 500 \left[f\left(\frac{X}{X_n}\right) - f\left(\frac{Y}{Y_n}\right)\right], \quad b^* = 200 \left[f\left(\frac{Y}{Y_n}\right) - f\left(\frac{Z}{Z_n}\right)\right]$$

$$f(t) = \begin{cases} t^{1/3}, & \text{jika } t > \left(\frac{6}{29}\right)^3 \approx 0.008856 \\ \frac{1}{3}\left(\frac{29}{6}\right)^2 t + \frac{4}{29}, & \text{lainnya} \end{cases}$$

Konversi koordinat silinder CIELCh:

$$C^* = \sqrt{(a^*)^2 + (b^*)^2}, \quad h^\circ = \operatorname{atan2}(b^*, a^*) \cdot \frac{180}{\pi} \pmod{360^\circ}$$

---

## 3. Matematika Diferensial Kurva Bézier Kubik & Kuadratur Panjang Busur

### A. Persamaan Parametrik Kurva Bézier Kubik
Didefinisikan oleh 4 titik kontrol $P_0, P_1, P_2, P_3 \in \mathbb{R}^2$ untuk parameter $t \in [0, 1]$:

$$B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3$$

### B. Vektor Kecepatan (Tangent), Percepatan & Kelengkungan (Curvature)
Turunan pertama dan kedua terhadap $t$:

$$B'(t) = 3(1-t)^2 (P_1 - P_0) + 6(1-t)t (P_2 - P_1) + 3t^2 (P_3 - P_2)$$

$$B''(t) = 6(1-t)(P_2 - 2P_1 + P_0) + 6t(P_3 - 2P_2 + P_1)$$

- **Vektor Tangen Satuan**: $\hat{T}(t) = \frac{B'(t)}{\|B'(t)\|}$
- **Vektor Normal Satuan**: $\hat{N}(t) = (-\hat{T}_y, \hat{T}_x)$
- **Kelengkungan Berarah (Signed Curvature)**:

$$\kappa(t) = \frac{x'(t)y''(t) - y'(t)x''(t)}{\left(x'(t)^2 + y'(t)^2\right)^{3/2}}$$

### C. Estimasi Panjang Busur dengan 5-Point Gauss-Legendre Quadrature
Panjang busur terhitung dari integral magnitudo turunan kecepatan $L = \int_0^1 \|B'(t)\| \, dt$. Pendekatan numerik deterministik tanpa komputasi berat:

$$L \approx \sum_{i=1}^N \frac{\Delta t}{2} \sum_{k=1}^5 w_k \left\|B'\left(t_{i,\text{start}} + \frac{x_k + 1}{2} \Delta t\right)\right\|$$

Di mana titik evaluasi ($x_k$) dan bobot ($w_k$) untuk 5-point quadrature:
- $x_0 = 0, \quad w_0 = \frac{128}{225} \approx 0.568889$
- $x_{\pm 1} = \pm \frac{1}{3}\sqrt{5 - 2\sqrt{10/7}}, \quad w_{\pm 1} = \frac{322 + 13\sqrt{70}}{900} \approx 0.478629$
- $x_{\pm 2} = \pm \frac{1}{3}\sqrt{5 + 2\sqrt{10/7}}, \quad w_{\pm 2} = \frac{322 - 13\sqrt{70}}{900} \approx 0.236927$

### D. Subdivisi De Casteljau
Membagi kurva kubik pada titik parameter $t_0$ menjadi dua segmen kurva kubik baru tanpa kehilangan kontinuitas $C^2$:

```
P0 ───► P01 ───► P012 ───► P0123 (Titik Tengah)
P1 ───► P12 ───► P123 ───► P0123
P2 ───► P23
P3
```
- Segmen Kiri: $\text{Bezier}(P_0, P_{01}, P_{012}, P_{0123})$
- Segmen Kanan: $\text{Bezier}(P_{0123}, P_{123}, P_{23}, P_3)$

---

## 4. Standar Ikonografi Grid 24px (Lucide/Penpot) & Animasi Kinetik

### A. Kaidah Vektor Grid 24x24 Pixel
1. **ViewBox Baku**: `viewBox="0 0 24 24"`, `width="24"`, `height="24"`.
2. **Stroke Geometry**:
   - `stroke-width="2"` (2px baku).
   - `stroke-linecap="round"` & `stroke-linejoin="round"`.
   - `fill="none"` (outline style) atau `fill="currentColor"`.
3. **Pixel Snapping & Padding**:
   - 2px minimum padding dari batas luar grid (live area: $20 \times 20\text{px}$).
   - Koordinat titik ujung garis harus berada pada kelipatan integer atau $0.5\text{px}$ untuk mencegah anti-aliasing buram pada layar non-retina.
4. **Optical Centering**:
   - Pusat gravitasi visual bentuk geometris (segitiga, play icon) digeser $1\text{px}$ ke kanan untuk mengompensasi asimetri massa optik.

### B. Fisika Pegas Kinetik (Spring Physics Timeline)
Model dinamika pegas teredam (*damped harmonic oscillator*) untuk transisi visual natural:

$$m \frac{d^2 x}{dt^2} + c \frac{dx}{dt} + k(x - x_{\text{target}}) = 0$$

Dengan rasio redaman (*damping ratio*) $\zeta = \frac{c}{2\sqrt{mk}}$:
- **Underdamped ($\zeta < 1.0$)**: Menghasilkan efek *overshoot / bounce* yang elastis dan hidup.
- **Critically Damped ($\zeta = 1.0$)**: Transisi tercepat mencapai target tanpa overshoot (ideal untuk UI modal/popover).

---

## 5. Implementasi Mesin Visual Python Murni (`scripts/graphic_design_visual_engine.py`)

Mesin nukleus visual telah diimplementasikan penuh di [`scripts/graphic_design_visual_engine.py`](file:///D:/Agent_Claudia_Autonomus/scripts/graphic_design_visual_engine.py) dengan fitur:
- `Color`: Parsing HEX/HSL/CIELAB/CIELCh, luminansi relatif, rasio kontras WCAG 2.2, dan pengujian kesesuaian AA/AAA.
- `PaletteGenerator`: Pembangkit palet Monokromatik, Analog, Komplementer, Triadik, Split-Komplementer, Tetradik, dan Gradien Multi-stop CIELAB.
- `Vec2D` & `CubicBezier`: Kalkulasi kurva parametrik, tangen, normal, kelengkungan, kuadratur panjang busur 5-titik Gauss-Legendre, dan subdivisi De Casteljau.
- `IconBuilder24`: Generator SVG standar Lucide / Penpot pada grid 24px.
- `GenerativePoster`: Pembangkit karya seni poster geometris prosedural berbasis kurva Lissajous 3D dan ornamen Bézier.
- **Suite Pengujian Deterministik 100% Lulus**.

---

## 6. Invarian Operasional & Aturan Koding Claudia (Visual Invariants)

1. **Accessibility First (WCAG 2.2 AA / AAA Invariant)**:
   - Semua elemen teks yang dirender pada UI atau materi grafis wajib memiliki rasio kontras $\ge 4.5:1$ (AA) dan diprioritaskan $\ge 7.0:1$ (AAA).
2. **Pure Vector Box Model (Zero Rasterization Artifacts)**:
   - Semua aset grafis, ikon, dan poster dibuat menggunakan SVG prosedural murni dengan koordinat parametrik presisi tinggi.
3. **No Heavy Dependency Constraint**:
   - Seluruh logika warna, Bézier, dan pembangkit SVG dijalankan secara instan menggunakan standard library Python murni tanpa ketergantungan paket pihak ketiga (PIL/Pillow, NumPy, Matplotlib tidak diperlukan untuk operasi inti).
4. **Snapping & Optical Alignment Invariant**:
   - Path ikon 24px wajib memanfaatkan titik koordinat bulat atau kelipatan 0.5px untuk menjaga ketajaman render sub-pixel.
