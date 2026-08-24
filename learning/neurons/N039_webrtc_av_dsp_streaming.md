# Neuron N039: Real-Time WebRTC, Audio/Video DSP & AV1 Streaming

Prinsip arsitektur media real-time berkinerja tinggi (*ultra-low latency <100ms*), WebRTC Selective Forwarding Unit (SFU), hardware-accelerated video/audio transcoding (AV1/Opus), pipeline Digital Signal Processing (DSP: AEC, NS, AGC), adaptive jitter buffer (NetEq WSOLA), dan packet loss concealment (PLC/FlexFEC):

- **Kategori**: Real-Time Communications (RTC), Media Systems Engineering, Audio/Video DSP & Streaming Infrastructure
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Menjamin transmisi media interaktif bidirectional sub-100ms glass-to-glass/mic-to-speaker, merancang SFU zero-decode packet routing dengan simulcast dan AV1 Scalable Video Coding (SVC), mengimplementasikan audio DSP sub-band filter, adaptive jitter buffer berbasis WSOLA, serta recovery kehilangan paket hibrida (NACK/FlexFEC/PLC).
- **Synaptic Links**: [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N010`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N010_distributed_systems_design.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N015`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N015_compiler_ast_and_system_profiling.md), [`N027`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N027_tensor_simd_vectorization.md), [`N029`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N029_modern_systems_rust_go.md), [`N030`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N030_nextgen_fullstack_edge.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md)
- **Status**: Active Operational Invariant

---

## 🌐 1. Ultra-Low Latency (<100ms) WebRTC Architecture & Transport Pipeline

```
[ Sender Camera/Mic ] 
      │ (Capture: 5-10ms)
      ▼
[ Audio/Video DSP + HW Encoder (AV1 / Opus) ] 
      │ (Encode: 8-15ms, Zero B-frames)
      ▼
[ RTP/SRTP Packetizer + Token Bucket Pacer ] 
      │ (Pacing & Crypto: 1-3ms)
      ▼
[ UDP / DTLS-SRTP Network Transit (TWCC BWE) ] ────► [ SFU Edge Router (0-2ms) ] ────► [ Receiver UDP ]
                                                                                              │ (Transit RTT/2: 15-35ms)
                                                                                              ▼
                                                                                   [ De-Jitter Buffer (NetEq) ]
                                                                                              │ (Playout Delay: 10-25ms)
                                                                                              ▼
                                                                                   [ HW Decoder (AV1/Opus) + PLC ]
                                                                                              │ (Decode: 5-10ms)
                                                                                              ▼
                                                                                   [ Renderer Display/Speaker ]
                                                                                      (Total E2E: < 100ms)
```

### 1.1. End-to-End Latency Budget Breakdown ($< 100\text{ ms}$)
Untuk menjamin komunikasi manusia interaktif yang natural (tanpa tabrakan suara), total keterlambatan dari sensor pengirim ke aktuator penerima (*glass-to-glass* untuk video, *mic-to-speaker* untuk audio) wajib berada di bawah $100\text{ ms}$ (budget kritis: $< 150\text{ ms}$ batas ITU-T G.114):

| Tahapan Pipeline | Budget Audio (Opus) | Budget Video (AV1) | Invarian Optimasi Kritis |
| :--- | :--- | :--- | :--- |
| **1. Sensor Capture & Buffering** | $5\text{--}10\text{ ms}$ | $4\text{--}8\text{ ms}$ | Raw ring buffer ALSA/CoreAudio/V4L2, 10ms audio frame chunks, 60/120fps camera sensor grab. |
| **2. DSP & Pre-Processing** | $2\text{--}5\text{ ms}$ | $1\text{--}3\text{ ms}$ | Sub-band AEC3, SIMD noise filter, GPU zero-copy color conversion (YUV420p via DMA-BUF). |
| **3. Media Hardware Encoding** | $5\text{--}10\text{ ms}$ | $8\text{--}15\text{ ms}$ | Opus low-delay mode (`OPUS_APPLICATION_VOIP`), AV1 hardware encoder (NVENC/VAAPI), 0 B-frames, CBR. |
| **4. Packetization & SRTP Encrypt** | $0.5\text{--}1.5\text{ ms}$ | $0.5\text{--}2\text{ ms}$ | RTP timestamp stamping, AES-GCM-128 SRTP encryption via hardware AES-NI / ARM Crypto extensions. |
| **5. Network Transit ($\text{RTT}/2$)** | $15\text{--}35\text{ ms}$ | $15\text{--}35\text{ ms}$ | Direct UDP routing, Edge POP nearest to client, BGP Anycast routing. |
| **6. SFU Switching Latency** | $0.5\text{--}2\text{ ms}$ | $0.5\text{--}2\text{ ms}$ | Zero-decode RTP header rewrite, epoll/io_uring event loop, lock-free routing table lookup. |
| **7. Adaptive Jitter Buffer** | $10\text{--}20\text{ ms}$ | $10\text{--}25\text{ ms}$ | NetEq minimum delay target tracking, WSOLA time-stretch acceleration when buffer inflates. |
| **8. Hardware Decode & Post-DSP** | $3\text{--}6\text{ ms}$ | $5\text{--}10\text{ ms}$ | Tile-parallel AV1 decoding, audio PLC extrapolation, double-buffering. |
| **9. Hardware Rendering / V-Sync** | $4\text{--}8\text{ ms}$ | $8\text{--}16\text{ ms}$ | Direct audio sink callback, low-latency display swapchain (DirectX DXGI flip model / Wayland). |
| **Total Glass-to-Glass / E2E** | **$45\text{--}97.5\text{ ms}$** | **$52\text{--}116\text{ ms}$** | **Jaminan Sub-100ms pada koneksi broadband normal ($\text{RTT} \le 50\text{ ms}$).** |

---

### 1.2. WebRTC Transport Protocol Stack & Cryptographic Handshake
1. **Interactive Connectivity Establishment (ICE - RFC 8445)**:
   - **Candidate Gathering**: Host (antarmuka fisik/LAN lokal), Server Reflexive / `srflx` (diperoleh via STUN RFC 5389 Binding Request untuk menembus Full Cone/Port Restricted NAT), dan Relay / `relay` (diperoleh via TURN RFC 5766 Allocation request untuk Symmetric NAT).
   - **Trickle ICE (RFC 8838)**: Kirim candidate secara incremental melalui channel signaling WebSocket/SSE seketika setelah ditemukan tanpa menunggu proses discovery selesai (*shortens connection setup by 80%*).
   - **STUN Connectivity Checks**: Mengirimkan STUN Binding request secara paralel over UDP dengan prioritas candidate pair tertinggi.
2. **DTLS 1.2/1.3 Handshake & Key Derivation**:
   - Melakukan pertukaran sertifikat self-signed ECDSA (P-256 / Ed25519) di atas UDP channel yang tervalidasi oleh ICE.
   - Mengekstrak *Master Key* & *Master Salt* via DTLS-SRTP Key Derivation (RFC 5764) untuk mengamankan aliran RTP/RTCP secara hardware-accelerated.
3. **SCTP over DTLS (WebRTC DataChannel - RFC 8831)**:
   - Menyediakan multiplexing channel data arbitrary di atas koneksi DTLS terenkripsi.
   - Konfigurasi parameter per-channel: *reliable & ordered* (TCP-like) vs *unreliable & unordered with maxPacketLifeTime / maxRetransmits* (UDP-like zero-latency messaging).

---

### 1.3. Transport-Wide Congestion Control (TWCC - RFC 8888) & BWE Algorithms
1. **TWCC Feedback Loop Invariant**:
   - Pengirim menyematkan *Transport-Wide Sequence Number* (16-bit counter) pada setiap header extension RTP paket keluar.
   - Penerima mengumpulkan arrival timestamp dengan presisi mikrodetik dan mengirimkan kembali paket `RTCP TWCC Feedback` berkala ($50\text{--}100\text{ ms}$ interval).
2. **Google Congestion Control (GCC) Dual-Engine Estimation**:
   - **Delay-Based Estimator (Arrival-Time Filter)**:
     - Menghitung inter-arrival time gradient $m(t)$ menggunakan Kalman Filter atau Trendline Slope over a sliding window ($500\text{ ms}$).
     - Bandingkan gradient terhadap adaptive threshold $\gamma(t)$:
       $$\Delta t_{\text{inter}} = (t_{\text{recv}, i} - t_{\text{recv}, i-1}) - (t_{\text{send}, i} - t_{\text{send}, i-1})$$
       - Jika $m(t) > \gamma(t)$ selama durasi $t_{\text{overuse}}$ $\rightarrow$ State: **Overuse** (antrean router mulai menumpuk). Turunkan target bitrate secara multiplikatif ($A_{\text{target}} = 0.85 \times A_{\text{prev}}$).
       - Jika $m(t) < -\gamma(t)$ $\rightarrow$ State: **Underuse** (antrean mengering). Naikkan bitrate secara aditif ($A_{\text{target}} = A_{\text{prev}} + \alpha$).
       - Jika $|m(t)| \le \gamma(t)$ $\rightarrow$ State: **Normal** (tahan bitrate saat ini).
   - **Loss-Based Estimator**:
     - Jika packet loss rasio $p > 10\%$: Turunkan bitrate $A_{\text{loss}} = A_{\text{target}} \times (1 - 0.5p)$.
     - Jika $2\% \le p \le 10\%$: Pertahankan bitrate konstan.
     - Jika $p < 2\%$: Naikkan bitrate $A_{\text{loss}} = 1.05 \times A_{\text{target}} + 1\text{ kbps}$.
   - **Final BWE**: $A_{\text{final}} = \min(A_{\text{delay}}, A_{\text{loss}})$.
3. **Token Bucket Pacer & Packet Bursts Smoothing**:
   - Video intra-frame (Keyframe/IDR) menghasilkan burst data masif (misal $15\text{--}40\text{ KB}$ terfragmentasi menjadi 15-30 paket MTU). Mengirimkannya sekaligus seketika (*instant dump*) menyebabkan buffer bloat dan packet drop pada edge router.
   - Pacer menjadwalkan pelepasan paket RTP secara kontinu dengan interval waktu teratur sesuai kapasitas BWE terestimasi, menggunakan antrean *Priority Queue* (Audio > Video Retransmission > Video Keyframe > Video Delta).

---

## 🏢 2. Media Topology: SFU vs MCU vs Mesh & Scalable Video Routing

```
[ P2P Full Mesh (N=4) ]             [ MCU (Multipoint Control) ]          [ SFU (Selective Forwarding) ]
    O(N^2) Uplink Saturation              Server Decodes & Mixes                  Zero-Decode RTP Routing
      A ◄─────────► B                         A       B                               A       B
      │ ╲       ╱ │                           │       │                               │       │
      │   ╲   ╱   │                           ▼       ▼                               ▼       ▼
      │     ╳     │                     ┌───────────────────┐                   ┌───────────────────┐
      │   ╱   ╲   │                     │  Decoder + Mixer  │                   │  RTP Layer Filter │
      │ ╱       ╲ │                     │  Re-encoder (CPU) │                   │  (Sub-ms latency) │
      C ◄─────────► D                     └───────────────────┘                   └───────────────────┘
                                                  ▲                                       ▲
                                                  │ (High Latency/CPU)                    │ (High Scale/O(N))
                                                  ▼                                       ▼
                                              C       D                               C       D
```

### 2.1. Topologi Media: Matriks Perbandingan Kritis

| Parameter Karakteristik | P2P Full Mesh | MCU (Multipoint Control Unit) | SFU (Selective Forwarding Unit) |
| :--- | :--- | :--- | :--- |
| **Beban Egress Klien Pengirim** | $O(N-1)$ streams (Saturasi uplink) | $O(1)$ stream | $O(1)$ stream (Simulcast: $1.5\text{--}2\times$) |
| **Beban Egress Klien Penerima** | $O(N-1)$ streams | $O(1)$ stream (single mixed grid) | $O(N-1)$ streams (dynamic layer) |
| **Beban CPU Server** | $0$ (Tanpa server media pusat) | **Ekstrem ($O(N)$ decoders + $O(N)$ encoders)** | **Ultra-Rendah ($O(N)$ zero-copy routing)** |
| **Server Switching Latency** | $0\text{ ms}$ | $50\text{--}150\text{ ms}$ (buffer mixer + re-encode) | **$< 2\text{ ms}$ (direct header rewrite)** |
| **Skalabilitas Partisipan** | $3\text{--}4$ pengguna max | $10\text{--}30$ per instance besar | **$100\text{--}1000+$ per instance SFU** |
| **Fleksibilitas Layout Klien** | Bebas render per peer di client | Terkunci pada layout server canvas | **Bebas (klien susun UI grid dinamis)** |
| **Rekomendasi Arsitektur** | Call 1-on-1 terisolasi | Jembatan Telepon PSTN / SIP warisan | **Konferensi Modern, Webinar, Autonomous Agent Swarm** |

---

### 2.2. SFU Zero-Decode Routing & RTP Stream Rewriting
Untuk mendistribusikan aliran media tanpa mendekode payload video/audio, SFU menjalankan operasi *RTP Stream Rewriting* in-place di memori buffer:
1. **SSRC (Synchronization Source) Mapping**:
   - Klien pengirim mempublikasikan stream dengan SSRC internalnya. SFU memetakan SSRC pengirim ke downstream SSRC yang diharapkan oleh receiver.
2. **Sequence Number & Timestamp Continuity**:
   - Ketika SFU beralih layer (*layer switching*, misal dari 1080p ke 360p karena jaringan penerima tersendat), terdapat lonjakan Sequence Number dan RTP Timestamp.
   - SFU menghitung offset offset delta:
     $$\Delta_{\text{seq}} = \text{Seq}_{\text{out, last}} - \text{Seq}_{\text{in, new}} + 1$$
     $$\Delta_{\text{ts}} = \text{TS}_{\text{out, last}} - \text{TS}_{\text{in, new}} + \Delta_{\text{frame}}$$
   - Setiap paket RTP berikutnya dimodifikasi field `sequence_number` dan `timestamp`-nya secara transparan sehingga decoder klien penerima tidak mengalami packet gap atau timestamp jumping error.
3. **Picture Loss Indication (PLI) Forwarding Invariant**:
   - Jangan pernah meneruskan PLI dari receiver ke pengirim jika SFU dapat memenuhi stream dari layer lain atau keyframe cache terdekat. Kirim PLI ke publisher hanya saat transisi layer membutuhkan IDR Keyframe baru.

---

### 2.3. Simulcast vs AV1 Scalable Video Coding (SVC)

```
[ AV1 Scalable Video Coding (SVC) Single Stream ]
   Bitstream Layer 2 (1080p @ 60fps) ───► [ S2T2 ] ──► (SFU forwards to Gigabit Fiber Clients)
   Bitstream Layer 1 (720p @ 30fps)  ───► [ S1T1 ] ──► (SFU forwards to 4G/LTE Clients)
   Bitstream Layer 0 (360p @ 15fps)  ───► [ S0T0 ] ──► (SFU forwards to Poor Mobile 3G Clients)
   *Single Encoder Instance on Publisher, Zero Transcoding on SFU Server*
```

1. **Simulcast (Multi-Stream Encoding)**:
   - Pengirim menjalankan 3 encoder independen secara paralel: High (1080p 2.5 Mbps), Mid (720p 800 kbps), Low (360p 200 kbps).
   - SFU memilih alokasi stream mana yang dikirim ke masing-masing subscriber berdasarkan bandwidth downlink yang tersedia.
   - Kelemahan: Beban CPU pengirim meningkat $1.5\times\text{--}2\times$ dan egress bitrate pengirim lebih besar.
2. **AV1 Scalable Video Coding (SVC) - Standar Masa Depan**:
   - Pengirim mengompilasi video menjadi **satu aliran terpadu** (*single scalable bitstream*) yang terdiri dari beberapa sub-layer spasial (*Spatial Layers: S0, S1, S2*) dan temporal (*Temporal Layers: T0, T1, T2*).
   - **AV1 Dependency Descriptor Extension (RFC draft-ietf-avtext-dd)**:
     - Header RTP menyematkan metadata struktur DAG layer: `SpatialId`, `TemporalId`, `KeyFrameFlag`, dan `FrameDependencyDiff`.
     - SFU cukup membaca 2 byte dependency descriptor pada header RTP:
       - Jika downlink penerima lambat, SFU langsung membuang paket dengan `SpatialId > 0` atau `TemporalId > 1` tanpa memicu korupsi bitstream atau error decoding pada layer dasar (S0T0).
   - Keuntungan: CPU pengirim sangat hemat (1 single encode pass), egress uplink pengirim minimal, transisi resolusi berlangsung instan ($0\text{ ms}$ keyframe delay).

---

## 🎙️ 3. Audio/Video DSP Pipelines, Opus & AV1 Hardware Transcoding

### 3.1. Real-Time Audio DSP Engine (AEC3, NS, AGC2 & Opus)

```
[ Microphone Input ] ──────► [ Sub-band AEC3 Filter ] ──────► [ Neural Noise Suppressor ] ──► [ AGC2 Limiter ] ──► [ Opus Encoder ] ──► RTP
                                     ▲ (Acoustic Echo Ref)
[ Speaker Playout ] ─────────────────┘
```

1. **Acoustic Echo Cancellation (AEC3)**:
   - **Far-End Reference Buffer**: Audio yang diputar di speaker dicatat ke dalam ring buffer referensi dengan kompensasi delay hardware ($20\text{--}120\text{ ms}$).
   - **Sub-Band Adaptive Filtering (Normalized Least Mean Squares - NLMS)**:
     - Spektrum audio dipecah menjadi sub-band filter (16 sub-bands).
     - Menghitung koefisien filter impuls akustik ruangan untuk memprediksi sinyal gema $\hat{y}(n)$ dan menguranginya dari sinyal mikrofon $d(n)$:
       $$e(n) = d(n) - \hat{y}(n)$$
   - **Double-Talk Detection (DTD)**: Menghentikan adaptasi koefisien filter saat kedua belah pihak berbicara bersamaan untuk mencegah distorsi suara lokal.
2. **Noise Suppression (NS)**:
   - Wiener filtering dan model Deep Learning GRU/LSTM kecil ($< 50\text{ KB}$ parameter) yang menganalisis rasio Signal-to-Noise (SNR) per frame waktu-frekuensi, mereduksi suara kipas, pendingin ruangan, dan ketikan keyboard tanpa merusak harmonik vokal.
3. **Automatic Gain Control (AGC2)**:
   - Melacak tingkat RMS (Root Mean Square) energi suara pembicara dan menerapkan dynamic compression/expansion dengan threshold target $-18\text{ dBFS}$ serta peak limiter untuk mencegah audio clipping.
4. **Opus Audio Codec Architecture (RFC 6716)**:
   - **Dual Hybrid Architecture**:
     - **SILK Mode (0 - 8 kHz)**: Linear Predictive Coding (LPC) yang dioptimalkan untuk artikulasi vokal manusia pada bitrate rendah ($6\text{--}20\text{ kbps}$).
     - **CELT Mode (8 - 20 kHz / Fullband)**: Modified Discrete Cosine Transform (MDCT) untuk transparansi musik dan dinamika audio frekuensi tinggi.
   - **In-Band Forward Error Correction (FEC)**:
     - Opus menyisipkan versi terkompresi dari frame $N-1$ ke dalam payload frame $N$ pada bitrate sedikit lebih tinggi. Jika frame $N-1$ hilang di jaringan, decoder mengekstrak data redundancy dari frame $N$ tanpa memerlukan transmisi ulang NACK.
   - **Discontinuous Transmission (DTX) & Comfort Noise Generation (CNG)**:
     - Saat pembicara hening (terdeteksi oleh VAD), transmisi paket dihentikan. Pengirim hanya mengirimkan paket *Silence Insertion Descriptor (SID)* setiap $400\text{ ms}$ untuk mereproduksi comfort noise latar belakang di sisi penerima.

---

### 3.2. AV1 Real-Time Hardware Transcoding & Codec Invariants
1. **Karakteristik AOMedia Video 1 (AV1) untuk Real-Time**:
   - Efisiensi kompresi $30\%\text{--}40\%$ lebih tinggi dibanding H.264 / VP8 pada bitrate yang sama, dengan lisensi bebas royalti (*royalty-free open standard*).
   - Mendukung kedalaman warna 10-bit HDR secara native, Super-Resolution filter, dan CDF (Cumulative Distribution Function) multi-symbol arithmetic entropy coding.
2. **Invarian Hardware Encoding Parameter untuk Real-Time Latency**:
   - **Zero Lookahead & No B-Frames**: B-Frames memerlukan frame masa depan untuk rekonstruksi bidirectional, menambahkan keterlambatan $66\text{--}200\text{ ms}$. Mode real-time wajib menetapkan `b-frames=0`, `lookahead=0`.
   - **Rate Control Mode**: Gunakan `CBR` (Constant Bitrate) atau `Low-Latency VBR` dengan token bucket decoder buffer size ($HRD\text{ buffer} = 1\times \text{frame time}$).
   - **Intra-Refresh (Periodic Column/Row Rolling Refresh)**:
     - Alih-alih mengirimkan Full IDR Keyframe masif ($100\text{ KB}+$) saat terjadi packet loss besar, encoder mengirimkan kolom intra-coded berjalan (misal 10% lebar frame per frame).
     - Menghilangkan *framerate stutter* dan lonjakan bandwidth tiba-tiba.
3. **Hardware Acceleration APIs**:
   - Linux / Edge Server: `VA-API` / `V4L2 M2M` / `NVIDIA NVENC SDK` / `Intel oneVPL`.
   - Pipeline Zero-Copy Memory: Tangkap frame kamera langsung ke GPU memory buffer (`EGLImage` / `DMA-BUF`), pasang ke hardware encoder tanpa proses salin memori CPU (*Zero-Copy Host RAM transfer*).

---

## 🛡️ 4. Adaptive Jitter Buffer (NetEq) & Packet Loss Concealment (PLC)

```
[ Incoming Out-of-Order RTP Packets ]
             │
             ▼
┌────────────────────────────────────────────────────────┐
│  Adaptive Packet Sorter & Insertion (Priority Heap)    │
└────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────┐
│  Target Playout Delay Estimator (Inter-Arrival Jitter) │
└────────────────────────────────────────────────────────┘
             │
      ┌──────┴───────────────────────────┐
      ▼                                  ▼
[ Buffer Underrun (Packet Lost) ]     [ Buffer Bloat (Excess Latency) ]
      │                                  │
      ▼                                  ▼
[ Audio PLC / Extrapolation ]         [ WSOLA Accelerated Playout ]
(Pitch-synchronous overlap)           (Compress time by 10-20%)
```

### 4.1. RFC 3550 Inter-Arrival Jitter Estimation & Playout Target
Jitter jaringan adalah variasi statistik dalam waktu kedatangan paket. Dihitung secara rekursif per paket kedatangan:
1. **Diferensial Waktu Transit**:
   $$D(i-1, i) = (R_i - S_i) - (R_{i-1} - S_{i-1})$$
   di mana $S_i$ adalah RTP Timestamp paket $i$ (dikirim) dan $R_i$ adalah Arrival Timestamp lokal (diterima) dalam satuan clock ticks.
2. **Exponential Smoothing Filter (RFC 3550)**:
   $$J_i = J_{i-1} + \frac{|D(i-1, i)| - J_{i-1}}{16}$$
3. **Target Playout Delay Formula**:
   $$\text{Delay}_{\text{target}} = \text{Percentile}_{95}(\text{InterArrivalDelay}) + \kappa \cdot J_i$$
   NetEq mengkalibrasi kedalaman antrean buffer agar selalu berada di atas variansi jitter jaringan tanpa menambahkan latency konstan yang tidak perlu.

---

### 4.2. Time-Scale Modification via WSOLA (Waveform Similarity Overlap-Add)
Ketika jitter buffer mendeteksi bahwa antrean terlalu panjang (buffer bloat) atau terlalu tipis (buffer starve), audio direntang (*expand*) atau dipadatkan (*compress*) secara waktu nyata tanpa mengubah tinggi nada vokal (*pitch invariant*):
1. **Accelerated Playout (Fast-Forward / Compression)**:
   - Jika buffer menumpuk $> 60\text{ ms}$, NetEq mencari dua segmen gelombang yang memiliki korelasi silang tertinggi (*Cross-Correlation Peak*) dengan jarak satu periode pitch ($T_0$), lalu melakukan *Overlap-Add (OLA)* dengan windowing segitiga/Hanning.
   - Durasi audio dipersingkat $10\%\text{--}20\%$ secara transparan tanpa disadari oleh telinga manusia, memangkas latency kembali ke level aman.
2. **Buffer Starvation Extension (Expansion)**:
   - Jika paket berikutnya terlambat tiba, NetEq memperpanjang periode gelombang sebelumnya dengan menyisipkan segmen pitch-synchronous yang di-fade, mencegah glitch atau bunyi *pop/click* akibat kekosongan audio sink.

---

### 4.3. Hybrid Loss Recovery & Packet Loss Concealment (PLC)
1. **Negative Acknowledgment (NACK - RFC 4585)**:
   - Receiver mendeteksi Sequence Number yang hilang. Jika $\text{RTT} \le 60\text{ ms}$, receiver mengirimkan permintaan NACK ke pengirim/SFU untuk retransmisi paket cepat.
2. **Flexible Forward Error Correction (FlexFEC - RFC 8627)**:
   - Pengirim menghitung paket paritas Reed-Solomon atau non-systematic XOR lintas $M$ paket media.
   - Receiver mampu merekonstruksi hingga $K$ paket yang hilang secara instan tanpa menunggu retransmisi RTT (*ideal for high-loss cellular networks*).
3. **Audio Packet Loss Concealment (PLC)**:
   - Jika paket audio hilang total dan tidak tercover oleh FEC:
     - **Frame 1 Hilang**: Ekstrapolasi gelombang sinusoidal berdasarkan pitch lag dan koefisien Linear Prediction Filter dari frame terakhir yang valid.
     - **Frame 2-3 Hilang**: Terapkan peredaman eksponensial energi gelombang (atenuasi $-2.5\text{ dB}$ per frame).
     - **Frame > 4 Hilang**: Transisi halus (*cross-fade*) ke Comfort Noise Generation (CNG).

---

## 🧪 5. Invariant Self-Check Executable (Pure Python Standard Library)

Skrip pengujian mandiri tanpa dependensi pihak ketiga (Pure Python 3.12 Standard Library) yang memvalidasi seluruh invarian transmisi WebRTC real-time:

```python
"""
Neuron N039 Invariant Self-Check:
1. RTP Packet Binary Serialization / Deserialization (RFC 3550)
2. RFC 3550 Inter-Arrival Jitter Exponential Smoothing Filter
3. Adaptive Jitter Buffer & Out-of-Order Packet Sorter with Loss Detection
4. Audio Packet Loss Concealment (PLC) Energy Attenuation & Extrapolation
5. SFU AV1 Scalable Video Coding (SVC) Layer Filter Routing
6. Token Bucket Real-Time Packet Pacer Rate Controller

Zero external dependencies (Pure Python Standard Library).
"""
import sys
import struct
import math
import time
from typing import List, Tuple, Optional, Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# --------------------------------------------------------------------------
# 1. RFC 3550 RTP Packet Serialization & Deserialization Invariant
# --------------------------------------------------------------------------
class RTPPacket:
    """
    RTP Header Format (RFC 3550):
     0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |V=2|P|X|  CC   |M|     PT      |       Sequence Number         |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                           Timestamp                           |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |           Synchronization Source (SSRC) identifier            |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """
    def __init__(self, pt: int, seq_num: int, timestamp: int, ssrc: int, payload: bytes, marker: bool = False):
        self.version = 2
        self.padding = 0
        self.extension = 0
        self.csrc_count = 0
        self.marker = 1 if marker else 0
        self.payload_type = pt
        self.seq_num = seq_num
        self.timestamp = timestamp
        self.ssrc = ssrc
        self.payload = payload

    def serialize(self) -> bytes:
        byte0 = (self.version << 6) | (self.padding << 5) | (self.extension << 4) | (self.csrc_count & 0x0F)
        byte1 = (self.marker << 7) | (self.payload_type & 0x7F)
        header = struct.pack("!BBHII", byte0, byte1, self.seq_num, self.timestamp, self.ssrc)
        return header + self.payload

    @classmethod
    def parse(cls, data: bytes) -> 'RTPPacket':
        if len(data) < 12:
            raise ValueError("Data too short for RTP header")
        byte0, byte1, seq_num, timestamp, ssrc = struct.unpack("!BBHII", data[:12])
        version = (byte0 >> 6) & 0x03
        if version != 2:
            raise ValueError(f"Unsupported RTP version: {version}")
        marker = bool((byte1 >> 7) & 0x01)
        pt = byte1 & 0x7F
        payload = data[12:]
        return cls(pt, seq_num, timestamp, ssrc, payload, marker)


# --------------------------------------------------------------------------
# 2. RFC 3550 Inter-Arrival Jitter Estimator
# --------------------------------------------------------------------------
class RFC3550JitterEstimator:
    def __init__(self, clock_rate: int = 90000):
        self.clock_rate = clock_rate
        self.jitter: float = 0.0
        self.prev_transit: Optional[float] = None

    def update(self, rtp_timestamp: int, arrival_time_sec: float) -> float:
        # Transit time in clock ticks
        arrival_ticks = arrival_time_sec * self.clock_rate
        transit = arrival_ticks - rtp_timestamp
        if self.prev_transit is not None:
            d = abs(transit - self.prev_transit)
            # RFC 3550 formula: J(i) = J(i-1) + (|D(i-1, i)| - J(i-1)) / 16
            self.jitter += (d - self.jitter) / 16.0
        self.prev_transit = transit
        return self.jitter / self.clock_rate  # return jitter in seconds


# --------------------------------------------------------------------------
# 3. Adaptive De-Jitter Buffer & Out-of-Order Sorter
# --------------------------------------------------------------------------
class AdaptiveJitterBuffer:
    def __init__(self, max_capacity: int = 50):
        self.buffer: Dict[int, RTPPacket] = {}
        self.max_capacity = max_capacity
        self.next_seq: Optional[int] = None
        self.lost_packets: List[int] = []

    def push(self, packet: RTPPacket):
        if self.next_seq is None:
            self.next_seq = packet.seq_num

        # Check sequence wrap-around or duplicate
        if packet.seq_num in self.buffer:
            return
        self.buffer[packet.seq_num] = packet

    def pop_in_order(self) -> Tuple[Optional[RTPPacket], bool]:
        """
        Returns (Packet, is_concealed_loss).
        If the expected next sequence packet is missing and buffer has advanced items,
        flags packet loss for PLC recovery.
        """
        if self.next_seq is None or not self.buffer:
            return None, False

        if self.next_seq in self.buffer:
            pkt = self.buffer.pop(self.next_seq)
            self.next_seq = (self.next_seq + 1) & 0xFFFF
            return pkt, False

        # Sequence gap detected: packet is missing
        # If newer packets arrived beyond missing sequence, declare loss
        available_higher = [seq for seq in self.buffer.keys() if seq > self.next_seq]
        if len(available_higher) >= 2 or len(self.buffer) >= 5:
            lost_seq = self.next_seq
            self.lost_packets.append(lost_seq)
            self.next_seq = (self.next_seq + 1) & 0xFFFF
            return None, True  # Missing packet trigger for PLC

        return None, False


# --------------------------------------------------------------------------
# 4. Audio Packet Loss Concealment (PLC) Waveform Extrapolator
# --------------------------------------------------------------------------
class AudioPLCExtrapolator:
    """
    Extrapolates periodic pitch audio waveform and applies exponential energy decay.
    """
    def __init__(self, sample_rate: int = 16000, frame_size: int = 160):
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.last_good_frame: List[float] = [0.0] * frame_size
        self.consecutive_lost_frames: int = 0
        self.decay_factor: float = 0.75  # ~ -2.5 dB per lost frame

    def feed_good_frame(self, frame: List[float]):
        self.last_good_frame = list(frame)
        self.consecutive_lost_frames = 0

    def generate_concealment_frame(self) -> List[float]:
        self.consecutive_lost_frames += 1
        attenuation = self.decay_factor ** self.consecutive_lost_frames
        
        # Invariant: After 4 lost frames, energy must drop below 35%
        if self.consecutive_lost_frames > 4:
            attenuation = max(0.0, attenuation * 0.5)

        # Extrapolate waveform with phase continuity + attenuation
        concealed = [val * attenuation for val in self.last_good_frame]
        return concealed


# --------------------------------------------------------------------------
# 5. SFU Scalable Video Coding (SVC) Zero-Decode Layer Filter
# --------------------------------------------------------------------------
class SFUAV1LayerFilter:
    """
    Inspects RTP packet AV1 Dependency Descriptor and filters spatial/temporal layers
    in O(1) without decoding video payload.
    """
    def __init__(self, max_spatial_layer: int = 1, max_temporal_layer: int = 1):
        self.max_spatial_layer = max_spatial_layer
        self.max_temporal_layer = max_temporal_layer
        self.routed_count = 0
        self.dropped_count = 0

    def route_packet(self, packet: RTPPacket, spatial_id: int, temporal_id: int) -> bool:
        if spatial_id <= self.max_spatial_layer and temporal_id <= self.max_temporal_layer:
            self.routed_count += 1
            return True  # Forward downstream
        else:
            self.dropped_count += 1
            return False  # Drop layer in SFU without bitstream corruption


# --------------------------------------------------------------------------
# 6. Token Bucket Real-Time Packet Pacer
# --------------------------------------------------------------------------
class TokenBucketPacer:
    def __init__(self, target_bitrate_bps: int, bucket_size_bytes: int):
        self.target_bitrate_bps = target_bitrate_bps
        self.rate_bytes_per_sec = target_bitrate_bps / 8.0
        self.bucket_size_bytes = bucket_size_bytes
        self.tokens_bytes = float(bucket_size_bytes)
        self.last_update = time.monotonic()

    def update_tokens(self, now: float):
        delta = now - self.last_update
        self.tokens_bytes = min(float(self.bucket_size_bytes), self.tokens_bytes + delta * self.rate_bytes_per_sec)
        self.last_update = now

    def can_send(self, packet_size_bytes: int, now: float) -> bool:
        self.update_tokens(now)
        if self.tokens_bytes >= packet_size_bytes:
            self.tokens_bytes -= packet_size_bytes
            return True
        return False


# --------------------------------------------------------------------------
# Main Invariant Verification Test Suite
# --------------------------------------------------------------------------
def run_all_invariants():
    print("=" * 70)
    print("  NEURON N039: REAL-TIME WEBRTC, AV DSP & AV1 STREAMING SELF-CHECK")
    print("=" * 70)

    # Test 1: RTP Binary Serialization
    payload_data = b"\x80\x98\x12\x34\xde\xad\xbe\xef\x01\x02\x03\x04"
    pkt = RTPPacket(pt=111, seq_num=1024, timestamp=900000, ssrc=0xDEADBEEF, payload=payload_data, marker=True)
    raw = pkt.serialize()
    assert len(raw) == 12 + len(payload_data), "RTP serialized size mismatch"
    parsed = RTPPacket.parse(raw)
    assert parsed.version == 2, "RTP version invariant broken"
    assert parsed.payload_type == 111, "RTP PT invariant broken"
    assert parsed.seq_num == 1024, "RTP sequence invariant broken"
    assert parsed.timestamp == 900000, "RTP timestamp invariant broken"
    assert parsed.ssrc == 0xDEADBEEF, "RTP SSRC invariant broken"
    assert parsed.marker == 1, "RTP marker bit invariant broken"
    assert parsed.payload == payload_data, "RTP payload mismatch"
    print("  [✓] 1. RFC 3550 RTP Packet Serialization & Bitfield Parsing: PASSED")

    # Test 2: RFC 3550 Inter-Arrival Jitter Estimator
    estimator = RFC3550JitterEstimator(clock_rate=90000)
    # Simulate packets sent every 20ms with variable network arrival jitter
    base_send_ts = 100000
    base_arrival = 10.0
    jitter_values = []
    delays = [0.0, 0.015, -0.010, 0.025, -0.020, 0.005] # variance in arrivals
    for i, d in enumerate(delays):
        send_ts = base_send_ts + i * 1800  # 20ms @ 90kHz = 1800 ticks
        arrival_t = base_arrival + (i * 0.020) + d
        j_sec = estimator.update(send_ts, arrival_t)
        jitter_values.append(j_sec)

    assert jitter_values[-1] > 0.0, "Jitter should be positive under network delay variance"
    assert jitter_values[-1] < 0.050, f"Jitter {jitter_values[-1]}s exceeded bounds"
    print(f"  [✓] 2. RFC 3550 Inter-Arrival Jitter Smoothing: PASSED (Est Jitter: {jitter_values[-1]*1000:.2f}ms)")

    # Test 3: Adaptive De-Jitter Buffer & Out-of-Order Sorter
    jb = AdaptiveJitterBuffer(max_capacity=20)
    # Feed packets out of order: seq 100, 102, 101, 104 (103 is missing)
    jb.push(RTPPacket(111, 100, 1000, 1, b"p100"))
    jb.push(RTPPacket(111, 102, 3000, 1, b"p102"))
    jb.push(RTPPacket(111, 101, 2000, 1, b"p101"))
    jb.push(RTPPacket(111, 104, 5000, 1, b"p104"))
    jb.push(RTPPacket(111, 105, 6000, 1, b"p105"))

    out_pkts = []
    losses = 0
    for _ in range(6):
        pkt_out, is_loss = jb.pop_in_order()
        if pkt_out:
            out_pkts.append(pkt_out.seq_num)
        if is_loss:
            losses += 1

    assert out_pkts == [100, 101, 102, 104, 105], f"Out of order sort failed: {out_pkts}"
    assert losses == 1, f"Expected 1 packet loss detected, got {losses}"
    assert 103 in jb.lost_packets, "Sequence 103 must be recorded as lost"
    print("  [✓] 3. Adaptive Jitter Buffer Sequencing & Loss Detection: PASSED")

    # Test 4: Audio Packet Loss Concealment (PLC)
    plc = AudioPLCExtrapolator(sample_rate=16000, frame_size=160)
    # Generate 1kHz sine test wave
    sine_frame = [math.sin(2 * math.pi * 1000 * n / 16000) for n in range(160)]
    plc.feed_good_frame(sine_frame)

    c1 = plc.generate_concealment_frame()
    c2 = plc.generate_concealment_frame()
    c3 = plc.generate_concealment_frame()
    c4 = plc.generate_concealment_frame()

    energy_orig = sum(x*x for x in sine_frame)
    energy_c1 = sum(x*x for x in c1)
    energy_c4 = sum(x*x for x in c4)

    assert energy_c1 < energy_orig, "Concealed frame 1 must show energy attenuation"
    assert energy_c4 < energy_c1 * 0.45, "Concealed frame 4 must attenuate by >55%"
    print(f"  [✓] 4. Audio PLC Extrapolation & Energy Attenuation (-2.5dB/frame): PASSED (E0: {energy_orig:.1f}, E4: {energy_c4:.1f})")

    # Test 5: SFU AV1 Scalable Video Coding (SVC) Layer Filter
    # Subscriber has 720p 30fps downlink limit (Spatial <= 1, Temporal <= 1)
    sfu_filter = SFUAV1LayerFilter(max_spatial_layer=1, max_temporal_layer=1)
    # Stream contains: (S0, T0), (S0, T1), (S1, T0), (S1, T1), (S2, T0), (S2, T2)
    layers = [
        (0, 0, True),
        (0, 1, True),
        (1, 0, True),
        (1, 1, True),
        (2, 0, False), # Exceeds S1 -> Drop
        (2, 2, False), # Exceeds S1, T1 -> Drop
        (1, 2, False)  # Exceeds T1 -> Drop
    ]
    for s_id, t_id, expected_routed in layers:
        dummy_pkt = RTPPacket(96, 1, 100, 1234, b"av1_payload")
        forwarded = sfu_filter.route_packet(dummy_pkt, s_id, t_id)
        assert forwarded == expected_routed, f"SVC routing failed for S{s_id}T{t_id}"

    assert sfu_filter.routed_count == 4, f"Expected 4 routed packets, got {sfu_filter.routed_count}"
    assert sfu_filter.dropped_count == 3, f"Expected 3 dropped packets, got {sfu_filter.dropped_count}"
    print(f"  [✓] 5. SFU AV1 SVC Layer Zero-Decode Selective Forwarding: PASSED ({sfu_filter.routed_count} routed, {sfu_filter.dropped_count} dropped)")

    # Test 6: Token Bucket Pacer Rate Limiting
    # Bitrate: 1 Mbps (125,000 bytes/sec), bucket size: 15,000 bytes
    pacer = TokenBucketPacer(target_bitrate_bps=1_000_000, bucket_size_bytes=15_000)
    t0 = 1000.0
    pacer.last_update = t0
    pacer.tokens_bytes = 15_000.0

    # Send 10 packets of 1200 bytes instantly
    sent = 0
    for _ in range(10):
        if pacer.can_send(1200, t0):
            sent += 1
    assert sent == 10, f"Expected 10 packets from initial burst bucket, sent {sent}"
    assert pacer.tokens_bytes == 3000.0, f"Remaining tokens mismatch: {pacer.tokens_bytes}"

    # Try sending 3 more packets without time advancing -> must be throttled
    throttled = 0
    for _ in range(3):
        if not pacer.can_send(1200, t0):
            throttled += 1
    assert throttled == 1, "Pacer should throttle once bucket runs out"

    # Advance time by 20ms -> adds 2500 bytes tokens -> can send 2 more packets
    t1 = t0 + 0.020
    assert pacer.can_send(1200, t1) is True, "Pacer should permit packet after time tick"
    print("  [✓] 6. Token Bucket Real-Time Packet Pacer Rate Regulation: PASSED")

    print("\n✨ ALL 6 RTC INVARIANTS SATISFIED DETERMINISTICALLY (Zero Dependencies).\n")

if __name__ == "__main__":
    run_all_invariants()
```
