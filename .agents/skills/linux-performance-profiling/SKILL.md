---
name: linux-performance-profiling
description: High-precision engineering reference for Linux kernel diagnostics, system resource triaging (CPU, memory, disk I/O, sockets), Node.js/V8 runtime profiling (heap dumps, event loop lag, GC thrashing), TCP stack tuning, and inode/storage recovery.
---

# Linux Performance Profiling & Runtime Diagnostics

Empirical, production-grade operational guide for Linux system profiling, kernel resource triaging, Node.js/V8 runtime performance diagnostics, TCP networking optimization, and filesystem inode recovery under extreme load.

---

## 1. Linux Resource Diagnostics & Triage Framework

### A. CPU Saturation vs. Load Averages
Linux load averages (`/proc/loadavg`) measure the average number of threads in an active state:
- `TASK_RUNNING` (`R` state): Actively executing on CPU or waiting in the OS run queue.
- `TASK_UNINTERRUPTIBLE` (`D` state): Blocked waiting for disk I/O, NFS, locks, or hardware response.

#### 1. Decoupling Compute Saturation from I/O Blocking
A high load average ($> \text{nproc}$) does **not** automatically imply CPU exhaustion.

```bash
# 1. Inspect core count and load average baseline
nproc
cat /proc/loadavg
# Output format: [1m load] [5m load] [15m load] [runnable/total threads] [last PID]

# 2. Distinguish CPU run queue (r) from Uninterruptible Sleep (b)
vmstat 1 5
```
- `r` (runnable): Number of processes waiting for CPU runtime. If `r > nproc`, CPU cores are saturated.
- `b` (blocked): Number of processes blocked in uninterruptible sleep (`D`). If `b > 0` while `%id` (idle) is high, the bottleneck is storage/network I/O, not CPU.

#### 2. Per-Core Utilization & Interrupt Profiling (`mpstat`)
```bash
# Install sysstat if missing
sudo apt-get install -y sysstat

# Monitor all individual CPU cores at 1-second intervals
mpstat -P ALL 1 3
```
| Metric | Diagnostic Interpretation | Remediation Path |
| :--- | :--- | :--- |
| `%usr` | High user-space code execution (Node.js, calculations, crypto). | Profile app runtime, optimize algorithms, scale worker threads/processes. |
| `%sys` | High kernel-space execution (syscalls, page faults, context switching). | Reduce syscall frequency (batch I/O, avoid tight `epoll`/read loops). |
| `%iowait` | CPU is idle while threads wait on outstanding disk/NFS requests. | Investigate storage IOPS, NVMe queue depths, database query indices. |
| `%soft` | High software interrupt processing (network packet handling). | Enable NIC multi-queue (RSS), balance IRQ affinity via `irqbalance` or `/proc/irq/<num>/smp_affinity`. |
| `%steal` | Hypervisor stealing cycles for noisy neighbors (Cloud VMs / VPS). | Escalate to cloud provider, change instance type, migrate VM. |

---

### B. Memory Anatomy: RSS, VSZ, PSS, Dirty Pages & Swap

#### 1. Memory Measurement Hierarchy
- **VSZ (Virtual Size)**: Total virtual memory address space allocated by the process (code, data, shared libraries, mapped files, and uncommitted pages).
- **RSS (Resident Set Size)**: Actual physical RAM pages currently mapped into the process address space.
- **PSS (Proportional Set Size)**: Private memory + proportional share of shared libraries ($PSS = USS + \frac{\text{Shared}}{N}$).
- **USS (Unique Set Size)**: Private RAM mapped exclusively to this process (memory freed if process terminates).

#### 2. Fast Rollup Inspection (`smaps_rollup`)
Do not parse raw `/proc/[pid]/smaps` (can cause high kernel overhead for large heaps). Use `/proc/[pid]/smaps_rollup`:
```bash
# Inspect aggregated memory allocation for a specific PID
cat /proc/<PID>/smaps_rollup
```
Example Output Analysis:
```text
Rss:               254320 kB   # Total physical RAM used
Pss:               248900 kB   # Proportional RAM used
Pss_Anon:          230400 kB   # Anonymous memory (heap, stacks)
Pss_File:           18500 kB   # Cached files/code mapped
Shared_Clean:        6200 kB   # Reusable shared library code
Private_Dirty:     230400 kB   # Unwritten private modifications (cannot be dropped without swap)
Swap:                   0 kB   # Pages pushed to swap
```

#### 3. Identifying Memory Leaks vs. Page Cache Usage
Linux aggressively utilizes free RAM for page caching (`Active(file)` and `Inactive(file)` in `/proc/meminfo`).
```bash
# Check memory allocation and real available memory
free -m

# Rank top 10 memory-consuming processes by PSS (requires smem)
sudo apt-get install -y smem
smem -t -k -p -r | head -n 15
```
- **Real Available Memory**: Look at the `available` column in `free -m`. The OS will reclaim `buff/cache` automatically before invoking the OOM killer.
- **True Memory Leak Signature**: `Private_Dirty` or `Pss_Anon` growing monotonically over time without stabilizing under steady-state traffic.

#### 4. Swap Activity & Thrashing Diagnostics
```bash
# Inspect real-time swap in/out pages per second
vmstat 1 5
```
- `si` (swap-in from disk to RAM): Pages read from swap per second.
- `so` (swap-out from RAM to disk): Pages written to swap per second.
- **Thrashing Invariant**: Continuous non-zero values for `si` and `so` combined with high CPU `%sys` or `%iowait` indicates swap thrashing. The system is spending more time paging than executing code.

---

### C. Disk I/O Wait & Block Layer Bottlenecks

#### 1. Device-Level Saturation (`iostat`)
```bash
# Extended device statistics, 1-second interval, omitting inactive devices
iostat -xz 1 5
```
Key Metrics & Critical Thresholds:
- `r/s` & `w/s`: Read and write requests completed per second (IOPS).
- `rkB/s` & `wkB/s`: Read and write throughput in kilobytes/sec.
- `aqu-sz` (Average Queue Size): Number of I/O requests queued at the driver layer. Values $> 2.0$ per disk channel indicate queued backlog.
- `await`: Average total time (in ms) for I/O requests (queue time + hardware service time).
  - NVMe SSD: Expected $< 1.0\text{ ms}$.
  - SATA SSD: Expected $< 5.0\text{ ms}$.
  - HDD: Expected $< 20.0\text{ ms}$.
  - Warning: `await > 50ms` indicates severe I/O bottleneck.
- `%util`: Percentage of CPU time during which I/O requests were issued to the device.
  - Spinning HDDs: `%util > 90%` means device saturation.
  - Multi-queue NVMe SSDs: `%util` may show 100% while device continues to scale due to internal parallel channels; rely on `await` and `aqu-sz` instead.

#### 2. Process-Level I/O Triaging (`pidstat` & `iotop`)
```bash
# Identify exact processes driving disk write/read throughput
pidstat -d 1 5

# Real-time top-like I/O monitor (accumulated I/O)
sudo iotop -oPa
```

---

### D. File Descriptor & Socket Leak Detection

Every open network connection, file on disk, pipe, and UNIX domain socket consumes a file descriptor (`fd`).

#### 1. System-Wide vs. Process-Level Limits
```bash
# Inspect system-wide allocated vs max file descriptors
cat /proc/sys/fs/file-nr
# Output format: [allocated_fds] [allocated_unused_fds] [max_fds]

# Inspect soft and hard limits for a running PID
cat /proc/<PID>/limits | grep "Max open files"
```

#### 2. File Descriptor Exhaustion Triage
```bash
# Count active file descriptors for a specific process
ls -1 /proc/<PID>/fd | wc -l

# Group and categorize open descriptors by target type/file
ls -l /proc/<PID>/fd | awk '{print $NF}' | sort | uniq -c | sort -nr | head -n 20
```

#### 3. Diagnosing Socket FD Leaks
If socket count grows unboundedly:
```bash
# Check sockets held by PID
lsof -p <PID> -a -i
```
- **Leak Signature**: Continuous growth of sockets in `CLOSE_WAIT` (app failed to close socket after remote termination) or unreferenced `ESTABLISHED` sockets remaining open indefinitely without read/write activity or keepalive timeouts.

---

## 2. Node.js & V8 Runtime Profiling & Diagnostics

### A. Heap Snapshot Analysis & Memory Leak Isolation

#### 1. Programmatic Heap Snapshot Generation
Generate memory snapshots directly from code upon memory threshold breach or debugging signal:

```javascript
// heap-dumper.js
const v8 = require('node:v8');
const fs = require('node:fs');
const path = require('node:path');

function captureHeapSnapshot(tag = 'manual') {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = path.join(process.cwd(), `heap-${tag}-${process.pid}-${timestamp}.heapsnapshot`);
  
  const snapshotPath = v8.writeHeapSnapshot(filename);
  console.log(`[HEAP] Snapshot written successfully to: ${snapshotPath}`);
  return snapshotPath;
}

// Example: Auto-capture snapshot if heap used exceeds 85% of max old space
const MEMORY_THRESHOLD_RATIO = 0.85;
setInterval(() => {
  const mem = process.memoryUsage();
  const heapStats = v8.getHeapStatistics();
  const maxHeap = heapStats.heap_size_limit;
  
  if (mem.heapUsed / maxHeap > MEMORY_THRESHOLD_RATIO) {
    console.warn(`[HEAP WARNING] Heap used (${(mem.heapUsed / 1024 / 1024).toFixed(2)} MB) breached 85% of limit (${(maxHeap / 1024 / 1024).toFixed(2)} MB)`);
    captureHeapSnapshot('threshold-breach');
  }
}, 10000).unref();

module.exports = { captureHeapSnapshot };
```

#### 2. Analyzing Heap Snapshots in Chrome DevTools / VSCode
1. Load `.heapsnapshot` into Chrome DevTools (Memory tab -> Load).
2. Compare two snapshots taken 5 minutes apart under sustained load:
   - Switch view from **Summary** to **Comparison**.
   - Sort by **# Delta** or **Size Delta** descending.
3. Key Retainer Patterns:
   - **Closure Scope Leaks**: Callbacks referencing large outer lexical scopes or unremoved listeners (`EventEmitter.on()` without `.off()`).
   - **Global Caches / Maps**: Static objects or `Map`/`Set` instances holding object references without TTL or LRU bounds.
   - **Detached Streams / Buffers**: Unclosed `fs.createReadStream()` or unconsumed pipeline instances retaining chunks in memory.

---

### B. Event Loop Lag Monitoring with `perf_hooks`

Synchronous, CPU-heavy execution blocks the single-threaded Node.js event loop, degrading API response times and causing connection timeouts.

#### 1. High-Precision Lag Instrumentation (`monitorEventLoopDelay`)
```javascript
// event-loop-monitor.js
const { monitorEventLoopDelay } = require('node:perf_hooks');

// Resolution in milliseconds (20ms is empirical standard)
const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();

setInterval(() => {
  const minMs = (h.min / 1e6).toFixed(2);
  const maxMs = (h.max / 1e6).toFixed(2);
  const meanMs = (h.mean / 1e6).toFixed(2);
  const p50Ms = (h.percentile(50) / 1e6).toFixed(2);
  const p99Ms = (h.percentile(99) / 1e6).toFixed(2);
  const p999Ms = (h.percentile(99.9) / 1e6).toFixed(2);

  console.log(`[EVENT LOOP LAG] min: ${minMs}ms | p50: ${p50Ms}ms | p99: ${p99Ms}ms | p99.9: ${p999Ms}ms | max: ${maxMs}ms | mean: ${meanMs}ms`);

  // Alert if p99 lag exceeds acceptable SLA boundary (e.g. 50ms)
  if (h.percentile(99) / 1e6 > 50) {
    console.error(`[ALERT] Event loop blocked! p99 lag = ${p99Ms}ms`);
  }

  // Reset histogram for next observation window
  h.reset();
}, 5000).unref();
```

#### 2. Root-Cause Triage for Event Loop Lag
- **Lag $> 100\text{ms}$ with High CPU (`%usr` $\sim 100\%$)**: Synchronous CPU bottleneck.
  - Culprits: Massive `JSON.parse()` / `JSON.stringify()`, catastrophic regex backtracking (ReDoS), un-workerized cryptography (`crypto.pbkdf2Sync`, `bcrypt.hashSync`), heavy array sorting/filtering.
- **Lag $> 100\text{ms}$ with Low CPU (`%usr` $< 10\%$)**: Synchronous I/O or system call blocking.
  - Culprits: `fs.readFileSync()`, `fs.statSync()`, blocking lock acquisition, or DNS lookups using `dns.lookup` (synchronous `getaddrinfo` thread pool exhaustion).

---

### C. Identifying Garbage Collection (GC) Thrashing

When Node.js heap approaches its configured limit (`--max-old-space-size`), the V8 engine triggers continuous, aggressive Mark-Sweep/Mark-Compact cycles to reclaim memory, consuming 100% CPU on GC pauses while throughput plummets.

#### 1. Runtime GC Telemetry via `PerformanceObserver`
```javascript
// gc-monitor.js
const { PerformanceObserver, constants } = require('node:perf_hooks');

const GC_TYPES = {
  [constants.NODE_PERFORMANCE_GC_MAJOR]: 'Mark-Sweep-Compact (Major)',
  [constants.NODE_PERFORMANCE_GC_MINOR]: 'Scavenge (Minor)',
  [constants.NODE_PERFORMANCE_GC_INCREMENTAL]: 'Incremental',
  [constants.NODE_PERFORMANCE_GC_WEAKCB]: 'Weak Callback'
};

const obs = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  for (const entry of entries) {
    const gcKind = GC_TYPES[entry.detail?.kind] || `Kind-${entry.detail?.kind}`;
    const durationMs = entry.duration.toFixed(2);
    
    // Flag any GC pause taking longer than 30ms
    if (entry.duration > 30) {
      console.warn(`[LONG GC PAUSE] ${gcKind} took ${durationMs}ms`);
    }
  }
});

obs.observe({ entryTypes: ['gc'] });
```

#### 2. V8 Flag Profiling & GC Trace Flags
Launch process with empirical GC tracing flags:
```bash
node --trace-gc --trace-gc-nvp --trace-gc-ignore-scavenger --max-old-space-size=4096 dist/index.js
```
Sample Trace Output Analysis:
```text
[12450:0x55d2]    45210 ms: Mark-sweep 2010.5 (2048.0) -> 1995.2 (2048.0) MB, 142.4 / 0.0 ms  (average mu = 0.120, current mu = 0.082) allocation failure GC in old space requested
```
- **Thrashing Diagnosis**:
  - `Mark-sweep 2010.5 -> 1995.2 MB`: 2010MB attempted GC, only reclaimed 15MB.
  - `142.4 ms`: Stop-the-world pause lasted 142.4ms.
  - `mu = 0.082` (Mutator Utilization): Application code ran only 8.2% of the time; 91.8% of CPU was lost to GC overhead.
  - **Remedy**: Increase `--max-old-space-size` or isolate and eliminate the memory retention path.

---

## 3. Linux TCP/IP Networking & Socket Diagnostics

### A. Socket Inspection & Deep Diagnostics (`ss`)

The `ss` utility reads socket information directly from kernel netlink and `/proc/net/tcp`, providing zero-latency socket states.

```bash
# 1. Summary of all socket states
ss -s

# 2. List all listening TCP/UDP sockets with process names and PIDs
sudo ss -tulpn

# 3. Filter sockets by specific TCP connection states
ss -tan state established
ss -tan state time-wait
ss -tan state close-wait
ss -tan state syn-recv

# 4. Inspect TCP internal socket buffers and congestion metrics for port 3000
ss -ti '( dport = :3000 or sport = :3000 )'
```

#### Socket State Operational Triage:
- `TIME_WAIT`: Normal termination state for the endpoint that initiated active close. Sockets remain in this state for $2 \times \text{MSL}$ (60s in Linux) to guarantee delivery of delayed packets.
- `CLOSE_WAIT`: The remote client closed the connection, but the local application has **not** closed its socket descriptor. A build-up of `CLOSE_WAIT` sockets indicates an application bug (missing `socket.end()` / `socket.destroy()` in error handling branches).
- `SYN_RECV`: Sockets waiting for client ACK after SYN-ACK. High count indicates SYN flood attack or asymmetric routing failure.

---

### B. TCP Connection Lifecycles, TIME_WAIT & Port Exhaustion

When an application acts as an HTTP client making high-frequency outbound requests to microservices/databases without HTTP Keep-Alive connection pooling, it rapidly exhausts ephemeral ports ($65535 - 1024 = 64511$ total).

#### 1. Ephemeral Port Range Expansion
```ini
# /etc/sysctl.d/99-networking.conf
# Maximize range of available outbound ports
net.ipv4.ip_local_port_range = 1024 65535
```

#### 2. Safe TIME_WAIT Socket Recycling
```ini
# Enable safe reuse of TIME_WAIT sockets for outgoing connections (Requires timestamps)
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_timestamps = 1

# Reduce FIN timeout from default 60s to 15s to free unacknowledged sockets faster
net.ipv4.tcp_fin_timeout = 15
```
> [!CAUTION]
> **Never enable `net.ipv4.tcp_tw_recycle`**. This flag was permanently removed in Linux Kernel 4.12+ because it drops legitimate SYN packets from clients behind NAT gateways due to timestamp mismatches. Always use `net.ipv4.tcp_tw_reuse = 1`.

#### 3. Client-Side HTTP Connection Pooling (Node.js)
Prevent socket exhaustion at the application layer by reusing TCP sockets across HTTP requests:
```javascript
// http-agent-pool.js
const http = require('node:http');
const https = require('node:https');

const httpAgent = new http.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 256,
  maxFreeSockets: 64,
  timeout: 60000
});

const httpsAgent = new https.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 256,
  maxFreeSockets: 64,
  timeout: 60000
});

module.exports = { httpAgent, httpsAgent };
```

---

### C. Socket Buffer Sizing, BDP & Kernel Tuning (`sysctl`)

For high-throughput networks (10Gbps+ or high latency links), default socket buffers artificially throttle transmission speeds due to the Bandwidth-Delay Product (BDP) ceiling.

$$\text{BDP (Bytes)} = \frac{\text{Bandwidth (Bits/sec)}}{8} \times \text{Round Trip Time (RTT in seconds)}$$

*Example*: On a 10Gbps link with 20ms RTT:
$$\text{BDP} = \left(\frac{10 \times 10^9}{8}\right) \times 0.020 = 25\text{ MB}$$
If TCP socket buffer is capped at the default 4MB, maximum single-stream throughput cannot exceed $\frac{4\text{ MB}}{0.020\text{ s}} = 1.6\text{ Gbps}$.

#### Production Network Kernel Sysctl Standard (`/etc/sysctl.d/99-performance.conf`)
```ini
# Maximum socket receive/send buffer size settable via setsockopt()
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# Default socket receive/send buffer size
net.core.rmem_default = 262144
net.core.wmem_default = 262144

# TCP autotuning buffer limits: [min] [default] [max] in bytes
# (Min: 4KB, Default: 87KB/64KB, Max: 16MB)
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Enable TCP Window Scaling (RFC 1323)
net.ipv4.tcp_window_scaling = 1

# Maximum listen backlog queue for pending connection handshakes (listen())
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# Maximum number of packets queued on input interface before processing
net.core.netdev_max_backlog = 65536

# Enable TCP BBR congestion control algorithm (requires Linux 4.9+)
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
```
Apply immediately:
```bash
sudo sysctl --system
```

---

## 4. Storage & Filesystem Inode Health

### A. Disk Space vs. Inode Exhaustion Diagnostics

A filesystem can report `No space left on device` (POSIX error `ENOSPC`) even when `df -h` shows gigabytes of available storage. This occurs when all filesystem **inodes** (metadata index blocks) are consumed by millions of tiny files.

#### 1. Inode Capacity Inspection
```bash
# Compare block space vs inode allocation
df -h
df -i
```
Sample Inode Exhaustion Output:
```text
Filesystem      Inodes   IUsed   IFree IUse% Mounted on
/dev/sda1      3276800 3276800       0  100% /
```

#### 2. Locating Inode Hog Directories (High-Speed Search)
Run a single-pass directory search to count file instances across the filesystem:
```bash
# Scan and rank directories containing the highest number of file entries
sudo find / -xdev -printf '%h\n' | sort | uniq -c | sort -nr | head -n 20
```
Common Culprits:
- `/var/spool/postfix/maildrop` or `/var/spool/clientmqueue`: Uncollected system cron error mails.
- `/var/lib/php/sessions` or `/tmp`: Abandoned session files without active cron garbage collection.
- `~/.npm/_cacache` or `/root/.cache`: Unpruned package manager caches.
- `/var/lib/docker/overlay2`: Orphaned container layers from continuous builds without `docker image prune`.

---

### B. Orphaned & Open-Deleted File Diagnostics (`lsof +L1`)

When a file is deleted with `rm`, the directory entry is unlinked. However, if a running process holds an open file descriptor pointing to that inode, the kernel **will not free the underlying disk blocks** until the process closes the descriptor or terminates.

#### 1. Pinpointing Hidden Deleted Files Holding Disk Space
```bash
# Find all open files with 0 link count (unlinked/deleted from filesystem)
sudo lsof +L1

# Alternative filter with process and size breakdown
sudo lsof | grep -i '(deleted)' | sort -k 7 -n -r | head -n 20
```
Example Output:
```text
COMMAND   PID USER   FD   TYPE DEVICE   SIZE/OFF NLINK    NODE NAME
node    18420 app     3w   REG    8,1 4294967296     0 1441824 /var/log/app/debug.log (deleted)
```
*Diagnosis*: Node.js (PID 18420) holds open descriptor `3w` for a 4.2GB deleted log file. Disk space remains locked.

#### 2. Safe In-Place Truncation (Zero Downtime)
Do not abruptly kill production processes. Truncate the file directly through the proc filesystem descriptor:
```bash
# Atomically zero the contents of the held file descriptor
sudo truncate -s 0 /proc/18420/fd/3
# Or using shell redirection:
sudo sh -c '> /proc/18420/fd/3'
```
Disk space is reclaimed immediately while the application continues running uninterrupted.

---

### C. Safe Pruning & Temp Storage Maintenance

#### 1. Safe Automated Temp File Cleanup
```bash
# Safely find and delete regular files in /tmp older than 7 days
sudo find /tmp -type f -atime +7 -delete

# Safely clean orphaned systemd temp files using native systemd facility
sudo systemd-tmpfiles --clean
```

#### 2. Invariant Rules for Disk Maintenance:
1. **Never use `rm -rf /tmp/*` blindly**: Active processes maintain UNIX domain sockets in `/tmp` (e.g. `/tmp/mongodb-27017.sock`, `/tmp/pm2.sock`). Removing active sockets breaks IPC connections without warning.
2. **Always filter by file type and modification time**: `find /tmp -type f -mtime +3 -delete`.
3. **Atomic Log Zeroing**: Never delete an active log file with `rm`. Truncate it with `: > /path/to/logfile.log` or enforce logrotate with `copytruncate`.

---

## 5. Performance Triaging Flowchart & Operational Cheatsheet

### A. Rapid Production Triaging Sequence (First 60 Seconds)

```
[System Incident Alert / High Latency]
                 |
                 v
   [1. Run: uptime / vmstat 1 3]
    ├── r > nproc? ───────────────> CPU Saturation -> mpstat -P ALL 1 -> Profile Process (node / perf)
    ├── b > 0 or wa% > 20%? ──────> Disk I/O Bottleneck -> iostat -xz 1 -> pidstat -d 1 -> Storage / Queries
    └── Load High, r=0, b=0? ─────> Network / Lock Contention -> ss -s / dmesg / lock tracing
                 |
                 v
   [2. Run: free -m / smem]
    ├── available RAM < 5%? ──────> OOM Threat -> smem / smaps_rollup -> check RSS vs Leaking AnonPages
    └── si/so continuous? ────────> Swap Thrashing -> Identify high-swap PID -> tune vm.swappiness
                 |
                 v
   [3. Run: df -h && df -i]
    ├── Use% = 100%? ─────────────> Disk Space Full -> lsof +L1 (deleted files) -> du -sh /*
    └── IUse% = 100%? ────────────> Inode Exhaustion -> find / -xdev -printf '%h\n' | sort | uniq -c
                 |
                 v
   [4. Run: ss -s && ss -tulpn]
    ├── CLOSE_WAIT high? ─────────> App socket leak -> Inspect PID open FDs -> patch socket handling
    └── Port exhaustion? ─────────> Enable tcp_tw_reuse -> implement HTTP Keep-Alive connection pooling
```

---

### B. High-Precision Command Reference Table

| Diagnostic Vector | Primary Command | Target Metric / Threshold | Corrective Action |
| :--- | :--- | :--- | :--- |
| **CPU Run Queue** | `vmstat 1` | `r > nproc` | Scale horizontally, cluster mode, optimize algorithms. |
| **CPU Core Hotspots** | `mpstat -P ALL 1` | `%soft > 20%` (NIC IRQ) | Enable RSS, balance IRQ CPU affinity. |
| **I/O Latency** | `iostat -xz 1` | `await > 20ms`, `%util > 90%` | Batch disk writes, upgrade storage tier, index queries. |
| **Process I/O** | `pidstat -d 1` | `kB_wr/s` high | Pinpoint writing process, isolate offending log/write stream. |
| **Process RAM / PSS** | `smem -t -k -p` | Monotonic PSS growth | Profile heap allocations, inspect object retention graphs. |
| **Unlinked Open Files** | `lsof +L1` | `NLINK = 0` with large size | Truncate via `truncate -s 0 /proc/<pid>/fd/<fd>`. |
| **Inode Hog Dirs** | `find / -xdev -printf '%h\n' ...` | Directory with $> 100\text{k}$ files | Prune old sessions/cache files, implement retention cron. |
| **Socket States** | `ss -tan state close-wait` | Growing count | Fix unclosed socket descriptors in application code. |
| **Node Event Loop** | `monitorEventLoopDelay` | `p99 > 50ms` | Eliminate sync CPU operations, offload to worker threads. |
| **V8 GC Health** | `--trace-gc` | GC pause $> 50\text{ms}$, `mu < 0.5` | Increase `--max-old-space-size`, eliminate memory leaks. |
