# N066: WASI Preview 2, WASM Component Model & Tokio Scheduler Internals

- **Kategori:** Systems Architecture, Asynchronous Runtimes & WASM Sandboxing
- **Tanggal Sintesis:** 2026-08-27 11:54:22
- **Status:** Active Operational Invariant
- **Synaptic Links:** [`N011`](file:///D:/GEMINI-HANAFI/learning/neurons/N011_mechanical_sympathy_perf.md), [`N029`](file:///D:/GEMINI-HANAFI/learning/neurons/N029_modern_systems_rust_go.md), [`N037`](file:///D:/GEMINI-HANAFI/learning/neurons/N037_wasm_wasi_microvm_sandboxing.md), [`N061`](file:///D:/GEMINI-HANAFI/learning/neurons/N061_lock_free_concurrency_and_cache.md)

---

## 🎯 1. Core Engineering Invariants

### 1.1. WASM Component Model & WASI Preview 2 (WASI 0.2)
WASI Preview 2 menggantikan POSIX syscall interface mentah dengan **Wasm Interface Type (WIT)** dan **Canonical ABI** typed resource handles:

```
+-----------------------------------------------------------------------------------+
| Guest Component (Rust / Wasm)                                                     |
|  [WIT Interface: wasi:http/incoming-handler, wasi:io/streams, wasi:cli]          |
|         |                                                             ^           |
|  1. Canonical Lowering (Typed Struct -> Flat Linear Memory)           | 4. Lifting|
|         v                                                             |           |
|  +--------------------------------------------------------------------+--------+  |
|  | Host Runtime Engine (Wasmtime / Tokio Async Driver)                         |  |
|  |   - Resource Table: Granular Handles (own<stream>, borrow<tcp-socket>)     |  |
|  |   - Zero Ambient Authority: Explicit capability capability-passing only    |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

1. **Canonical ABI Memory Rules**:
   - **Lowering**: Mengonversi high-level data types (strings, records, variants) menjadi flat primitive representation (`i32`, `i64`, `f32`, `f64`) untuk dilewatkan melalui stack register WASM.
   - **Lifting**: Mengonversi flat primitive representation kembali ke high-level types di memory boundary sisi penerima.
   - **Resource Types (`own<T>` / `borrow<T>`)**: Handle 32-bit integer yang dipetakan ke host table index dengan reference counting otomatis (`[resource-drop]`).
2. **Zero Ambient Authority**:
   - Guest tidak memiliki akses default ke network, filesystem, env vars, atau high-res clock. Akses hanya diberikan via inject explicit resource token saat runtime instantiation.

---

### 1.2. Deterministic Fuel Metering & Memory Sandboxing
Eksekusi untrusted code dibatasi secara deterministik dengan injeksi instruksi penghitung bahan bakar (*fuel*) pada setiap basic block:

$$\text{Fuel}_{\text{remaining}} = \text{Fuel}_{\text{initial}} - \sum_{i=1}^{N} \text{Cost}(\text{block}_i), \quad \text{Trap if } \text{Fuel}_{\text{remaining}} < 0$$

1. **Basic Block Fuel Injection (Cranelift)**:
   - Kompiler JIT menyisipkan instruksi pengurangan fuel di awal setiap header basic block loop/branch, mencegah infinite loop DoS.
2. **Epoch Interruption vs Fuel**:
   - **Fuel**: Bersifat $100\%$ deterministik (jumlah instruksi identik per eksekusi). Digunakan untuk consensus/billing.
   - **Epoch**: Timer asinkron berbasis interval epoch ticks di thread pool Tokio (`engine.increment_epoch()`). Digunakan untuk timeout wall-clock dengan zero instruction overhead.

```rust
// Invariant: Deterministic Fuel & Memory Quota
let mut config = Config::new();
config.consume_fuel(true);
config.static_memory_maximum_size(64 * 1024 * 1024); // 64MB hard limit
let mut store = Store::new(&engine, ());
store.set_fuel(5_000_000)?; // 5M CPU instruction budget
```

---

### 1.3. Tokio 2024 Multi-Threaded Work-Stealing Scheduler
Arsitektur runtime multi-threaded Tokio mendistribusikan task asynchronous ke worker threads tanpa lock contention global:

```
+-----------------------------------------------------------------------------------+
| Global Injector Queue (Lock-Free MPMC / SegQueue)                                 |
+-----------------------------------------------------------------------------------+
        | (Check every 61 ticks)                                  ^
        v                                                         | Push on local full
+------------------------------------+  Steal 50%  +------------------------------------+
| Worker Thread 0                    | <========== | Worker Thread 1                    |
|  - LIFO Slot: Task (Locality)      | (Atomic CAS)|  - LIFO Slot: Task (Locality)      |
|  - Local RunQueue: 256-slot ring   |             |  - Local RunQueue: 256-slot ring   |
+------------------------------------+             +------------------------------------+
```

1. **Hierarchical Task Resolution (Search Order)**:
   - **LIFO Slot**: Task yang baru terbangun diperiksa pertama kali untuk memaksimalkan cache locality L1/L2.
   - **Local Run Queue (256-slot circular array)**: Eksekusi task lokal tanpa lock antar thread.
   - **Global Injector Queue**: Diperiksa setiap **61 tick** untuk mencegah kelaparan (*starvation*) task global.
   - **Work-Stealing**: Jika queue lokal kosong, curi $\lceil N_{\text{victim}}/2 \rceil$ task dari queue worker lain via atomic CAS operation.
2. **Cooperative Budget Invariant (`consume_budget`)**:
   - Setiap task memiliki alokasi budget **128 polls**. Task yang melakukan loop tak berhingga secara otomatis dipaksa yield (`tokio::task::yield_now().await`) agar task lain mendapatkan jatah core.

---

### 1.4. Cancellation Safety & Async Drop Invariants
Dalam Rust `Future`, pembatalan (*cancellation*) terjadi seketika saat future didrop (`Drop`) di tengah eksekusi (contoh: pada `tokio::select!` branch yang kalah):

```rust
// HAZARD: Non-Cancellation-Safe Operation
tokio::select! {
    res = socket.read_exact(&mut buf) => { /* If canceled, partially read bytes are lost forever */ }
    _ = timeout => { /* Timeout triggered, socket stream is now corrupted */ }
}

// INVARIANT: Cancellation-Safe Design via Framed Buffers
let mut framed = FramedRead::new(socket, LengthDelimitedCodec::new());
tokio::select! {
    frame = framed.next() => { /* Safe: framed decoder buffers partial state across polls */ }
    _ = timeout => { /* Safe: internal buffer preserved in framed object */ }
}
```

1. **Cancellation Safety Rules**:
   - Operasi aman dibatalkan jika `poll()` dapat diinterupsi dan di-drop tanpa meninggalkan data korup atau setengah termutasi.
   - **Unsafe Operations**: `AsyncReadExt::read_exact`, mutex lock release across await points, multi-step non-atomic channel state modifications.
   - **Mitigasi**: Simpan parser state di luar loop `select!`, gunakan message-passing transaction channel, atau spawn task independen (`tokio::spawn`) yang didorong hingga tuntas.

---

### 1.5. Lock-Free SPSC Barriers between WASM & Host Loop
Menghubungkan event loop WASM linear memory dengan thread pool Tokio tanpa blocking mutex:

```rust
#[repr(align(64))]
pub struct SpscRing<T, const CAP: usize> {
    head: std::sync::atomic::AtomicUsize, // Written by Consumer, Read by Producer
    _pad0: [u8; 56],
    tail: std::sync::atomic::AtomicUsize, // Written by Producer, Read by Consumer
    _pad1: [u8; 56],
    buffer: [std::cell::UnsafeCell<Option<T>>; CAP],
}
// Invariant: Producer stores with Release, Consumer loads with Acquire.
// Cache lines 64-byte isolated to eliminate cross-core false sharing.
```

---

## 🔍 2. Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Invariant Defense / Guard |
| :--- | :--- | :--- |
| **Worker Thread Starvation / Deadlock** | Menjalankan blocking call (e.g. `std::fs`, `std::thread::sleep`, sync mutex) di worker Tokio. | Wajib menggunakan `tokio::task::spawn_blocking` atau IO non-blocking murni. |
| **Data Corruption on `select!` Drop** | Future yang menahan buffer transisi di-drop di tengah jalan saat branch lain selesai. | Gunakan framing codec (`tokio_util::codec`) yang menyimpan residual buffer secara permanen. |
| **WASM Out-Of-Fuel Hang** | Host lupa menyetel fuel refill atau epoch tick tidak di-advance secara teratur di timer loop. | Injeksi dedicated ticker thread `tokio::spawn(async move { loop { sleep(10ms); engine.increment_epoch(); } })`. |
| **WASM Memory Leak across Executions** | Linear memory instans tidak di-reset / pooling allocator kotor setelah plugin trap. | Gunakan `PoolingAllocationConfig` dengan explicit `store.gc()` dan memori recycle per invocations. |

---

## 🛡️ 3. Edge Case Invariants

1. **Async Drop Limitation**:
   - Rust tidak memiliki asynchronous destructor (`async Drop`). Jika cleanup membutuhkan I/O jaringan/disk, kirim event cleanup ke background channel (`mpsc::unbounded_channel`) sebelum drop.
2. **Recursive WIT Interface Nesting**:
   - Hindari nested type depth $> 16$ pada parameter WIT Canonical ABI untuk mencegah stack overflow saat lifting/lowering pointer translation.

---

## 🔒 4. Execution Discipline

- **Ponytail YAGNI**: Jangan gunakan WASM Sandboxing jika hanya mengeksekusi trusted internal services; gunakan static dynamic linking biasa.
- **Single Root Fix**: Perbaiki problem konkurensi pada level future state machine & scheduling budget, bukan menambah ukuran worker thread pool.
- **Line Limit Check**: File ini dirancang padat dan strictly di bawah 300 baris markdown.
