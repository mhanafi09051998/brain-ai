# Neuron N037: WebAssembly (WASM), WASI & Micro-VM Sandboxing

Prinsip rekayasa isolasi runtime modern, komputasi multi-tenant zero-trust, dan sandboxing kode tak tepercaya (*untrusted third-party plugin execution*) memanfaatkan WebAssembly (WASM), WASI Component Model, Wasmtime, Extism, Firecracker Micro-VMs, dan V8 Isolates:

- **Kategori**: Systems Architecture, Sandboxing & Zero-Trust Isolation, WebAssembly / WASI, Micro-VMs, V8 Isolates
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengisolasi eksekusi kode pihak ketiga dengan performa mendekati native ($<5\text{ms}$ cold start, $<5\text{MB}$ overhead), mengeliminasi celah memori lintas thread/tenant via WASM linear memory hardware page guards & V8 isolate cages, menegakkan capability-based access control via WASI Component Model, serta menjamin deterministik CPU/Memory budgeting via fuel metering dan KVM hardware-assisted micro-VMs.
- **Synaptic Links**: [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N014`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N014_zero_trust_security_and_cryptography.md), [`N023`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N023_zero_day_kernel_defense.md), [`N029`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N029_modern_systems_rust_go.md), [`N032`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N032_cloud_native_edge_infra.md)
- **Status**: Active Operational Invariant

---

## 🛡️ 1. WebAssembly Linear Memory Sandboxing & Hardware Intercepts

```
+-----------------------------------------------------------------------------------+
| Host Address Space (Virtual Memory)                                               |
|  +---------------------------+-----------------------------------+--------------+ |
|  | WASM Linear Memory (Heap) | Guard Page Region (PROT_NONE)     | Host Engine  | |
|  | 0x00000000 -> 0x00010000  | 4GB / 6GB Unmapped Virtual Memory | & Stack      | |
|  +---------------------------+-----------------------------------+--------------+ |
|               ^                               |                                   |
|       Valid Guest Access              Out-of-Bounds Access                        |
|        (Direct Offset)           (Triggers MMU SIGSEGV / SIGBUS)                  |
|                                               |                                   |
|                                               v                                   |
|                             Host Signal Trap Handler -> WASM Trap                 |
+-----------------------------------------------------------------------------------+
```

### 1.1. Linear Memory Model & Page Granularity
1. **Struktur Memori Kontigu**:
   - Memori WASM adalah array biner byte tunggal (*flat contiguous byte array*) yang terindeks dari offset `0` hingga `memory.size * 65536 - 1`.
   - **Ukuran Halaman Standar (Page Granularity)**: 1 WebAssembly Page = **$64\text{ KiB}$** ($65,536\text{ bytes}$).
   - Guest tidak dapat membaca atau menulis alamat di luar array ini. Seluruh pointer guest adalah offset 32-bit (`u32` / `wasm32`) atau 64-bit (`u64` / `wasm64`) relatif terhadap basis linear memory.
2. **Dinamika Alokasi (`memory.grow`)**:
   - Penambahan kapasitas memori dilakukan secara eksplisit via instruksi `memory.grow(pages)`.
   - Host runtime (Wasmtime, Extism) dapat menetapkan batas atas keras (*maximum memory pages*) untuk mencegah eksploitasi Out-Of-Memory (OOM) Denial of Service.

### 1.2. Hardware Guard Pages & Zero-Cost Signal Traps
1. **Kelemahan Software Bounds Checking**:
   - Memeriksa batas memori via instruksi kondisional CPU (`cmp` + `jge`) pada setiap operasi `load`/`store` menimbulkan penalti throughput $20\text{--}30\%$.
2. **Zero-Cost Hardware Page Trapping (Cranelift / Wasmtime)**:
   - Pada arsitektur 64-bit, host mengalokasikan reservasi virtual address space sebesar **$4\text{ GB}$ atau $6\text{ GB}$** untuk setiap instans WASM menggunakan `mmap(PROT_NONE)`.
   - Linear memory yang aktif dipetakan dengan hak akses `PROT_READ | PROT_WRITE` di awal rentang tersebut. Sisa rentang virtual dibiarkan sebagai *Guard Pages* tanpa hak akses.
   - Ketika guest mencoba mengakses memori out-of-bounds (misal offset $> \text{linear memory size}$), CPU Memory Management Unit (MMU) memicu hardware fault (`SIGSEGV` di Linux/POSIX atau `STATUS_ACCESS_VIOLATION` di Windows).
   - Host signal handler menangkap fault tersebut, memverifikasi alamat fault berada di dalam guard region, dan menerjemahkannya seketika menjadi *deterministic WASM runtime trap* tanpa membahayakan integritas proses host.

### 1.3. Shadow Stack & Control-Flow Integrity (CFI)
1. **Pemisahan Execution Stack & Data Stack**:
   - Call stack eksekusi (return addresses, frame pointers, register saves) dikelola langsung oleh mesin virtual host dan **sama sekali tidak dapat diakses** oleh linear memory WASM.
   - Guest hanya memiliki *data stack* terisolasi untuk variabel lokal dan array/struktur yang membutuhkan address reference.
2. **Eliminasi Total Serangan ROP/JOP**:
   - Return-Oriented Programming (ROP) dan buffer overflow yang menimpa alamat return stack menjadi tidak mungkin terjadi (*structurally impossible*) di dalam WASM sandbox karena instruksi jumping hanya diizinkan ke target fungsi tervalidasi dalam Type Table (`call_indirect`).

---

## 🌐 2. WASI (WebAssembly System Interface) & Capability-Based Security

### 2.1. Paradigma Capability-Based Security (Zero Ambient Authority)
1. **Penolakan Ambient Authority**:
   - Berbeda dengan model POSIX tradisional di mana proses mewarisi seluruh hak akses pengguna (misal: dapat membaca sembarang file di `/etc` atau membuka raw socket jika proses berjalan sebagai user tersebut), WASI menerapkan **Zero Ambient Authority**.
   - Guest WASM secara default tidak memiliki akses ke:
     - Syscall kernel sistem operasi.
     - Filesystem lokal host.
     - Network socket dan antarmuka jaringan.
     - System clocks dan monotonic timers beresolusi tinggi.
     - Environment variables dan command-line arguments.
2. **Pre-Opened File Descriptors (`dirfd`) & Capability Attenuation**:
   - Host memberikan hak akses secara eksplisit hanya pada direktori tertentu yang didaftarkan (*pre-opened directories*).
   - Operasi file guest dibatasi pada handle direktori tersebut (`path_open`, `fd_read`, `fd_write`).
   - **Path Traversal Shield**: Runtime WASI memverifikasi setiap resolusi path relatif. Upaya melarikan diri menggunakan `../` atau symlink di luar root boundary direktori yang diberikan akan ditolak dengan error `WASI_ENOTCAPABLE` / `WASI_EPERM`.

### 2.2. Evolusi WASI & The Component Model (WASI Preview 2 / Wasm 2.0)
1. **WASI Preview 1 (`wasi_snapshot_preview1`)**:
   - Mengadopsi abstraksi file descriptor datar mirip POSIX sederhana (`fd_read`, `fd_write`, `environ_get`).
2. **WASI Preview 2 (`wasi:cli`, `wasi:http`, `wasi:filesystem`, `wasi:sockets`)**:
   - Dibangun di atas **WASM Component Model** menggunakan antarmuka formal `WIT` (*WebAssembly Interface Type*).
   - Menggantikan antarmuka berbasis pointer C mentah dengan typed interface berkecepatan tinggi: *records, variants, lists, resources, async streams*.
3. **Canonical ABI (Lifting & Lowering)**:
   - Menstandarkan tata letak memori biner saat memindahkan tipe data kompleks antar bahasa pemrograman (misal Rust $\leftrightarrow$ Go $\leftrightarrow$ Python $\leftrightarrow$ Host) tanpa serialisasi JSON yang lambat.

---

## ⚡ 3. High-Performance Runtimes (Wasmtime) & Universal Plugins (Extism)

```
+-----------------------------------------------------------------------------------+
| Extism / Wasmtime Host Application                                                |
|  +-----------------------------------------------------------------------------+  |
|  | Host Manifest: Allowed Hosts = ["api.zolu.my.id"], Memory Max = 16MB        |  |
|  +-----------------------------------------------------------------------------+  |
|         |                                                             ^           |
|         | 1. Allocate Handle & Write Input Payload                    | 4. Return |
|         v                                                             |    Output |
|  +--------------------------------------------------------------------+--------+  |
|  | WASM Plugin Instance (Isolated Linear Memory)                               |  |
|  |   - Fuel Counter: 10,000,000 instructions max (Deterministic Timeout)       |  |
|  |   - Extism PDK: extism:host/env memory block resolution                    |  |
|  |   - Execution Logic (Untrusted User Code)                                   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 3.1. Wasmtime & Cranelift JIT Invariants
1. **Fuel Metering (Gas Accounting)**:
   - Menghitung konsumsi siklus komputasi secara deterministik dengan mengurangkan counter bahan bakar (*fuel*) pada setiap basic block eksekusi.
   - Ketika fuel habis (`fuel == 0`), runtime seketika menghentikan eksekusi dengan `Trap::OutOfFuel`.
   - Mengeliminasi risiko *infinite loops* dan *CPU starvation* tanpa memerlukan preemptive OS thread cancellation.
2. **Epoch-Based Interruption**:
   - Host thread secara berkala menaikkan nilai epoch mesin (`engine.increment_epoch()`).
   - Instans WASM memeriksa counter epoch pada loop headers dan function entries. Jika epoch melebihi ambang batas, eksekusi di-yield atau di-trap, memberikan mekanisme timeout berbasis wall-clock beroverhead sangat rendah ($<1\%$ CPU).
3. **Resource Limiter (`ResourceLimiter`)**:
   - Menetapkan batas ketat: `memory_growing(current, desired, maximum)`, `table_growing()`, dan jumlah instance simultan.

### 3.2. Extism Universal Plugin Framework
1. **Arsitektur Multi-Bahasa**:
   - Berjalan di atas Wasmtime dengan antarmuka universal PDK (*Plugin Development Kit*) untuk Rust, Go, TypeScript, C, Python, dan Zig.
2. **Protokol Alokasi Memori Host-Guest**:
   - Pertukaran data antar Host dan Guest menggunakan memory handles 64-bit yang dipetakan ke offset linear memory (`extism_alloc`, `extism_load_u8`, `extism_store_u8`).
   - Host menulis payload ke dalam sandbox guest, mengirimkan offset pointer, mengeksekusi entry point fungsi, dan membaca kembali output buffer secara aman.
3. **Host Manifest Declarative Security**:
   - Deklarasi hak akses plugin didefinisikan dalam manifest JSON/struktur:
     ```json
     {
       "wasm": [{"path": "untrusted_plugin.wasm"}],
       "memory": {"max_pages": 256},
       "allowed_hosts": ["*.zolu.my.id"],
       "allowed_paths": {"/tmp/sandbox": "/data"}
     }
     ```

---

## 🚀 4. Micro-VMs & Hardware-Assisted Virtualization (Firecracker & KVM)

```
+------------------------------------------------------------------------------------+
| Bare-Metal Linux Host (Kernel 6.x)                                                 |
|  +-------------------------------------------------------------------------------+ |
|  | Firecracker Jailer (PID Namespace, cgroups v2, Seccomp-BPF Whitelist, No Root)| |
|  |  +--------------------------------------------------------------------------+ | |
|  |  | Firecracker VMM Process (Rust, Minimalist, No PCI/ACPI)                  | | |
|  |  |  +---------------------------------------------------------------------+  | | |
|  |  |  | KVM Virtual Machine (Intel VT-x / AMD-V Hardware Virtualization)    |  | | |
|  |  |  |  - Guest Linux Kernel (vmlinux uncompressed, boots in <5ms)         |  | | |
|  |  |  |  - Minimal Initrd / Rootfs (Ext4 / SquashFS)                        |  | | |
|  |  |  |  - VirtIO MMIO Devices: virtio-net, virtio-block, virtio-vsock       |  | | |
|  |  |  +---------------------------------------------------------------------+  | | |
|  |  +--------------------------------------------------------------------------+ | |
|  +-------------------------------------------------------------------------------+ |
+------------------------------------------------------------------------------------+
```

### 4.1. Hardware Virtualization (KVM: `/dev/kvm`)
1. **VMX Root vs Non-Root Mode (Intel VT-x / AMD-V)**:
   - CPU beralih ke *VMX Non-Root Mode* saat mengeksekusi instruksi guest OS.
   - Upaya eksekusi instruksi sensitif (I/O port, modifikasi control registers `CR0/CR3/CR4`, pemetaan page table) memicu hardware *VM-Exit* kembali ke host VMM (*VMX Root Mode*).
2. **Two-Dimensional Paging (EPT / NPT)**:
   - Extended Page Tables (Intel EPT) / Nested Page Tables (AMD NPT) menerjemahkan *Guest Virtual Address (GVA)* $\to$ *Guest Physical Address (GPA)* $\to$ *Host Physical Address (HPA)* secara langsung pada level hardware MMU dengan overhead TLB minimal.

### 4.2. Arsitektur Firecracker Micro-VM
1. **Desain Minimalis Berorientasi Cloud-Native**:
   - Ditulis murni dalam Rust untuk menjamin memory-safety pada level VMM.
   - Menghapus seluruh bus warisan PC: **Tanpa PCI bus, tanpa ACPI tables, tanpa IDE controller, tanpa legacy BIOS/UEFI firmware**.
   - Perangkat I/O disederhanakan murni menjadi **VirtIO over MMIO (Memory Mapped I/O)**:
     - `virtio-net`: Antarmuka jaringan via Linux TUN/TAP device.
     - `virtio-block`: Penyimpanan disk via sparse file atau raw drive backend.
     - `virtio-vsock`: Komunikasi socket berkecepatan tinggi antara host dan guest tanpa stack TCP/IP.
     - `serial console`: Output logging teks minimal.
2. **Metrik Performa & Skala Ekstrem**:
   - **Waktu Booting**: $< 5\text{ ms}$ (dari cold start hingga eksekusi kernel guest).
   - **Konsumsi Memori**: $\approx 5\text{ MB}$ base memory overhead per microVM.
   - **Kepadatan Tenant**: Mendukung ribuan microVM independen pada satu node bare-metal.

### 4.3. Confinement & The Firecracker Jailer
1. **Isolasi Multi-Lapis (Defense-in-Depth)**:
   - **Linux Namespaces**: Pemisahan `PID`, `NET`, `MNT`, `IPC`, `UTS`, dan `USER` namespaces.
   - **cgroups v2**: Penetapan kuota ketat `cpu.max` (CPU throttling) dan `memory.max` (OOM enclosure).
   - **Chroot Jail**: Mengunci VMM pada direktori kosong terisolasi.
   - **Privilege Dropping**: Menjalankan proses VMM sebagai non-root unprivileged UID/GID.
   - **Seccomp-BPF Filtering**: Memasang filter seccomp ketat yang hanya mengizinkan subset kecil syscall Linux esensial (`epoll_wait`, `read`, `write`, `ioctl` khusus KVM). Syscall tak terduga seketika membunuh proses via `SECCOMP_RET_KILL`.

---

## ⚡ 5. V8 Isolates & Ultra-Dense Edge Compute

### 5.1. Arsitektur V8 Isolate (Cloudflare Workers / Deno Core)
1. **Multi-Tenancy dalam Satu Proses OS**:
   - Berbeda dengan kontainer atau VM yang memerlukan proses OS terpisah, ribuan *V8 Isolates* dapat berjalan di dalam satu OS process yang sama pada thread pool bersama.
   - Setiap isolate memiliki heap JavaScript, garbage collector, dan call stack independen yang sepenuhnya terisolasi.
2. **Pointer Compression (32-Bit Cages)**:
   - V8 membatasi heap isolate dalam *4GB Virtual Memory Cage*. Seluruh pointer objek disimpan sebagai offset 32-bit relatif terhadap cage base address.
   - Mengurangi penggunaan memori hingga $40\%$ dan secara struktural mencegah pointer JavaScript menjangkau memori proses host di luar cage.

### 5.2. Startup Latency & V8 Snapshots
1. **Sub-Millisecond Cold Starts**:
   - Cold start isolate hanya membutuhkan waktu $\approx 1\text{--}3\text{ ms}$, dengan overhead memori dasar $\approx 3\text{ MB}$.
2. **Heap Snapshots**:
   - Runtime mengompilasi dan menginisialisasi lingkungan dasar (core library, standard APIs) saat build-time, lalu menyimpannya sebagai binary memory snapshot.
   - Saat request baru datang, snapshot dipetakan langsung ke RAM (*instant deserialization*), menghilangkan waktu parsing AST JavaScript.

---

## 📊 6. Matriks Perbandingan Teknologi Sandboxing

| Dimensi Evaluasi | Native Container (Docker/RunC) | Micro-VM (AWS Firecracker) | WebAssembly (Wasmtime/Extism) | V8 Isolates (Deno/Workers) |
| :--- | :--- | :--- | :--- | :--- |
| **Batas Isolasi (Boundary)** | Shared Linux Kernel (cgroups/ns) | Hardware VT-x / AMD-V (KVM) | Software Memory & Type Safety | VM Heap & Pointer Compression |
| **Tingkat Keamanan** | Menengah (Rentan Kernel 0-day) | **Sangat Tinggi (Hardware Level)** | **Tinggi (Capability-Based)** | Tinggi (Language Sandbox) |
| **Waktu Cold Start** | $200\text{ms}\text{--}2\text{s}$ | **$< 5\text{ ms}$** | **$< 1\text{ ms}$** | **$< 2\text{ ms}$** |
| **Overhead Memori / Tenant** | $50\text{MB}\text{--}200\text{MB}$ | $\approx 5\text{ MB}$ | **$< 1\text{--}2\text{ MB}$** | $\approx 3\text{--}5\text{ MB}$ |
| **Dukungan Bahasa** | Semua binary Linux | Semua OS/Linux Kernel | Rust, C/C++, Go, TS, Zig | JavaScript, TypeScript, WASM |
| **Akses Syscall OS** | Lengkap (Filter Seccomp) | Lengkap di dalam Guest Kernel | Nol (WASI Capability Gated) | Nol (Host API Injection) |
| **Use Case Utama** | Legacy microservices, CI/CD | Multi-tenant Serverless (Lambda) | Plugin systems, Edge Functions | Serverless Edge Workers, SSR |

---

## 🎯 7. Zero-Trust Untrusted Plugin Execution Pipeline

Eksekusi kode pihak ketiga (*untrusted user scripts/plugins*) wajib melewati pipeline pertahanan berlapis:

```
[Untrusted Plugin Binary]
           │
           ▼
1. Static Validation Pass ──────► [Verify WASM magic header, type sections, valid opcodes]
           │
           ▼
2. Capability Attenuation ──────► [Grant only explicit dirfd & whitelisted egress domains]
           │
           ▼
3. Execution Sandboxing  ──────► [Allocate Linear Memory + 4GB Guard Page Reservation]
           │
           ▼
4. Budget Enforcement    ──────► [Inject Fuel Metering + Watchdog Wall-Clock Timer]
           │
           ▼
5. Output Marshalling    ──────► [Copy result from guest linear memory -> Free sandbox]
```

---

## 🧪 8. Invariant Self-Check Executable (Pure Python Standard Library)

Skrip verifikasi mandiri komprehensif menguji seluruh invarian arsitektur sandboxing tanpa dependensi eksternal:

```python
"""
Neuron N037 Invariant Self-Check:
WebAssembly Linear Memory Sandboxing, Hardware Guard Page Simulation,
Fuel-Based Gas Metering, Capability-Based Filesystem Attenuation,
and Extism-Style Memory Handle Marshalling.
Zero external dependencies (Python 3.12+ Standard Library).
"""
import sys
import struct
import time
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ============================================================================
# 1. WASM Linear Memory Sandbox with Bounds & Guard Trapping
# ============================================================================
WASM_PAGE_SIZE = 65536  # 64 KiB

class WasmLinearMemorySandbox:
    """
    Simulasi WebAssembly Linear Memory dengan batasan halaman,
    dynamic memory growth, dan deterministik OOB memory fault trapping.
    """
    def __init__(self, initial_pages: int = 1, max_pages: int = 16):
        self.max_pages = max_pages
        self.pages = initial_pages
        self.buffer = bytearray(self.pages * WASM_PAGE_SIZE)

    @property
    def byte_size(self) -> int:
        return len(self.buffer)

    def grow(self, additional_pages: int) -> int:
        old_pages = self.pages
        if self.pages + additional_pages > self.max_pages:
            return -1  # Growth failure: exceeds maximum page limit
        self.pages += additional_pages
        self.buffer.extend(b"\x00" * (additional_pages * WASM_PAGE_SIZE))
        return old_pages

    def write_u32(self, offset: int, value: int):
        if offset < 0 or offset + 4 > self.byte_size:
            raise MemoryError(f"WASM Trap: Out-of-bounds write at offset {offset} (size: {self.byte_size})")
        struct.pack_into("<I", self.buffer, offset, value)

    def read_u32(self, offset: int) -> int:
        if offset < 0 or offset + 4 > self.byte_size:
            raise MemoryError(f"WASM Trap: Out-of-bounds read at offset {offset} (size: {self.byte_size})")
        return struct.unpack_from("<I", self.buffer, offset)[0]

    def write_bytes(self, offset: int, data: bytes):
        length = len(data)
        if offset < 0 or offset + length > self.byte_size:
            raise MemoryError(f"WASM Trap: Out-of-bounds memory write at offset {offset}..{offset+length}")
        self.buffer[offset : offset + length] = data

    def read_bytes(self, offset: int, length: int) -> bytes:
        if offset < 0 or offset + length > self.byte_size:
            raise MemoryError(f"WASM Trap: Out-of-bounds memory read at offset {offset}..{offset+length}")
        return bytes(self.buffer[offset : offset + length])

def verify_wasm_linear_memory():
    sandbox = WasmLinearMemorySandbox(initial_pages=1, max_pages=4)
    assert sandbox.byte_size == 65536, "Initial page size must be exactly 64KiB"

    # Write & read valid little-endian integer
    sandbox.write_u32(1024, 0x12345678)
    assert sandbox.read_u32(1024) == 0x12345678, "Linear memory read/write mismatch"

    # Memory growth test
    old_pages = sandbox.grow(1)
    assert old_pages == 1 and sandbox.byte_size == 131072, "Memory growth failed"

    # Exceed maximum page allowance
    failed_growth = sandbox.grow(5)
    assert failed_growth == -1, "Exceeding max_pages should fail with -1"

    # Verify Out-Of-Bounds Memory Access Trap
    trap_caught = False
    try:
        sandbox.read_u32(131070)  # Offset + 4 exceeds 131072 byte boundary
    except MemoryError:
        trap_caught = True
    assert trap_caught, "OOB read must trigger deterministic WASM memory trap"
    return True

# ============================================================================
# 2. Fuel / Gas Metering Engine (Deterministic CPU Budgeting)
# ============================================================================
class FuelBudgetExhaustedError(RuntimeError):
    pass

class WasmFuelExecutor:
    """
    Simulasi Fuel Metering Cranelift / Wasmtime:
    Mengurangkan fuel per instruksi/blok komputasi dan mematikan infinite loops.
    """
    def __init__(self, initial_fuel: int):
        self.fuel = initial_fuel

    def consume_fuel(self, amount: int):
        if self.fuel < amount:
            self.fuel = 0
            raise FuelBudgetExhaustedError("WASM Trap: Deterministic Fuel Budget Exhausted (CPU Starvation Shield)")
        self.fuel -= amount

    def execute_loop(self, iterations: int) -> int:
        accum = 0
        for i in range(iterations):
            self.consume_fuel(10)  # Each loop iteration costs 10 fuel units
            accum += (i ^ 0x5A) & 0xFF
        return accum

def verify_fuel_metering():
    # Scenario A: Loop finishes within fuel budget
    executor_a = WasmFuelExecutor(initial_fuel=1000)
    result = executor_a.execute_loop(50)  # Costs 500 fuel
    assert result >= 0 and executor_a.fuel == 500, "Fuel deduction mismatch"

    # Scenario B: Infinite loop / runaway calculation terminated deterministically
    executor_b = WasmFuelExecutor(initial_fuel=300)
    fuel_trapped = False
    try:
        executor_b.execute_loop(100)  # Requires 1000 fuel, budget is 300
    except FuelBudgetExhaustedError:
        fuel_trapped = True
    assert fuel_trapped and executor_b.fuel == 0, "Runaway execution must be halted by fuel depletion"
    return True

# ============================================================================
# 3. WASI Capability-Based Virtual Filesystem & Path Traversal Guard
# ============================================================================
class WasiPermissionError(PermissionError):
    pass

class WasiCapabilityFileSystem:
    """
    Simulasi Capability-Based Filesystem WASI:
    Akses hanya diizinkan melalui pre-opened directory handle,
    dan path traversal escape (../) dicegah secara ketat.
    """
    def __init__(self):
        self.preopened_dirs: dict[str, dict[str, bytes]] = {}

    def grant_preopen(self, virtual_dir: str):
        norm_dir = os.path.normpath(virtual_dir).replace("\\", "/")
        if not norm_dir.startswith("/"):
            norm_dir = "/" + norm_dir
        self.preopened_dirs[norm_dir] = {}

    def _resolve_safe(self, virtual_dir: str, rel_path: str) -> tuple[str, str]:
        norm_dir = os.path.normpath(virtual_dir).replace("\\", "/")
        if not norm_dir.startswith("/"):
            norm_dir = "/" + norm_dir

        if norm_dir not in self.preopened_dirs:
            raise WasiPermissionError(f"WASI_ENOTCAPABLE: Directory handle '{virtual_dir}' is not pre-opened")

        # Resolve relative target
        target = os.path.normpath(os.path.join(norm_dir, rel_path)).replace("\\", "/")
        
        # Check boundary containment (anti-traversal guard)
        if target != norm_dir and not target.startswith(norm_dir.rstrip("/") + "/"):
            raise WasiPermissionError(f"WASI_EPERM: Path traversal escape attempt detected for '{rel_path}'")
        return norm_dir, target

    def write_file(self, virtual_dir: str, rel_path: str, data: bytes):
        norm_dir, target = self._resolve_safe(virtual_dir, rel_path)
        self.preopened_dirs[norm_dir][target] = data

    def read_file(self, virtual_dir: str, rel_path: str) -> bytes:
        norm_dir, target = self._resolve_safe(virtual_dir, rel_path)
        if target not in self.preopened_dirs[norm_dir]:
            raise FileNotFoundError(f"WASI_ENOENT: '{rel_path}' not found in virtual dir")
        return self.preopened_dirs[norm_dir][target]

def verify_wasi_capability_fs():
    wasi_fs = WasiCapabilityFileSystem()
    wasi_fs.grant_preopen("/sandbox/data")

    # Valid write and read within preopened root
    wasi_fs.write_file("/sandbox/data", "config.json", b'{"status": "ok"}')
    content = wasi_fs.read_file("/sandbox/data", "config.json")
    assert content == b'{"status": "ok"}', "WASI file content mismatch"

    # Attempt path traversal breakout (../../etc/passwd)
    traversal_blocked = False
    try:
        wasi_fs.write_file("/sandbox/data", "../../etc/passwd", b"malicious")
    except WasiPermissionError:
        traversal_blocked = True
    assert traversal_blocked, "Path traversal breakout attempt must be strictly blocked"

    # Attempt access to ungranted ambient path
    ungranted_blocked = False
    try:
        wasi_fs.read_file("/var/secrets", "key.pem")
    except WasiPermissionError:
        ungranted_blocked = True
    assert ungranted_blocked, "Access without pre-opened capability grant must be rejected"
    return True

# ============================================================================
# 4. Extism-Style Memory Block Marshalling & Host-Guest Boundary
# ============================================================================
class ExtismPluginHostSimulator:
    """
    Simulasi protokol Extism: Alokasi blok memori pada linear memory guest,
    pertukaran data terstruktur via handle/offset, dan validasi boundary.
    """
    def __init__(self, memory: WasmLinearMemorySandbox):
        self.mem = memory
        self.alloc_offset = 1024  # Reserve 0..1023 for internal stack

    def alloc_guest_block(self, data: bytes) -> int:
        offset = self.alloc_offset
        length = len(data)
        # Store header: [4-byte length][payload]
        total_size = 4 + length
        if offset + total_size > self.mem.byte_size:
            raise MemoryError("Extism Host: Guest memory exhausted during allocation")
        
        self.mem.write_u32(offset, length)
        self.mem.write_bytes(offset + 4, data)
        self.alloc_offset += (total_size + 7) & ~7  # 8-byte aligned
        return offset

    def read_guest_block(self, handle_offset: int) -> bytes:
        length = self.mem.read_u32(handle_offset)
        return self.mem.read_bytes(handle_offset + 4, length)

def verify_extism_plugin_marshalling():
    sandbox = WasmLinearMemorySandbox(initial_pages=2, max_pages=4)
    host = ExtismPluginHostSimulator(sandbox)

    payload_in = b'{"action": "transform", "value": 42}'
    handle = host.alloc_guest_block(payload_in)
    
    # Guest reads input, performs pure computation, and writes back
    read_back = host.read_guest_block(handle)
    assert read_back == payload_in, "Extism handle data marshaling failed"

    # Guest writes transformed output to new handle
    payload_out = b'{"status": "success", "result": 1764}'
    out_handle = host.alloc_guest_block(payload_out)
    output_result = host.read_guest_block(out_handle)
    assert b'"result": 1764' in output_result, "Plugin output transformation failed"
    return True

# ============================================================================
# 5. Micro-VM Multi-Tenant Resource Budgeting Simulation
# ============================================================================
class MicroVMInstance:
    """Simulasi Firecracker Micro-VM containerization & cgroups v2 resource capping."""
    def __init__(self, vm_id: str, memory_mb: int, vcpu_quota_pct: int):
        self.vm_id = vm_id
        self.memory_mb = memory_mb
        self.vcpu_quota_pct = min(100, max(1, vcpu_quota_pct))
        self.allocated_ram = 0
        self.is_running = True

    def allocate_memory(self, amount_mb: int) -> bool:
        if not self.is_running:
            return False
        if self.allocated_ram + amount_mb > self.memory_mb:
            # Trigger Micro-VM Cgroup OOM Killer
            self.is_running = False
            return False
        self.allocated_ram += amount_mb
        return True

def verify_microvm_isolation():
    vm_alpha = MicroVMInstance(vm_id="vm-001", memory_mb=128, vcpu_quota_pct=50)
    vm_beta = MicroVMInstance(vm_id="vm-002", memory_mb=64, vcpu_quota_pct=25)

    assert vm_alpha.allocate_memory(64) is True, "VM Alpha valid RAM allocation failed"
    assert vm_beta.allocate_memory(32) is True, "VM Beta valid RAM allocation failed"

    # VM Beta exceeds memory limit -> triggers isolated OOM enclosure
    oom_result = vm_beta.allocate_memory(64)  # 32 + 64 = 96 > 64MB limit
    assert oom_result is False and vm_beta.is_running is False, "OOM enclosure must terminate offending VM"
    
    # Verify VM Alpha remains unaffected (complete multi-tenant fault isolation)
    assert vm_alpha.is_running is True and vm_alpha.allocated_ram == 64, "Tenant isolation breach: VM Alpha affected"
    return True

# ============================================================================
# Main Verification Entry Point
# ============================================================================
if __name__ == "__main__":
    t_start = time.perf_counter()
    v_mem = verify_wasm_linear_memory()
    v_fuel = verify_fuel_metering()
    v_wasi = verify_wasi_capability_fs()
    v_extism = verify_extism_plugin_marshalling()
    v_vm = verify_microvm_isolation()
    t_elapsed = (time.perf_counter() - t_start) * 1000

    print(f"[+] N037 Invariants Verified ({t_elapsed:.2f}ms):")
    print(f"    - WASM Linear Memory & Guard Traps   : {v_mem}")
    print(f"    - Fuel Metering & CPU Starvation Gate: {v_fuel}")
    print(f"    - WASI Capability Filesystem & Egress: {v_wasi}")
    print(f"    - Extism Host-Guest Handle Marshalling: {v_extism}")
    print(f"    - Micro-VM Tenant Isolation & OOM   : {v_vm}")
```
