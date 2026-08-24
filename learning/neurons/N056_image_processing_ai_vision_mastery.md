# Neuron N056: Image Processing, Computer Vision & AI Visual Generation Mastery

- **Kategori**: Computer Vision, Classical Image Processing, Latent Diffusion Models, Node-Graph Generation, Alpha Matting, Raster-to-Vector Tracing, Low-Memory Streaming Pipelines, Deep Super-Resolution
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Menguasai matematika konvolusi spasial (Gaussian, Sobel, Laplacian, Sharpen), konversi ruang warna (RGB, Grayscale BT.601/BT.709, HSV, YCbCr), interpolasi geometris (Bilinear, Lanczos, Aspect Letterbox), arsitektur generasi visual AI (ComfyUI DAG, UNet/DiT Latent Diffusion, ControlNet Zero-Conv), segmentasi foreground (Alpha Matting U2Net), tracing raster-ke-vektor (Bézier polygonization), streaming citra hemat RAM (`libvips` chunking), serta super-resolusi mendalam (RRDB Real-ESRGAN).
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N007`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N007_self_improving_loop.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N015`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N015_compiler_ast_and_system_profiling.md), [`N026`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N026_vision_dom_spatial_reasoning.md), [`N027`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N027_tensor_simd_vectorization.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [`N039`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N039_webrtc_av_dsp_streaming.md)
- **Status**: Active Operational Invariant

---

## 1. Peta Repositori & Standar Visual Computing Terbaik Dunia

| Domain | Repositori / Standar Industri | Inti Algoritma / Metodologi | Kasus Penggunaan Kritis |
| :--- | :--- | :--- | :--- |
| **Classical Image Kernels & Color** | **`opencv/opencv`** & **`python-pillow/Pillow`** | Matriks konvolusi 2D, separability filter $O(K^2) \rightarrow O(2K)$, konversi ruang warna ITU-R BT.601/709, HSV hexagonal cone, Bilinear/Lanczos resampling. | Preprocessing citra, deteksi tepi Sobel, ekstraksi fitur spasial, penyesuaian kontras, manipulasi pixel real-time. |
| **Graph-Based Generative AI** | **`comfyanonymous/ComfyUI`** & **`huggingface/diffusers`** | Directed Acyclic Execution Graph (DAG), Latent Diffusion Models (LDM), UNet / Diffusion Transformer (DiT), K-diffusion schedulers (Euler, DPM++ 2M Karras). | Pipeline modular generasi visual AI, caching node eksekusi, prompt conditioning, VRAM dynamic swapping. |
| **Spatial Conditioning** | **`lllyasviel/ControlNet`** | Zero-Convolution initialized residual adapters, direct feature map injection pada skip-connections UNet/DiT. | Kontrol presisi spasial generasi AI menggunakan edge (Canny), depth maps, human pose keypoints, dan segmentation masks. |
| **Matting & Segmentation** | **`danielgatis/rembg`** (U2Net/MODNet) | Salient object detection, Alpha Matting ($I = \alpha F + (1-\alpha)B$), Trimap refinement, boundary softening. | Ekstraksi subjek otomatis, penghapusan latar belakang instan tanpa artefak halo, isolasi aset grafis e-commerce. |
| **Raster-to-Vector Tracing** | **`visioncortex/vtracer`** & **`potrace`** | Dual-color clustering quantization, pixel contour polygonization, subpixel vertex smoothing, cubic Bézier curve fitting. | Konversi bitmap raster (PNG/JPG) resolusi rendah ke vektor SVG resolusi tak terbatas tanpa kehilangan ketajaman. |
| **Low-Memory Image Streaming** | **`libvips/libvips`** | Demand-driven pull pipeline, horizontal scanline iterator, tile-based memory paging, zero-copy buffer slicing. | Pemrosesan citra raksasa (gigapixel, medical imaging, batch visual processing) dengan footprint RAM konstan sub-100MB. |
| **Deep Super-Resolution** | **`xinntao/Real-ESRGAN`** & **`ESRGAN`** | Residual-in-Residual Dense Block (RRDB), Sub-Pixel Convolution (PixelShuffle upsampling), Perceptual & Adversarial VGG Loss. | Restorasi citra terdegradasi parah, upscaling 4x–8x dengan rekonstruksi tekstur fotorealistik resolusi tinggi. |

---

## 2. Matematika Pemrosesan Citra Klasik (Classical Image Processing)

```
                            CLASSICAL IMAGE PROCESSING PIPELINE
                            
    [ Raw Pixel Buffer (H x W x C) ]
                   │
                   ├──► [ Color Space Math ] ──► Grayscale (BT.601/BT.709) / HSV / YCbCr
                   │
                   ├──► [ 2D Spatial Convolution ] ──► Gaussian Blur (Separable 1D x 1D)
                   │                                     Sobel Gradient Magnitude & Angle (Edge)
                   │                                     Laplacian & Unsharp Mask (Sharpen)
                   │
                   └──► [ Geometric Resampling ] ──► Bilinear Interpolation Grid
                                                       Aspect Ratio Letterbox / Padding
```

### A. 2D Spatial Convolution & Kernel Filters
Diberikan citra input $I(x, y)$ dan kernel filter $K$ berukuran $(2k+1) \times (2k+1)$:

$$(I * K)(x, y) = \sum_{u=-k}^{k} \sum_{v=-k}^{k} I(x-u, y-v) \cdot K(u+k, v+k)$$

1. **Gaussian Blur Kernel (Low-Pass Filter)**:
   $$G(u, v) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{u^2 + v^2}{2\sigma^2}\right)$$
   *Separability Property*: $G(u, v) = G_x(u) \cdot G_y(v)$, mereduksi kompleksitas komputasi dari $O(K^2 \cdot W \cdot H)$ menjadi $O(2K \cdot W \cdot H)$.

2. **Sobel Edge Detection (First-Order Spatial Derivatives)**:
   $$K_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad K_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$
   $$\text{Gradient Magnitude: } M(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2}$$
   $$\text{Gradient Orientation: } \theta(x, y) = \operatorname{atan2}(G_y(x, y), G_x(x, y)) \times \frac{180^\circ}{\pi}$$

3. **Laplacian & Sharpening (Second-Order Derivative)**:
   $$K_{\text{Laplacian}} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}, \quad K_{\text{Sharpen}} = \begin{bmatrix} 0 & -1 & 0 \\ -1 & 5 & -1 \\ 0 & -1 & 0 \end{bmatrix}$$

---

### B. Color Space Transformations

#### 1. RGB ke Grayscale (Luminosity Weighting)
Mata manusia memiliki sensitivitas fotoreseptor puncak pada spektrum hijau, diikuti merah, lalu biru:
- **ITU-R BT.601 (Standard Definition / OpenCV default)**:
  $$Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
- **ITU-R BT.709 (High Definition / sRGB)**:
  $$Y = 0.2126 \cdot R + 0.7152 \cdot G + 0.0722 \cdot B$$

#### 2. RGB ke HSV (Hue, Saturation, Value)
Diberikan $R, G, B \in [0, 1]$, $C_{\max} = \max(R, G, B)$, $C_{\min} = \min(R, G, B)$, dan $\Delta = C_{\max} - C_{\min}$:

$$V = C_{\max}$$

$$S = \begin{cases} 0, & \text{jika } C_{\max} = 0 \\ \frac{\Delta}{C_{\max}}, & \text{jika } C_{\max} > 0 \end{cases}$$

$$H = \begin{cases} 
0^\circ, & \text{jika } \Delta = 0 \\ 
60^\circ \times \left(\frac{G - B}{\Delta} \bmod 6\right), & \text{jika } C_{\max} = R \\ 
60^\circ \times \left(\frac{B - R}{\Delta} + 2\right), & \text{jika } C_{\max} = G \\ 
60^\circ \times \left(\frac{R - G}{\Delta} + 4\right), & \text{jika } C_{\max} = B 
\end{cases}$$

#### 3. RGB ke YCbCr (Luma-Chroma Video Subsampling)
$$Y = 0.299 R + 0.587 G + 0.114 B$$
$$C_b = 128 - 0.168736 R - 0.331264 G + 0.5 B$$
$$C_r = 128 + 0.5 R - 0.418688 G - 0.081312 B$$

---

### C. Geometric Resampling & Bilinear Interpolation
Diberikan koordinat kontinu $(x', y')$ pada citra asal dengan $x_0 = \lfloor x' \rfloor, x_1 = x_0 + 1, y_0 = \lfloor y' \rfloor, y_1 = y_0 + 1$, dan fractional offsets $dx = x' - x_0, dy = y' - y_0$:

$$f(x', y') = (1 - dx)(1 - dy) I(x_0, y_0) + dx(1 - dy) I(x_1, y_0) + (1 - dx)dy I(x_0, y_1) + dx \cdot dy I(x_1, y_1)$$

#### Aspect Ratio Preserving Letterbox
Untuk mengubah resolusi dari $(W_{\text{src}}, H_{\text{src}})$ ke target $(W_{\text{dst}}, H_{\text{dst}})$ tanpa distorsi rasio aspek:
$$s = \min\left(\frac{W_{\text{dst}}}{W_{\text{src}}}, \frac{H_{\text{dst}}}{H_{\text{src}}}\right)$$
$$W_{\text{scaled}} = \lfloor W_{\text{src}} \times s \rfloor, \quad H_{\text{scaled}} = \lfloor H_{\text{src}} \times s \rfloor$$
$$\text{pad}_x = \left\lfloor \frac{W_{\text{dst}} - W_{\text{scaled}}}{2} \right\rfloor, \quad \text{pad}_y = \left\lfloor \frac{H_{\text{dst}} - H_{\text{scaled}}}{2} \right\rfloor$$

---

## 3. Arsitektur AI Generatif Visual & Latent Diffusion

```
                       LATENT DIFFUSION & COMFYUI NODE GRAPH
                       
    [ Text Prompt ] ──► [ CLIP Text Encoder ] ──► Text Conditioning Embeddings (c_cross)
                                                         │
    [ Latent Seed (Random Noise z_T) ] ────────┐         │
                                               ▼         ▼
    [ Timestep Schedule (t_T ... t_0) ] ──► [ UNet / DiT Denoising Core ] ◄── [ ControlNet Spatial Guide ]
                                               │
                                               ▼
                                      [ Denoised Latent z_0 ]
                                               │
                                               ▼
                                    [ VAE Decoder D(z_0) ]
                                               │
                                               ▼
                                   [ High-Res RGB Output Image ]
```

### A. Latent Space Compression Factor
Model Latent Diffusion (LDM / Stable Diffusion / FLUX) tidak melakukan difusi pada ruang pixel $X \in \mathbb{R}^{H \times W \times 3}$, melainkan pada ruang laten terkodifikasi melalui Variational Autoencoder (VAE):
$$z = \mathcal{E}(x) \in \mathbb{R}^{\frac{H}{8} \times \frac{W}{8} \times 4}, \quad \hat{x} = \mathcal{D}(z)$$
- **Penghematan Komputasi**: Kompresi spatial $8\times$ mereduksi jumlah token komputasi $64\times$ ($8^2$).

### B. Diffusion Transformer (DiT) vs UNet Denoising
1. **UNet Backbone**: Menggunakan downsampling convolution encoder, spatial cross-attention layers, dan upsampling decoder dengan skip-connections.
2. **Diffusion Transformer (DiT)**:
   - Input latent $z_t$ dipecah menjadi sequence of patches $p \times p$ ($p=2$).
   - Di-embed menjadi patch tokens $T \in \mathbb{R}^{N \times d}$.
   - Menggunakan Transformer Blocks standar dengan **adaLN-Zero (Adaptive Layer Normalization Zero-Initialized)**:
     $$\text{adaLN}(h, y) = \gamma(y) \odot \left(\frac{h - \mu}{\sigma}\right) + \beta(y)$$
     di mana scaling $\gamma, \beta$ dan gate parameter $\alpha$ diinjeksi langsung dari timestep $t$ dan conditioning vector $c$.

### C. ControlNet Zero-Convolution Spatial Conditioning
ControlNet menduplikasi arsitektur encoder neural network dan menguncinya (*locked weights*), lalu menghubungkan cabangnya dengan lapisan *zero-convolution* ($1 \times 1$ conv dengan weights & bias diinisialisasi ke 0):
$$\mathcal{Z}(x; \Theta_{\mathcal{Z}}) = W_{\mathcal{Z}} \cdot x + B_{\mathcal{Z}} = 0 \quad (\text{pada iterasi awal})$$
$$y = \mathcal{F}(x; \Theta) + \mathcal{Z}(\mathcal{F}(x + \mathcal{Z}(c; \Theta_{z1}); \Theta_c); \Theta_{z2})$$
- Menjamin tidak ada noise berbahaya yang merusak model difusi dasar pada langkah awal pelatihan/inferensi.

---

## 4. Segmentasi Alpha Matting & Tracing Vektor (Raster-to-Vector)

### A. Alpha Matting Equation
Setiap pixel citra $I$ merupakan kombinasi linear dari warna Foreground $F$ dan Background $B$:
$$I(x, y) = \alpha(x, y) \cdot F(x, y) + (1 - \alpha(x, y)) \cdot B(x, y), \quad \alpha(x, y) \in [0, 1]$$
- **U2Net / Rembg Pipeline**:
  1. Deep Salient Feature Extraction menghasilkan coarse binary mask.
  2. Guided Filter / Laplacian Trimap Boundary Refinement membagi citra menjadi 3 zona: Definite Foreground ($\alpha=1$), Definite Background ($\alpha=0$), dan Unknown Transition Band ($\alpha \in (0, 1)$).
  3. Closed-Form Alpha Matting / Soft-edge Poisson Reconstruction menghitung nilai transparansi subpixel halus untuk rambut dan serat tipis.

### B. Tracing Raster-ke-Vektor (Potrace & VTracer)
1. **Color Quantization**: Mengelompokkan warna raster ke palet diskrit menggunakan K-Means atau Median Cut.
2. **Contour Pixel Boundary Walking**: Algoritma Moore-Neighbor / Radial Sweep menelusuri boundary loop dari pulau piksel warna yang sama.
3. **Polygon Simplification (Ramer-Douglas-Peucker - RDP)**:
   Mereduksi verteks tak perlu dengan mengeliminasi titik yang memiliki jarak tegak lurus $\le \epsilon$ dari garis baseline segmen:
   $$d = \frac{|(y_2 - y_1)x_0 - (x_2 - x_1)y_0 + x_2 y_1 - y_2 x_1|}{\sqrt{(y_2 - y_1)^2 + (x_2 - x_1)^2}}$$
4. **Cubic Bézier Curve Fitting**:
   $$B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3, \quad t \in [0, 1]$$

---

## 5. Streaming Citra Memori Rendah (`libvips`) & Super-Resolution (`Real-ESRGAN`)

### A. Libvips Demand-Driven Streaming Architecture
- **Problem**: Memuat citra $20,000 \times 20,000$ RGBA 8-bit ke RAM membutuhkan $\approx 1.6 \text{ GB}$ buffer mentah dalam memori kontinu.
- **Solusi Libvips**: Pipeline *demand-driven pull*:
  - Citra direpresentasikan sebagai graph of operations (bukan array in-memory).
  - Sink node (misal: file saver atau tile viewer) meminta wilayah kecil $(x, y, w, h)$.
  - Generator memproses citra per baris scanline horizontal atau blok ubin (*tile*) $256 \times 256$ piksel.
  - Footprint memori tetap konstan sub-50MB berapapun gigapixel ukuran citranya.

### B. Real-ESRGAN Super-Resolution (RRDB Architecture)
- Menggantikan Residual Block konvensional dengan **Residual-in-Residual Dense Block (RRDB)** tanpa batch normalization untuk mencegah artefak warna.
- **Sub-Pixel Convolution (PixelShuffle)**:
  $$\text{Feature Map } (H \times W \times C \cdot r^2) \xrightarrow{\text{PixelShuffle}} \text{High-Res Output } (rH \times rW \times C)$$
  Menghilangkan komputasi dekonvolusi/transposed-conv yang rentan artefak checkerboard.

---

## 6. Invarian Operasional & Aturan Emas Claudia (Visual Invariants)

1. **Deterministic Coordinate Clamping**: Setiap akses piksel matriks berkoordinat $(x, y)$ di luar batas $[0, W-1] \times [0, H-1]$ wajib ditangani dengan strategi deterministik (`replicate`, `reflect`, atau `constant`), jangan pernah membiarkan unhandled `IndexError`.
2. **Channel Value Boundaries**: Nilai kanal warna RGB wajib di-clamp strictly pada rentang $[0, 255]$ integer atau $[0.0, 1.0]$ float sebelum diekspor atau dialirkan antar-tahap.
3. **Aspect-Ratio Fidelity**: Jangan pernah melakukan *non-uniform stretching* pada citra antarmuka pengguna atau foto tanpa persetujuan eksplisit. Gunakan Letterbox Padding atau Center Crop untuk mempertahankan rasio aspek alami.
4. **Zero-Memory-Spike Streaming**: Operasi citra berskala besar wajib menggunakan chunking / tile-based generators agar RAM footprint tidak melonjak proporsional terhadap ukuran file.
5. **No External Dependency Core**: Seluruh algoritma fondasional (konvolusi, grayscale, HSV, bilinear, letterbox, DAG execution) harus memiliki implementasi referensi Python murni yang siap berjalan di lingkungan tanpa dependensi C/C++ sekalipun.

---

## 7. Referensi Eksekusi Mandiri: Python Nucleus Engine

Implementasi algoritma produksi lengkap tersedia dan teruji 100% pada file:
[`scripts/image_vision_nucleus_engine.py`](file:///D:/Agent_Claudia_Autonomus/scripts/image_vision_nucleus_engine.py)

Neuron ini menjadi landasan kognitif komputasi visual, image processing, dan multimodal spatial synthesis Claudia.
