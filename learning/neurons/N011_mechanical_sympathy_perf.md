# Neuron N011: Mechanical Sympathy & Zero-Copy Performance

Prinsip optimasi tingkat terdalam (Hardware-Aware Software Engineering):

---

## 1. CPU Cache Locality & Data-Oriented Design
- **L1/L2/L3 Cache Lines (64 Bytes)**: Mengelompokkan data dalam array kontinu (*Structure of Arrays vs Array of Structures*) untuk menghindari *Cache Miss* ($~200$ cycle CPU penalty).
- **Branch Prediction & Anti-Branching**: Menyusun logika kondisi hot-loop agar mudah diprediksi oleh CPU pipeline execution unit.

---

## 2. Zero-Copy I/O & Asynchronous Event Loops
- **Linux `sendfile` & `splice`**: Mengalirkan data file langsung dari disk cache ke network socket kernel tanpa menyalin ke memory user-space (kunci streaming Jellyfin instan).
- **Kernel Event Multiplexing (`epoll` / `io_uring`)**: Mengelola ratusan ribu socket I/O simultan tanpa membuat thread terpisah per koneksi.
- **Memory Pooling & Buffer Reuse**: Mencegah Garbage Collector pause dengan mendaur ulang ArrayBuffer dan Buffer pool pada Node.js/Rust.
