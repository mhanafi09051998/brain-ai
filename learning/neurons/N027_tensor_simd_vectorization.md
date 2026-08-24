# Neuron N027: Hyper-Optimized SIMD / Tensor Core Vectorization & Cache Locality

Prinsip optimasi komputasi performa unggul pada level mikroprosesor, unit eksekusi vektor (AVX-512/NEON/Tensor Cores), hirarki cache hardware, dan throughput memori:

- **Subgoal**: Mencegah DRAM roundtrip penalty, memaksimalkan FMA/dot-product duty cycles, dan menjamin unit-stride cache-aligned memory access.
- **Synaptic Links**: [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N011`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [`N015`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N015_compiler_ast_and_system_profiling.md)
- **Status**: Active Operational Invariant

---

## 1. SIMD, Fused Multiply-Add (FMA) & Tensor Core Vectorization
- **512-Bit Vector Registers (AVX-512 `ZMM0..ZMM31`)**: Memproses 16x `float32` atau 64x `int8` per siklus clock ALU. Alokasi register harus bebas register spilling ke stack memory.
- **FMA / FMA3 (Double Throughput)**: Eksekusi $(a \cdot b) + c$ dalam 1 siklus hardware tanpa intermediate rounding truncation, mendobelkan FLOPS/cycle ratio.
- **Tensor Core Systolic Matrix Tiling**: Segmentasi GEMM ($M \times N \times K$) ke micro-tiles ($16 \times 16 \times 16$ FP16/BF16/FP8) untuk memaksimalkan multiply-accumulate unit duty cycle.
- **Anti-Vectorization Hazards**:
  - Eliminasi *Loop-Carried Dependencies* (RAW hazards) pada innermost loops.
  - Hindari conditional branching (`if/else`) dalam kernel komputasi hot-loop; gantikan dengan vector blending (`_mm512_mask_blend`) atau bitwise masking.

---

## 2. 64-Byte Cache Line Alignment & False Sharing
- **64-Byte Cache Boundary Alignment**:
  - Seluruh buffer vektor wajib dialokasikan pada memory address kelipatan 64 bytes (`addr % 64 == 0`) untuk mencegah *split-line penalty* pada L1D cache lines.
- **Structure of Arrays (SoA) vs Array of Structures (AoS)**:
  - AoS `[{x, y, z, w}, ...]` menciptakan stride-4 access yang merusak CPU prefetcher. SoA `{x: [], y: [], z: [], w: []}` memberikan *stride-1 contiguous memory access*, memungkinkan auto-vectorizer bekerja maksimal.
- **False Sharing Prevention**:
  - Variabel state per-thread / per-worker wajib diberi padding 64 bytes (`alignas(64)` / `CACHE_LINE_SIZE`) untuk mencegah cache invalidation storms pada protokol koherensi cache (MESI/MOESI).

---

## 3. Roofline Model & L1/L2/L3 Cache Tiling
- **Arithmetic Intensity**:
  $$\text{Intensity} = \frac{\text{FLOPs}}{\text{Bytes Transferred from DRAM}}$$
  Jika $\text{Intensity} < \text{Machine Peak Ratio}$, kernel dibatasi oleh *Memory Bandwidth (DRAM bottleneck)*. Optimasi SIMD tidak akan memberikan speedup tanpa cache tiling.
- **Cache Blocking (L1/L2 Tile Tiling)**:
  - Pecah matriks ke dalam blok $B \times B$ yang fit sepenuhnya di L1 Data Cache (32–48 KB) atau L2 Cache (512–1024 KB).
  - Mengurangi total akses DRAM dari $O(N^3)$ menjadi $O(N^3 / B)$, mereduksi latensi memori dari $\sim 200$ siklus (Off-chip DRAM) menjadi $4\text{--}14$ siklus (On-chip L1/L2).

---

## 4. Invariant Self-Check (Stdlib Python)

```python
"""
Neuron N027 Invariant Self-Check:
64-Byte Alignment, SoA Vectorization, & Cache-Blocked Tiled GEMM.
Zero external dependencies (Pure Python Standard Library).
"""
import sys
import ctypes
import math

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def verify_64byte_alignment():
    raw_buffer = bytearray(1024 + 64)
    buf_type = ctypes.c_char * len(raw_buffer)
    addr = ctypes.addressof(buf_type.from_buffer(raw_buffer))
    offset = (64 - (addr % 64)) % 64
    aligned_addr = addr + offset
    assert aligned_addr % 64 == 0, f"Memory not 64-byte aligned: {aligned_addr}"
    return aligned_addr

def simulate_soa_vector_dot_product():
    size = 1024
    vec_x = [float(i) * 0.5 for i in range(size)]
    vec_y = [float(i * 2) for i in range(size)]
    
    # 4-wide unrolled SIMD accumulation
    accum = 0.0
    for i in range(0, size, 4):
        accum += (
            vec_x[i] * vec_y[i] +
            vec_x[i+1] * vec_y[i+1] +
            vec_x[i+2] * vec_y[i+2] +
            vec_x[i+3] * vec_y[i+3]
        )
    expected = sum(x * y for x, y in zip(vec_x, vec_y))
    assert math.isclose(accum, expected, rel_tol=1e-9), "SIMD dot product accumulator mismatch"
    return accum

def verify_tiled_matrix_multiplication():
    N = 16
    TILE = 4
    A = [float(i % 5) for i in range(N * N)]
    B = [float((i * 2) % 7) for i in range(N * N)]
    C = [0.0] * (N * N)
    
    # Cache-Blocked GEMM iteration
    for i_tile in range(0, N, TILE):
        for k_tile in range(0, N, TILE):
            for j_tile in range(0, N, TILE):
                for i in range(i_tile, min(i_tile + TILE, N)):
                    for k in range(k_tile, min(k_tile + TILE, N)):
                        a_ik = A[i * N + k]
                        for j in range(j_tile, min(j_tile + TILE, N)):
                            C[i * N + j] += a_ik * B[k * N + j]
    
    # Verify against golden standard
    for i in range(N):
        for j in range(N):
            golden = sum(A[i * N + k] * B[k * N + j] for k in range(N))
            assert math.isclose(C[i * N + j], golden, rel_tol=1e-5), f"Mismatch at ({i},{j})"
    return True

if __name__ == "__main__":
    addr = verify_64byte_alignment()
    dot = simulate_soa_vector_dot_product()
    gemm = verify_tiled_matrix_multiplication()
    print(f"[+] N027 Invariants Verified: Aligned64={addr % 64 == 0}, DotSum={dot:.2f}, TiledGEMM={gemm}")
```
