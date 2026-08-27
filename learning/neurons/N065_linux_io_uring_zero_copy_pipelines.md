# N065: Linux io_uring, Kernel Bypass eBPF XDP & Zero-Copy Pipelines

- **Kategori:** Systems Engineering & High-Performance I/O
- **Tanggal Sintesis:** 2026-08-27 11:54:22
- **Status:** Active Operational Invariant
- **Synaptic Links:** [`N011`](file:///D:/GEMINI-HANAFI/learning/neurons/N011_mechanical_sympathy_perf.md), [`N023`](file:///D:/GEMINI-HANAFI/learning/neurons/N023_zero_day_kernel_defense.md), [`N029`](file:///D:/GEMINI-HANAFI/learning/neurons/N029_modern_systems_rust_go.md), [`N061`](file:///D:/GEMINI-HANAFI/learning/neurons/N061_lock_free_concurrency_and_cache.md)

---

## 🎯 1. Core Engineering Invariants

### 1.1. io_uring Submission & Completion Queue (SQ/CQ) Ring Architecture
io_uring mengeliminasi syscall overhead dengan membagi dua lockless ring buffer di shared memory (mmap) antara userspace dan kernel:

```
+-----------------------------------------------------------------------------------+
| USER SPACE                                           KERNEL SPACE (SQPOLL Kernel) |
|  [SQ Entries Array]       [CQ Entries Array]           |                          |
|   - sqe[0], sqe[1]...      - cqe[0], cqe[1]...         |                          |
|         ^                        |                     |                          |
|  Tail ++ (Producer)        Head ++ (Consumer)          |                          |
|         |                        ^                     |                          |
|  +------v------------------------|---------------------+                          |
|  | SQ Ring: Head (Kernel) <-> Tail (User)              |                          |
|  | CQ Ring: Head (User)   <-> Tail (Kernel)            |                          |
|  +-----------------------------------------------------+                          |
+-----------------------------------------------------------------------------------+
```

1. **Lock-Free Ring Synchronization & Memory Ordering**:
   - **SQ (Submission Queue)**: User memutasi `sqes[tail & mask]`, lalu merilis pointer dengan `smp_store_release(sq_ring->tail, new_tail)`. Kernel membaca dengan `smp_load_acquire(sq_ring->tail)`.
   - **CQ (Completion Queue)**: Kernel menulis `cqes[tail & mask]`, mengupdate `cq_ring->tail` via release semantics. User membaca hingga `cq_ring->head != smp_load_acquire(cq_ring->tail)` dan memutasi head via `smp_store_release(cq_ring->head, new_head)`.
   - **Zero-Syscall Mode (`IORING_SETUP_SQPOLL`)**: Kernel thread (`io_uring-sq`) secara kontinu melakukan polling pada SQ ring. Jika tidak ada I/O baru setelah `sq_thread_idle` ms, thread tertidur dan user membangunkannya via flag `IORING_ENTER_SQ_WAKEUP`.
2. **Fixed Buffers & Registered Files (`IORING_REGISTER_BUFFERS` / `FILES`)**:
   - Buffer memory dipin dan dipetakan ke struct `io_uring` sekali di awal via `io_uring_register()`. Menghilangkan overhead `get_user_pages()` / `put_page()` dan page-table walking per I/O submission.
   - File descriptor didaftarkan ke kernel internal direct table untuk bypass lookup `fget()` / `fput()` dan spinlock table lock contention.

```c
// Invariant: Zero-Syscall Submission Loop (SQPOLL + Registered Buffers)
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read_fixed(sqe, fixed_fd_idx, buf_addr, buf_len, offset, buf_index);
sqe->flags |= IOSQE_FIXED_FILE;
// Commit submission to ring with release semantics
atomic_store_explicit((_Atomic unsigned *)ring.sq.ktail, ring.sq.sqe_tail, memory_order_release);
```

---

### 1.2. Kernel Bypass via eBPF XDP & AF_XDP (XSK) Zero-Copy
XDP mengeksekusi bytecode eBPF langsung pada Network Interface Card (NIC) driver ring sebelum alokasi kernel `sk_buff`:

$$\text{Throughput Limit: } \text{AF\_XDP Zero-Copy} \ge 24.5\text{ Mpps/core} \gg \text{Standard POSIX Socket} \approx 1.8\text{ Mpps/core}$$

1. **UMEM Shared Memory Architecture**:
   - Userspace mengalokasikan area memori contiguous 2MB/1GB HugePages (UMEM).
   - Terdiri dari 4 lock-free ring buffers:
     - **Fill Ring (Userspace $\to$ Kernel)**: Memberikan descriptor memory frame kosong ke kernel.
     - **Rx Ring (Kernel $\to$ Userspace)**: Mengirimkan paket yang diterima ke userspace.
     - **Tx Ring (Userspace $\to$ Kernel)**: Mengirimkan descriptor paket yang akan ditransmisikan.
     - **Completion Ring (Kernel $\to$ Userspace)**: Konfirmasi bahwa buffer TX telah selesai ditransmisikan oleh DMA NIC.
2. **eBPF XDP Driver Redirect (`XDP_REDIRECT`)**:
   - Driver menyalin paket langsung ke UMEM chunk via DMA tanpa alokasi `sk_buff` maupun interupsi stack TCP/IP OS (`bpf_redirect_map(&xsk_map, queue_id, XDP_PASS)`).

---

### 1.3. Zero-Copy Pipelines: `splice`, `sendfile`, & `MSG_ZEROCOPY`

```
Traditional:  [Disk] -(DMA)-> [Kernel Page Cache] -(CPU Copy)-> [User Buffer] -(CPU Copy)-> [Socket Buffer] -(DMA)-> [NIC]
Zero-Copy:    [Disk] -(DMA)-> [Kernel Page Cache] ======(Pipe Page Ref Swapping)======> [Socket Buffer] -(DMA)-> [NIC]
```

1. **Pipe Page Reference Transfer (`splice(2)`)**:
   - `splice` tidak menyalin byte data di CPU. Kernel hanya mentransfer referensi pointer `struct page*` di dalam `struct pipe_inode_info`.
   - Data mengalir langsung dari page cache storage ke socket buffer tanpa melintasi userspace memory boundary.
2. **Network Scatter-Gather Zero-Copy (`MSG_ZEROCOPY`)**:
   - Flag `send(fd, buf, len, MSG_ZEROCOPY)` menandai page user untuk langsung dipin dan di-DMA oleh hardware NIC.
   - **Notification Invariant**: User TIDAK BOLEH memodifikasi atau me-reuse buffer sampai menerima `SO_EE_ORIGIN_ZEROCOPY` notification completion dari socket error queue (`recvmsg(fd, &msg, MSG_ERRQUEUE)`).

---

### 1.4. Mirror-Mapped Virtual Memory Circular Ring Buffer
Menghilangkan modulo branch instruction (`index % capacity`) dan buffer wrap-around checks dengan memetakan physical memory chunk yang sama dua kali secara contiguous di virtual address space:

```c
// Invariant: Contiguous wrap-around virtual memory mapping
int fd = memfd_create("ring_buf", MFD_CLOEXEC);
ftruncate(fd, buffer_size); // buffer_size must be multiple of page size
void *addr = mmap(NULL, buffer_size * 2, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
mmap(addr, buffer_size, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_FIXED, fd, 0);
mmap((char*)addr + buffer_size, buffer_size, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_FIXED, fd, 0);
// Address range [addr, addr + 2*buffer_size) can now be read/written continuously
// without handling wrap-around splits across buffer boundaries.
```

---

## 🔍 2. Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Invariant Defense / Guard |
| :--- | :--- | :--- |
| **Short Writes / Reads under io_uring** | Asynchronous non-blocking file/socket descriptor mengembalikan partial size saat pipe/socket buffer penuh. | Wajib menggunakan flag `IOSQE_ASYNC` atau loop consumption dengan offset accumulator hingga byte habis. |
| **Memory Corruption on `MSG_ZEROCOPY`** | Userspace thread memodifikasi buffer payload saat DMA transfer NIC masih aktif di background. | Buffer di-freeze ke state read-only sampai `SO_EE_CODE_ZEROCOPY_COPIED` completion diproses dari `MSG_ERRQUEUE`. |
| **`ENOMEM` on `io_uring_register`** | Kernel `RLIMIT_MEMLOCK` terlalu rendah untuk menampung fixed buffer pinning. | Naikkan `prlimit(RLIMIT_MEMLOCK, RLIM_INFINITY)` sebelum inisialisasi runtime buffer pool. |
| **Cache Line Bouncing / False Sharing** | SQ Head/Tail dan CQ Head/Tail berada di cache line 64-byte yang sama. | io_uring mendesain offset ring header pada cache line terpisah (`alignas(64)` / separate pages). |

---

## 🛡️ 3. Edge Case Invariants

1. **CQ Overflow (`IORING_FEAT_NODROP` & `IORING_SQ_CQ_OVERFLOW`)**:
   - Jika SQ submissions jauh melebihi laju konsumsi CQ, event completion ditahan di internal kernel list. Pastikan queue depth CQ setidaknya berukuran $2 \times \text{SQ Depth}$ (`io_uring_params.cq_entries`).
2. **Order Preservation via Linked SQEs (`IOSQE_IO_LINK`)**:
   - Operasi dependen (misal `write` lalu `fsync`, atau `splice` sequential) wajib dihubungkan dengan flag `IOSQE_IO_LINK`. Jika head SQE gagal, seluruh linked chain dibatalkan dengan error `-ECANCELED`.

---

## 🔒 4. Execution Discipline

- **Ponytail YAGNI**: Jangan gunakan eBPF XDP / io_uring jika throughput requirement $< 100\text{k RPS}$; gunakan standard epoll/Tokio I/O loop.
- **Single Root Fix**: Tangani bottlenecks I/O langsung pada level syscall & page pinning abstraction, bukan menambah thread pool concurrency.
- **Zero-Allocation**: Buffer ring harus dialokasikan secara statis di awal lifecycle aplikasi (pre-allocated pool).
- **Line Limit Check**: File ini dikunci di bawah 300 baris markdown untuk menjaga kepadatan informasi operasional.
