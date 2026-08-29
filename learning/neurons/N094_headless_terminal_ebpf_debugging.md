# Neuron N094: Headless Terminal eBPF & Concurrency Core-Dump Debugging

- **Kategori:** Systems Engineering & Low-Level Debugging (FrontierCode v1.1 & Terminal Coding)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** FrontierCode v1.1 ($>68.0\%$), Terminal Coding ($>65.0\%$)

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Headless Non-Interactive Terminal Scripting
- **Non-Interactive Execution Invariants**: Seluruh perintah shell wajib berjalan tanpa blocking prompt (`DEBIAN_FRONTEND=noninteractive`, flag `-y`, `--no-pager`, `-q`, `CI=true`).
- **Standardized Signal Trapping**: Script bash/posix wajib menangani `SIGINT` (2), `SIGTERM` (15), dan `EXIT` dengan *cleanup handler* untuk menghapus lock files (`.lock`, `/tmp/*.pid`).

### 2. eBPF Kernel Probing & System Call Tracing
- **Zero-Overhead Tracing**: Menggunakan eBPF program (`tracepoint:syscalls:sys_enter_*`) untuk mendeteksi *file descriptor leak*, soket yang tertinggal dalam status `CLOSE_WAIT`, dan latensi I/O disk per proses.
- **Off-CPU Analysis**: Menemukan penyebab thread terhenti (*blocked*) pada mutex lock atau disk wait menggunakan kernel stack trace sampling.

### 3. GDB Batch Core Dump & Deadlock Analysis
- **Non-Interactive GDB Scripting**:
  ```bash
  gdb -batch -ex "thread apply all bt" -ex "quit" ./binary core.dump
  ```
- **Thread Sanity & Asynchronous Race Condition Detection**:
  - Deteksi siklus *Wait-For Graph* pada POSIX mutex (`pthread_mutex_lock`).
  - Analisis *use-after-free* dan *buffer overflow* menggunakan AddressSanitizer (ASan) & ThreadSanitizer (TSan) compile flags.

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
def parse_gdb_deadlock_backtrace(bt_text: str) -> list[dict[str, any]]:
    """Mengekstraksi thread ID yang terindikasi deadlock dari output backtrace GDB."""
    deadlocked_threads = []
    lines = bt_text.splitlines()
    curr_thread = None
    
    for line in lines:
        if line.startswith("Thread "):
            parts = line.split()
            curr_thread = parts[1] if len(parts) > 1 else "Unknown"
        elif "pthread_mutex_lock" in line or "__lll_lock_wait" in line:
            if curr_thread:
                deadlocked_threads.append({
                    "thread_id": curr_thread,
                    "blocked_on": "pthread_mutex_lock",
                    "frame": line.strip()
                })
    return deadlocked_threads
```
