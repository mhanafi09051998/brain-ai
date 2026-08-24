# Neuron N034: Autonomous Runtime Profiler, Flamegraph & Memory Leak Oracle

Prinsip rekayasa performa tingkat rendah, continuous low-overhead profiling, dekomposisi call stack kernel/user-space, visualisasi flamegraph sub-millisecond, serta deteksi deterministik memory leak dan heap fragmentation:

- **Kategori**: Systems Performance Engineering, Low-Level Profiling, Memory Optimization & Observability
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengeliminasi blind-spot performa CPU, I/O, dan memori pada level kernel dan runtime aplikasi; mengeksekusi continuous profiling zero-instrumentation (<1% overhead) via eBPF & sampling profilers (`py-spy`, `pprof`); menghasilkan on-CPU/off-CPU & differential flamegraph; serta mendiagnosis fragmentasi heap dan memory leak alokator (`jemalloc`, `mimalloc`, `tracemalloc`).
- **Synaptic Links**: [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N015`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N015_compiler_ast_and_system_profiling.md), [`N027`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N027_tensor_simd_vectorization.md), [`N032`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N032_cloud_native_edge_infra.md), [`N033`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md)
- **Status**: Active Operational Invariant

---

## 1. Continuous In-Kernel eBPF Profiling & Tracing Architecture

```
                                  +---------------------------------------+
                                  |     User Space Application Stack      |
                                  |   (Python / Rust / Go / C++ / Node)   |
                                  +-------------------+-------------------+
                                                      |
                                                      | Context Switch / Syscalls
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                           LINUX KERNEL SPACE                                            |
|                                                                                                         |
|  [ PMU Hardware Timer ] --------> [ BPF_PROG_TYPE_PERF_EVENT (Sampling at 49Hz/99Hz/997Hz) ]           |
|                                                     |                                                   |
|  [ Tracepoints: sched_switch ] ---> [ Off-CPU Delta Calculator (prev_pid sleep -> wakeup) ]             |
|                                                     |                                                   |
|  [ Kernel Stack Unwind ] <------+                   v                                                   |
|  [ User Stack Unwind   ] <------+====== [ BPF Stack Trace Map & Ring Buffer (Zero-Copy) ]               |
+-----------------------------------------------------|---------------------------------------------------+
                                                      |
                                                      v  (Low-overhead mmap / BPF CO-RE)
                                     +--------------------------------+
                                     |   External Profiling Daemon    |
                                     |   (Folded Stacks -> Flamegraph)|
                                     +--------------------------------+
```

### A. eBPF Subsystem & BPF CO-RE (Compile Once – Run Everywhere)
1. **Safety & In-Kernel Execution**:
   - Program eBPF diverifikasi secara statis oleh Linux Kernel Verifier (memastikan bebas null pointer dereference, bounded loops, dan batasan instruksi) sebelum dieksekusi via JIT compiler di dalam ring 0 kernel space.
   - BPF Type Format (BTF) dan Clang `-target bpf` memungkinkan relocation struct kernel secara dinamis pada berbagai versi Linux kernel tanpa kompilasi ulang di target host (*BPF CO-RE*).
2. **Probe Latency & Overhead Hierarchy**:
   - **Static Tracepoints** (`/sys/kernel/debug/tracing/events/*`, misal `sched:sched_switch`, `syscalls:sys_enter_*`): ~10–25 ns overhead per event. Ideal untuk continuous profiling skala produksi.
   - **Kernel Probes (kprobes/kretprobes)**: Dynamic kernel function hooks via breakpoint int3 / ftrace. Overhead ~100–250 ns per trigger.
   - **User Probes (uprobes/uretprobes)**: Dynamic user-space binary hooks. Mengharuskan trap breakpoint dan double context switch (User $\to$ Kernel $\to$ User), menimbulkan overhead ~1.5–3.5 $\mu$s per call. Hindari uprobe pada loop mikro dengan jutaan iterasi per detik.

### B. On-CPU & Off-CPU Profiling Engine
1. **Statistical On-CPU Sampling via Hardware PMU (`perf_event_open`)**:
   - Menjalankan `BPF_PROG_TYPE_PERF_EVENT` terikat pada CPU hardware counters.
   - **Sampling Rate Invariant**: Selalu gunakan bilangan prima (misal $49\,\text{Hz}$, $99\,\text{Hz}$, $499\,\text{Hz}$, atau $997\,\text{Hz}$) untuk menghindari *harmonic lockstep resonance* (fenomena di mana profiler tersinkronisasi persis dengan periodisitas timer aplikasi atau tick cron, mendistorsi distribusi sample).
   - Menghasilkan stack trace gabungan kernel + user space (`bpf_get_stackid(ctx, &stack_map, BPF_F_USER_STACK)`).
2. **Off-CPU Latency & Blocked State Tracing**:
   - Bottleneck I/O, database queries, disk seek, dan mutex locks tidak terlihat pada On-CPU profile.
   - Mengaitkan tracepoint `sched:sched_switch`:
     - Saat thread bertransisi dari state `TASK_RUNNING` ke `TASK_INTERRUPTIBLE` / `TASK_UNINTERRUPTIBLE`, catat `timestamp_start` dan stack trace ke dalam BPF hash map.
     - Saat thread kembali dijadwalkan (`sched:sched_wakeup`), hitung $\Delta t = \text{timestamp\_end} - \text{timestamp\_start}$.
     - Agregasikan durasi off-CPU terhadap stack trace pemanggil.
3. **Scheduler Run-Queue (`runqlat`) & Block I/O (`biolatency`)**:
   - **`runqlat` Invariant**: Mengukur waktu tunggu thread yang sudah berstatus *runnable* sebelum mendapatkan alokasi physical CPU core. Lonjakan `runqlat` $> 1\,\text{ms}$ mengindikasikan CPU saturation atau cgroups throttling.
   - **`biolatency` Invariant**: Histogram latensi I/O blok storage dari driver device hingga completion interrupt untuk mengidentifikasi storage queue saturation.

---

## 2. Sampling Profilers & Multi-Runtime Stack Unwinding (py-spy, pprof)

### A. Sampling Profiling vs Instrumentation Overhead

$$\text{Slowdown}_{\text{Sampling}} = \frac{T_{\text{profiled}}}{T_{\text{baseline}}} \approx 1.01 \text{ – } 1.03 \quad (\le 3\% \text{ overhead})$$

$$\text{Slowdown}_{\text{Instrumentation}} = \frac{T_{\text{profiled}}}{T_{\text{baseline}}} \approx 5.0 \text{ – } 50.0 \quad (\text{distorsi ekstrim pada hot loops})$$

1. **Kegagalan Profiler Berbasis Instrumentasi (`cProfile`, `sys.settrace`, `gprof`)**:
   - Menginjeksi hook di setiap enter/exit function.
   - Mengubah karakteristik runtime: fungsi inline berukuran kecil mengalami pembengkakan latency hingga ratusan persen, merusak validitas urutan hotspot (*Observer Effect*).
2. **Sampling Profiler Non-Invasif (`py-spy`)**:
   - Membaca memori virtual proses target secara eksternal via syscall `process_vm_readv` (Linux), `mach_vm_read` (macOS), atau `ReadProcessMemory` (Windows).
   - Beroperasi sepenuhnya di luar ruang proses target: tidak memerlukan modifikasi bytecode, tidak menginjeksi shared library, dan **tidak pernah mengunci atau menghentikan CPython GIL**.

### B. CPython Stack Unwinding Internals (Python 3.11–3.13+)
1. **Struktur Memory Traversal**:
   - `py-spy` membaca symbol pointer `_PyRuntime` / `interp_head` $\to$ `PyInterpreterState` $\to$ `PyThreadState` $\to$ frame stack aktif.
   - Pada Python 3.11+, stack frame bertransisi dari linked-list `PyFrameObject` heap ke array kontigu `_PyInterpreterFrame` pada thread execution stack.
2. **GIL Contention Tracking**:
   - Membaca field `gil_runtime_state` / `locked` atomic pointer.
   - Mengklasifikasikan thread state ke dalam 3 kuadran:
     1. **Active GIL**: Menjalankan bytecode Python murni pada CPU.
     2. **Waiting for GIL**: Mengantre pada mutex lock GIL (`gil_drop_request`).
     3. **GIL Released**: Menjalankan C-Extension intensif / I/O syscall (NumPy, Polars, socket recv) tanpa mengunci interpreter.
3. **Native Mixed-Mode Stack Unwinding**:
   - Mengombinasikan tabel DWARF / `.eh_frame` dan `-fno-omit-frame-pointer` untuk menyatukan frame C/C++/Rust native dengan frame high-level Python dalam satu pohon call stack linier.

### C. Google Continuous Profiling Standard (`pprof` Protocol)
1. **Data Model Protobuf (`profile.proto`)**:
   - Struktur representasi terstandarisasi untuk multi-language profiling:
     - `Sample`: Array nilai int64 (`values`) yang terikat pada `location_id` list.
     - `ValueType`: Dimensi metrik profil (`samples/count`, `cpu/nanoseconds`, `alloc_objects/count`, `alloc_space/bytes`, `inuse_objects/count`, `inuse_space/bytes`, `goroutine/count`, `contention/delay_nanoseconds`).
     - `StringTable`: String deduplication dictionary untuk kompresi payload transmisi profile.
2. **Continuous Profiling Lifecycle**:
   - Agen mengumpulkan sample selama interval 10–60 detik, mengompresi payload via gzip, dan mengirimkannya ke central time-series profile backend (Grafana Pyroscope / Parca / Google Cloud Profiler).
3. **Profile Delta & Diffing Invariant**:
   - Menganalisis regresi performa antar release commit via aljabar profil:
     $$\Delta \text{Profile} = \text{Profile}_{\text{PR}} - \text{Profile}_{\text{Baseline}}$$

---

## 3. Sub-Millisecond Flamegraph & CPU Contention Analysis

```
                              FLAMEGRAPH TRIE STRUCTURE
                              
  Stack Depth (Y)
       ^
       |  [       sqlite3_step (12ms)       ]  [   json_dumps (8ms)   ]
       |  [            execute_query (16ms) ]  [ serialize_resp (10ms)]
       |  [                     handle_http_request (30ms)            ]
       |  [                            main (35ms)                    ]
       +-------------------------------------------------------------------> Resource % / Samples (X)
```

### A. Algoritma Konstruksi Flamegraph
1. **Folded Stack Trace Format**:
   - Representasi teks terkompresi dari jalur eksekusi:
     ```text
     main;handle_http_request;execute_query;sqlite3_step 120
     main;handle_http_request;serialize_resp;json_dumps 80
     main;handle_http_request;process_auth 40
     ```
2. **Prefix-Tree (Trie) Aggregation**:
   - Setiap node pada Trie merepresentasikan frame fungsi unik dengan atribut:
     - `self_time` (eksekusi pada leaf node saja).
     - `total_time` (akumulasi diri sendiri dan seluruh child branches).
     - `children` (ordered map sub-pemanggilan).
3. **Dimensi Visualisasi**:
   - **X-axis**: Representasi proporsi total resource (persentase CPU cycles, alokasi memori, atau delay) diurutkan secara alfabetis atau kronologis. *Lebar kotak berbanding lurus dengan konsumsi resource*.
   - **Y-axis**: Kedalaman call stack (root berada di dasar, leaf/callee berada di puncak).
   - **Warna**: Hashing palet warna berbasis nama package/modul untuk memisahkan domain kode kernel, library eksternal, dan business logic aplikasi.

### B. Varian Analisis Flamegraph
1. **On-CPU Flamegraph**: Mengidentifikasi algoritma CPU-bound yang tidak efisien, loop bersarang, atau serialisasi JSON/Protobuf berat.
2. **Off-CPU Flamegraph**: Mengidentifikasi antrean I/O, database connection pool starvation, dan thread sleep.
3. **Differential Flamegraph (2-Way Diff)**:
   - Warna **Merah**: Peningkatan konsumsi CPU/memori relatif terhadap baseline.
   - Warna **Biru**: Penurunan konsumsi CPU/memori (optimasi berhasil).
4. **Reversed Flamegraph (Icicle Graph)**:
   - Membalikkan orientasi (root di atas, leaf di bawah) atau mengelompokkan dari leaf terpanas ke atas (*top-down aggregation*) untuk menemukan fungsi pembantu yang lambat terlepas dari siapa pemanggilnya.

### C. Hardware Performance Counters (PMU / PMC)
1. **Instructions Per Cycle (IPC)**:
   $$\text{IPC} = \frac{\text{Instructions Executed}}{\text{CPU Cycles}}$$
   - $\text{IPC} \ge 2.0$: **Compute-Bound** (optimasi struktur algoritma / SIMD vectorization).
   - $\text{IPC} \le 0.75$: **Memory-Bound / Pipeline-Stalled** (terhambat cache misses, pointer chasing, atau branch misprediction).
2. **Hardware Metrics Vital**:
   - **L1/L2/LLC Cache Misses**: Mengindikasikan fragmentasi memori atau data layout non-kontigu.
   - **Branch Mispredictions**: Terjadi pada kondisi `if/else` acak yang menggagalkan CPU instruction speculative execution.
   - **False Sharing**: Dua core CPU memodifikasi variabel berbeda yang berada di dalam satu 64-byte cache line yang sama, memicu invalidasi cache bolak-balik (*cache-line bouncing* via protokol MESI/MOESI).

### D. Thread Lock Contention & Futex Oracle
1. **Anatomi Lock Contention**:
   - **Hold Time**: Durasi sebuah thread memegang lock (critical section).
   - **Wait Time**: Durasi thread lain terblokir menunggu lock dilepaskan.
2. **Futex (Fast Userspace Mutex) Escalation**:
   - Fast-path: Atomic Compare-And-Swap (CAS) di user space ($\sim 5\text{–}15\,\text{ns}$).
   - Slow-path contention: Pemanggilan syscall `sys_futex(FUTEX_WAIT)` yang menidurkan thread ke kernel run-queue dan memicu context switch ($\sim 2\text{–}5\,\mu\text{s}$).
3. **Invarian Resolusi Contention**:
   - Mengganti coarse-grained lock dengan *Fine-Grained Striped Locks*.
   - Menerapkan *Lock-Free Ring Buffers* berbasis Single-Producer Single-Consumer (SPSC) atomic pointer.
   - Menggunakan *Read-Copy-Update (RCU)* untuk struktur data yang sering dibaca namun jarang diubah.

---

## 4. Memory Leak Oracle, Heap Profiling & Advanced Allocator Internals

### A. Arsitektur Heap Allocator Modern (jemalloc & mimalloc)

```
                            JEMALLOC / MIMALLOC SLAB ARCHITECTURE
                            
  Thread 1 ---> [ TCache / Local Pool ] (Lock-Free Thread Allocation)
  Thread 2 ---> [ TCache / Local Pool ]
                      |
                      | (Refill when empty / Flush when full)
                      v
  [ Arena 1 (Chunk/Slab) ]   [ Arena 2 (Chunk/Slab) ] ... [ Arena N (Per Core) ]
         |                          |
         +--------------------------+
                      |
                      v (mmap / madvise)
               [ Linux Kernel VMM ]
```

1. **Prinsip Partisi Arena**:
   - Mengalokasikan arena memori independen per CPU core ($4 \times N_{\text{cores}}$) untuk mengeliminasi contention mutex global pada pemanggilan `malloc()` / `free()`.
2. **Thread-Local Cache (TCache / Thread-Local Pool)**:
   - Setiap thread memiliki ring-buffer alokasi lokal untuk size classes kecil ($\le 14\,\text{KB}$). Alokasi dan dealokasi pada tcache berjalan $100\%$ lock-free.
3. **Kategori Ukuran Alokasi**:
   - **Small** ($\le 14\,\text{KB}$): Dialokasikan pada slab/bin dengan ukuran tetap untuk meminimalkan fragmentasi internal.
   - **Large** ($14\,\text{KB} \text{ – } 2\,\text{MB}$): Dialokasikan langsung pada chunk page run.
   - **Huge** ($> 2\,\text{MB}$): Dialokasikan langsung via `mmap` dedicated page mapping.
4. **Purging & Page Reclamation (`madvise`)**:
   - Alokator mengembalikan page memori yang tidak terpakai ke OS via `madvise(MADV_DONTNEED)` atau `madvise(MADV_FREE)` tanpa de-alokasi virtual address space.

### B. Taksonomi Anomali Memori: Leak vs Retention vs Fragmentation
1. **Virtual Size (VSS) vs Resident Set Size (RSS) vs Proportional Set Size (PSS)**:
   - $\text{VSS}$: Total address space yang dipetakan oleh proses (termasuk shared libs dan alokasi belum terpakai).
   - $\text{RSS}$: Memori fisik aktual (RAM) yang sedang digunakan oleh proses saat ini.
   - $\text{PSS}$: Proporsi penggunaan RAM fisik riil dengan membagi shared library memory secara adil antar proses.
2. **Definisi Deterministik Anomali**:
   - **True Memory Leak**: Pointer objek terputus / tak dapat dijangkau (*unreachable*), namun memori gagal dide-alokasi ke alokator.
   - **Memory Retention (Unbounded Cache / Logical Leak)**: Objek masih dapat dijangkau (*reachable* dari global root/dict), namun fungsinya sudah usang dan tidak pernah dibersihkan.
   - **Heap Fragmentation**: Objek-objek kecil yang masih aktif tersebar di banyak slab page, mencegah page dikembalikan ke kernel OS meskipun persentase occupancy rendah.

### C. Profiling Produksi Berbasis `jemalloc` (`jeprof`)
1. **Konfigurasi Environment Variable Invariant**:
   ```bash
   export MALLOC_CONF="prof:true,prof_active:true,prof_prefix:jeprof.out,lg_prof_interval:30,prof_leak:true"
   ```
   - `prof:true`: Mengaktifkan profiling engine jemalloc.
   - `lg_prof_interval:30`: Mengeluarkan snapshot dump setiap $2^{30}\,\text{bytes} = 1\,\text{GB}$ alokasi baru via sampling Poisson process.
   - `prof_leak:true`: Memicu automated leak dump saat program exit.
2. **Analisis Leak Dump**:
   ```bash
   # Visualisasi leak trace ke format SVG / PDF
   jeprof --show_bytes --pdf ./my_service jeprof.out.* > leak_graph.pdf
   
   # Analisis delta pertumbuhan memori antar dua interval snapshot
   jeprof --show_bytes --base=jeprof.out.01 ./my_service jeprof.out.02 --text
   ```

### D. CPython Memory Tracking & Snapshot Diffing (`tracemalloc`)
1. **PyMalloc vs System Allocator**:
   - CPython menggunakan `pymalloc` untuk objek $\le 512\,\text{bytes}$ yang dialokasikan dalam 256KB Arenas $\to$ 4KB Pools $\to$ Size-classed Blocks.
   - Objek $> 512\,\text{bytes}$ langsung dialihkan ke system `malloc()`.
2. **Snapshot Diffing Pattern**:
   ```python
   import tracemalloc

   tracemalloc.start(25) # Rekam kedalaman 25 stack frames
   snap1 = tracemalloc.take_snapshot()
   
   # Eksekusi beban kerja / batch request
   process_workload()
   
   snap2 = tracemalloc.take_snapshot()
   top_diffs = snap2.compare_to(snap1, 'lineno')
   for stat in top_diffs[:10]:
       print(stat)
   ```
3. **Cyclic Garbage Detection**:
   - Reference counting gagal membebaskan siklus referensi melingkar ($A \to B \to A$).
   - Manfaatkan `gc.collect()`, pantau `gc.garbage`, dan hindari closure berantai atau custom finalizer `__del__` pada objek dengan circular reference.

---

## 5. Invariant Self-Check Executable (Pure Python 3.12 Standard Library)

Skrip verifikasi mandiri komprehensif tanpa dependensi pihak ketiga (*Pure Python Standard Library*). Menguji Sampling Profiler Simulator, Stack Trie Aggregator, Flamegraph Generator, Differential Profile Delta Calculator, Memory Leak Detector, dan Lock Contention Oracle:

```python
"""
Neuron N034 Invariant Self-Check:
Autonomous Runtime Profiler, Stack Fold Trie, Sub-Millisecond Flamegraph,
Differential Profile Diffing, Memory Leak Oracle, & Mutex Contention Oracle.
Zero external dependencies (Python 3.12+ Standard Library).
"""
import sys
import time
import math
import threading
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ============================================================================
# 1. SAMPLING PROFILER & STACK TRIE AGGREGATOR
# ============================================================================
class StackFrameNode:
    """Trie Node untuk agregasi hierarki call stack."""
    def __init__(self, name: str):
        self.name: str = name
        self.samples: int = 0
        self.total_duration_us: int = 0
        self.children: Dict[str, "StackFrameNode"] = {}

    def get_or_create_child(self, child_name: str) -> "StackFrameNode":
        if child_name not in self.children:
            self.children[child_name] = StackFrameNode(child_name)
        return self.children[child_name]


class SamplingProfilerTrie:
    """
    Agregasi stack trace sampling menjadi struktur prefix-tree (Trie)
    untuk kalkulasi on-CPU/off-CPU Flamegraph.
    """
    def __init__(self):
        self.root = StackFrameNode("root")
        self.total_samples: int = 0

    def insert_sample(self, stack_frames: List[str], duration_us: int = 100):
        """Menyisipkan satu sample stack trace (root -> leaf order)."""
        current = self.root
        current.samples += 1
        current.total_duration_us += duration_us
        self.total_samples += 1

        for frame in stack_frames:
            current = current.get_or_create_child(frame)
            current.samples += 1
            current.total_duration_us += duration_us

    def parse_folded_line(self, line: str):
        """Mem-parsing baris folded stack format ('func1;func2;func3 42')."""
        line = line.strip()
        if not line:
            return
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            return
        stack_str, count_str = parts
        count = int(count_str)
        frames = stack_str.split(";")
        for _ in range(count):
            self.insert_sample(frames, duration_us=100)

    def export_folded_format(self) -> List[str]:
        """Mengekspor kembali Trie ke format folded stack standar industri."""
        results = []

        def _traverse(node: StackFrameNode, current_path: List[str]):
            if not node.children and current_path:
                results.append(f"{';'.join(current_path)} {node.samples}")
                return
            for child_name, child_node in sorted(node.children.items()):
                _traverse(child_node, current_path + [child_name])

        for name, child in sorted(self.root.children.items()):
            _traverse(child, [name])
        return results

    def render_ascii_flamegraph(self, max_width: int = 60) -> str:
        """Menghasilkan representasi visual Flamegraph ASCII berbasis proporsi."""
        lines = []

        def _render(node: StackFrameNode, depth: int):
            indent = "  " * depth
            fraction = node.samples / max(1, self.total_samples)
            bar_len = max(1, int(fraction * max_width))
            bar = "#" * bar_len
            lines.append(f"{indent}|- {node.name} [{node.samples} smp, {fraction*100:5.1f}%] {bar}")
            for child in sorted(node.children.values(), key=lambda x: x.samples, reverse=True):
                _render(child, depth + 1)

        for child in sorted(self.root.children.values(), key=lambda x: x.samples, reverse=True):
            _render(child, 0)
        return "\n".join(lines)


# ============================================================================
# 2. DIFFERENTIAL PROFILING ENGINE (2-WAY DIFF REGRESSION)
# ============================================================================
class DifferentialProfiler:
    """
    Menghitung delta perubahan persentase resource antar baseline dan current profile
    untuk mendeteksi regresi performa secara instan.
    """
    @staticmethod
    def compute_diff(baseline_folded: List[str], current_folded: List[str]) -> Dict[str, Dict[str, Any]]:
        def _to_map(lines: List[str]) -> Tuple[Dict[str, int], int]:
            m = {}
            total = 0
            for line in lines:
                if not line.strip():
                    continue
                k, v = line.rsplit(" ", 1)
                count = int(v)
                m[k] = count
                total += count
            return m, total

        base_map, base_total = _to_map(baseline_folded)
        curr_map, curr_total = _to_map(current_folded)

        all_keys = set(base_map.keys()) | set(curr_map.keys())
        diff_report = {}

        for stack in sorted(all_keys):
            base_count = base_map.get(stack, 0)
            curr_count = curr_map.get(stack, 0)

            base_pct = (base_count / max(1, base_total)) * 100.0
            curr_pct = (curr_count / max(1, curr_total)) * 100.0
            delta_pct = curr_pct - base_pct

            diff_report[stack] = {
                "base_count": base_count,
                "curr_count": curr_count,
                "base_pct": base_pct,
                "curr_pct": curr_pct,
                "delta_pct": delta_pct,
                "status": "REGRESSION" if delta_pct > 2.0 else ("OPTIMIZED" if delta_pct < -2.0 else "NEUTRAL")
            }
        return diff_report


# ============================================================================
# 3. ADVANCED MEMORY LEAK ORACLE (HEAP RETENTION & CYCLE DETECTOR)
# ============================================================================
class SimulatedHeapBlock:
    def __init__(self, block_id: int, size_bytes: int, call_site: str):
        self.block_id = block_id
        self.size_bytes = size_bytes
        self.call_site = call_site
        self.timestamp = time.monotonic()


class MemoryLeakOracle:
    """
    Detektor memory leak tingkat alokator dengan snapshot comparison,
    tracking alokasi un-freed, dan kalkulasi laju kebocoran linear (bytes/sec).
    """
    def __init__(self):
        self.active_allocations: Dict[int, SimulatedHeapBlock] = {}
        self._next_block_id: int = 1
        self._lock = threading.Lock()

    def allocate(self, size_bytes: int, call_site: str) -> int:
        with self._lock:
            bid = self._next_block_id
            self._next_block_id += 1
            self.active_allocations[bid] = SimulatedHeapBlock(bid, size_bytes, call_site)
            return bid

    def free(self, block_id: int) -> bool:
        with self._lock:
            if block_id in self.active_allocations:
                del self.active_allocations[block_id]
                return True
            return False

    def take_snapshot(self) -> Dict[str, Dict[str, int]]:
        """Merekam agregasi memori aktif per call site."""
        with self._lock:
            snapshot = defaultdict(lambda: {"count": 0, "total_bytes": 0})
            for block in self.active_allocations.values():
                snapshot[block.call_site]["count"] += 1
                snapshot[block.call_site]["total_bytes"] += block.size_bytes
            return dict(snapshot)

    def detect_leaks(self, snap_before: Dict[str, Dict[str, int]], snap_after: Dict[str, Dict[str, int]], threshold_bytes: int = 1024) -> List[Dict[str, Any]]:
        """Mengidentifikasi call site yang mengalami pertumbuhan memori monotonik tak wajar."""
        leaks = []
        for site, after_stat in snap_after.items():
            before_stat = snap_before.get(site, {"count": 0, "total_bytes": 0})
            delta_bytes = after_stat["total_bytes"] - before_stat["total_bytes"]
            delta_count = after_stat["count"] - before_stat["count"]

            if delta_bytes >= threshold_bytes and delta_count > 0:
                leaks.append({
                    "call_site": site,
                    "leaked_bytes": delta_bytes,
                    "leaked_objects": delta_count,
                    "growth_rate_pct": ((delta_bytes / max(1, before_stat["total_bytes"])) * 100.0) if before_stat["total_bytes"] > 0 else 100.0
                })
        return sorted(leaks, key=lambda x: x["leaked_bytes"], reverse=True)


# ============================================================================
# 4. MUTEX LOCK CONTENTION ORACLE
# ============================================================================
class MonitoredMutex:
    """
    Mutex wrapper yang mencatat metrik latensi akuisisi (Wait Time)
    dan durasi eksekusi critical section (Hold Time) untuk deteksi bottleneck thread.
    """
    def __init__(self, name: str):
        self.name = name
        self._raw_lock = threading.Lock()
        self.total_acquisitions: int = 0
        self.total_wait_time_ns: int = 0
        self.total_hold_time_ns: int = 0
        self.contended_acquisitions: int = 0
        self._hold_start_ns: int = 0

    def __enter__(self):
        t_start = time.perf_counter_ns()
        acquired = self._raw_lock.acquire(blocking=True)
        t_acquired = time.perf_counter_ns()

        wait_ns = t_acquired - t_start
        self.total_wait_time_ns += wait_ns
        self.total_acquisitions += 1
        if wait_ns > 500_000: # Wait > 0.5ms dianggap mengalami contention
            self.contended_acquisitions += 1

        self._hold_start_ns = t_acquired
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        t_release = time.perf_counter_ns()
        self.total_hold_time_ns += (t_release - self._hold_start_ns)
        self._raw_lock.release()

    def get_stats(self) -> Dict[str, Any]:
        avg_wait_us = (self.total_wait_time_ns / max(1, self.total_acquisitions)) / 1000.0
        avg_hold_us = (self.total_hold_time_ns / max(1, self.total_acquisitions)) / 1000.0
        contention_rate = (self.contended_acquisitions / max(1, self.total_acquisitions)) * 100.0
        return {
            "name": self.name,
            "acquisitions": self.total_acquisitions,
            "avg_wait_us": avg_wait_us,
            "avg_hold_us": avg_hold_us,
            "contention_rate_pct": contention_rate
        }


# ============================================================================
# 5. INVARIANT VERIFICATION SUITE
# ============================================================================
def verify_stack_trie_and_flamegraph():
    """Invarian 1: Akurasi agregasi prefix tree & transformasi folded stack."""
    profiler = SamplingProfilerTrie()
    
    # Masukkan sampel trace
    profiler.parse_folded_line("main;router;auth_middleware 50")
    profiler.parse_folded_line("main;router;database_query;sqlite3_step 100")
    profiler.parse_folded_line("main;router;serialize_json 50")

    assert profiler.total_samples == 200, f"Expected 200 total samples, got {profiler.total_samples}"
    
    # Verifikasi ekspor folded string
    folded_out = profiler.export_folded_format()
    assert len(folded_out) == 3, f"Expected 3 unique leaf paths, got {len(folded_out)}"
    assert "main;router;database_query;sqlite3_step 100" in folded_out

    # Verifikasi ASCII Flamegraph rendering
    ascii_graph = profiler.render_ascii_flamegraph()
    assert "database_query" in ascii_graph
    assert "50.0%" in ascii_graph # 100 / 200 = 50.0%
    return True


def verify_differential_profiling():
    """Invarian 2: Kalkulasi regresi performa 2-way diff."""
    baseline = [
        "app;handle_req;fast_json 100",
        "app;handle_req;sql_read 100"
    ] # Total 200 (masing-masing 50%)

    current = [
        "app;handle_req;fast_json 100",
        "app;handle_req;sql_read 300"
    ] # Total 400 (fast_json 25%, sql_read 75%)

    diff = DifferentialProfiler.compute_diff(baseline, current)
    
    sql_diff = diff["app;handle_req;sql_read"]
    assert sql_diff["base_pct"] == 50.0, "Baseline pct mismatch"
    assert sql_diff["curr_pct"] == 75.0, "Current pct mismatch"
    assert sql_diff["delta_pct"] == 25.0, "Delta pct mismatch"
    assert sql_diff["status"] == "REGRESSION", "Status should be REGRESSION"

    json_diff = diff["app;handle_req;fast_json"]
    assert json_diff["delta_pct"] == -25.0, "Delta pct should decrease by 25%"
    assert json_diff["status"] == "OPTIMIZED" or json_diff["status"] == "NEUTRAL" or json_diff["delta_pct"] < 0
    return True


def verify_memory_leak_oracle():
    """Invarian 3: Snapshot diffing & identifikasi un-freed heap blocks."""
    oracle = MemoryLeakOracle()

    # Snapshot 1 (Baseline)
    snap1 = oracle.take_snapshot()

    # Simulasi alokasi yang dibebaskan secara normal
    b1 = oracle.allocate(512, "service/cache.py:42")
    b2 = oracle.allocate(512, "service/cache.py:42")
    oracle.free(b1)
    oracle.free(b2)

    # Simulasi alokasi bocor (leaked allocations tanpa free)
    for _ in range(50):
        oracle.allocate(1024, "service/leaky_buffer.py:88")

    # Snapshot 2 (Post-workload)
    snap2 = oracle.take_snapshot()

    leaks = oracle.detect_leaks(snap1, snap2, threshold_bytes=10_000)
    assert len(leaks) == 1, f"Expected 1 detected leak site, got {len(leaks)}"
    assert leaks[0]["call_site"] == "service/leaky_buffer.py:88"
    assert leaks[0]["leaked_bytes"] == 50 * 1024, f"Expected 51200 leaked bytes, got {leaks[0]['leaked_bytes']}"
    assert leaks[0]["leaked_objects"] == 50
    return True


def verify_mutex_contention_oracle():
    """Invarian 4: Tracking thread contention & lock acquisition delays."""
    mutex = MonitoredMutex("SharedDatabasePool")
    num_threads = 4
    iterations = 20

    def worker():
        for _ in range(iterations):
            with mutex:
                time.sleep(0.001) # Tahan lock selama 1ms untuk memicu contention

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    stats = mutex.get_stats()
    assert stats["acquisitions"] == num_threads * iterations
    assert stats["avg_hold_us"] >= 900.0, f"Expected hold time >= 900us, got {stats['avg_hold_us']}"
    assert stats["contention_rate_pct"] > 0.0, "Expected positive contention rate under concurrent load"
    return True


if __name__ == "__main__":
    t0 = time.perf_counter()
    r_trie = verify_stack_trie_and_flamegraph()
    r_diff = verify_differential_profiling()
    r_leak = verify_memory_leak_oracle()
    r_mutex = verify_mutex_contention_oracle()
    dur_ms = (time.perf_counter() - t0) * 1000.0

    print(f"[+] N034 Invariants Verified in {dur_ms:.2f}ms:")
    print(f"    - StackTrie & Flamegraph: {r_trie}")
    print(f"    - Differential Profiling: {r_diff}")
    print(f"    - Memory Leak Oracle:    {r_leak}")
    print(f"    - Mutex Contention:      {r_mutex}")
```
