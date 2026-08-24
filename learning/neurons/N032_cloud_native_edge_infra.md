# Neuron N032: Cloud-Native Edge Infrastructure & Zero-Downtime Operations

- **Kategori:** Cloud-Native Architecture, High-Availability Edge & Container Hardening
- **Tanggal Sintesis:** 2026-08-24
- **Status:** Active Operational Invariant
- **Rujukan Invarian:** Caddy 2.8+ HTTP/3 (QUIC / UDP 443 / 0-RTT TLS 1.3 / Automated Certificate Authority ACME), Docker Distroless Multi-Stage Hardening (OCI / Scratch / Non-Root UID 65532 / Read-Only RootFS), PM2 Cluster Mode & Zero-Downtime Supervision (Graceful Rolling Reload / Connection Draining / Liveness-Readiness Probes), Linux Namespaces & cgroups v2 Kernel Sandboxing (PID, NET, MNT, IPC, UTS, USER, CPU/Memory strict quotas).

---

## 🎯 5 Pilar & Invarian Operasional Edge & Containerization

### 1. Modern Edge Ingress & Transport Layer (Caddy 2.8+ HTTP/3 QUIC & TLS 1.3 0-RTT)
- **HTTP/3 & QUIC Transport Invariant**:
  - Protokol QUIC berjalan di atas UDP port 443, mengeliminasi masalah *Head-of-Line (HoL) Blocking* pada level TCP transport stream.
  - Mendukung *Connection Migration* berbasis Connection ID (CID) 64/128-bit: pergantian rute IP/jaringan klien (Wi-Fi $\leftrightarrow$ 4G/5G) tidak memutus stream HTTP/3 aktif.
  - Header `Alt-Svc: h3=":443"; ma=2592000` wajib disertakan pada seluruh response HTTP/1.1 & HTTP/2 untuk memfasilitasi upgrade otomatis ke HTTP/3 pada request berikutnya.
- **Automated ACME & Strict TLS 1.3 Zero-RTT Invariant**:
  - Manajemen sertifikat otomatis penuh (Let's Encrypt / ZeroSSL) via ACME v2 HTTP-01 / TLS-ALPN-01 challenge dengan automated renewal pada sisa masa berlaku $\le 30$ hari.
  - Enkripsi modern TLS 1.3 dengan cipher suites terverifikasi: `AEAD_AES_128_GCM_SHA256`, `AEAD_AES_256_GCM_SHA384`, `AEAD_CHACHA20_POLY1305_SHA256`.
  - OCSP Stapling diaktifkan secara wajib (*Must-Staple*) untuk mengeliminasi latency validasi sertifikat sisi klien.
- **Edge Reverse Proxy, Dynamic Load Balancing & Circuit Breaking**:
  - Algoritma routing deterministik: *Round Robin*, *Least Connections*, dan *Consistent Header/IP Hash*.
  - Passive & Active Health Checking: Upstream yang mengembalikan status $5xx \ge 3$ kali berturut-turut langsung ditandai `UNHEALTHY` dan diisolasi dari routing pool selama interval cooldown $T_{\text{cooldown}}$.
  - Token Bucket Rate Limiting per Client IP/Fingerprint pada level edge L4/L7 untuk mitigasi DDoS dan brute-force attack.

### 2. Multi-Stage Distroless Hardening & Minimal Attack Surface
- **Multi-Stage Build Separation**:
  - **Stage 1 (Builder)**: Menjalankan compiler toolchain, package manager (`npm`, `pip`, `cargo`), dan devDependencies untuk memproduksi compiled artifact / production node_modules.
  - **Stage 2 (Runtime)**: Image final berbasis `gcr.io/distroless/nodejs22-debian12`, `gcr.io/distroless/static-debian12`, atau `scratch`.
- **Zero-Shell & Zero-Package-Manager Hardening**:
  - Image runtime sama sekali tidak memiliki shell (`/bin/sh`, `/bin/bash`), package manager (`apt`, `apk`, `yum`), compiler, maupun utilitas sistem (`curl`, `wget`, `nc`).
  - Menghentikan eksploitasi Remote Code Execution (RCE) berbasis command injection dan reverse shell secara deterministik di level filesystem.
- **Immutable & Non-Root Least-Privilege Execution**:
  - Eksekusi wajib menggunakan unprivileged user: `USER nonroot:nonroot` (UID/GID `65532:65532`).
  - Container root filesystem di-mount sebagai **Read-Only** (`read_only_rootfs: true`).
  - Direktori temporer (`/tmp`, `/run`) dialokasikan melalui `tmpfs` in-memory dengan opsi keamanan ketat: `noexec, nosuid, nodev, size=64m`.

### 3. Zero-Downtime Cluster Supervision & Process Lifecycle (PM2 Orchestration)
- **Multi-Core Worker Cluster Invariant**:
  - Memanfaatkan Node.js `cluster` module untuk membagi beban kerja ke seluruh logical CPU cores (`instances: "max"` atau integer) tanpa konflik port jaringan (`SO_REUSEPORT` abstraction).
- **Graceful Rolling Reload & Zero-Drop Connection Draining**:
  - Siklus deployment tanpa downtime (*Zero-Downtime Rolling Reload*):
    1. Orchestrator memicu restart worker secara berurutan (*rolling reload* satu per satu).
    2. Worker lama menerima sinyal `SIGINT`, berhenti menerima request baru dari reverse proxy/cluster master, dan memulai fase draining untuk menyelesaikan seluruh *in-flight requests* aktif.
    3. Worker baru di-*spawn*, menginisialisasi database pool dan cache warmup.
    4. Setelah worker baru mengirim sinyal `process.send('ready')` (atau `wait_ready: true`), traffic dialihkan ke worker baru.
    5. Jika worker lama tidak selesai dalam `kill_timeout` (default 5000ms), sinyal `SIGKILL` dikirim secara paksa.
- **Autonomous Recovery & Memory Leak Ceiling**:
  - Parameter `max_memory_restart: "450M"`: Jika heap memory worker melebihi batas aman karena fragmentation atau memory leak, PM2 merestart worker secara bergilir tanpa interupsi layanan.
  - Exponential restart backoff jika terjadi failure berulang (*crash loop protection*).

### 4. Linux Kernel Namespaces & cgroups v2 Sandboxing
- **6 Dimensi Isolasi Linux Namespaces**:
  1. **PID Namespace**: Memetakan proses container sebagai PID 1 di dalam namespace, menyembunyikan proses host dan container lain.
  2. **NET Namespace**: Stack jaringan terisolasi dengan virtual ethernet pair (`veth`), routing table, dan firewall iptables/nftables mandiri.
  3. **MNT Namespace**: Mount table terisolasi via `pivot_root`, mengisolasi filesystem container dari root filesystem host.
  4. **IPC Namespace**: Isolasi System V IPC dan POSIX message queue / shared memory.
  5. **UTS Namespace**: Hostname dan NIS domain terisolasi per container.
  6. **USER Namespace**: Memetakan UID 0 (root) di dalam namespace container ke unprivileged UID (misal `10001`) di level kernel host.
- **cgroups v2 Strict Resource Governance**:
  - **CPU Hard Limit**: `cpu.max = "50000 100000"` (maksimal 50% dari 1 CPU core per interval 100ms) untuk mencegah CPU starvation.
  - **Memory Hard Ceiling**: `memory.max = "512M"`, `memory.high = "440M"` (memicu asynchronous reclaim sebelum OOM killer), dan `memory.swap.max = "0"` (mencegah disk thrashing).
- **Linux Capabilities Dropping & Seccomp Profiling**:
  - `CapDrop = ["ALL"]`, hanya mengizinkan capabilities mutlak yang dibutuhkan (misal: `CAP_NET_BIND_SERVICE`).
  - Blokir syscall berbahaya via Seccomp filter: cegah `ptrace`, `sys_chroot`, `kexec_load`, dan modifikasi kernel module.

### 5. Autonomous Edge SRE & High-Availability Playbook
- **Tri-Probe Health Architecture**:
  - **Startup Probe**: Memverifikasi inisialisasi awal aplikasi (skema database migration, config loading). Probes lain dinonaktifkan hingga probe ini sukses.
  - **Liveness Probe**: Memeriksa apakah event loop dan process thread responsif. Kegagalan $\implies$ restart proses container.
  - **Readiness Probe**: Memeriksa ketersediaan dependensi downstream (database, Redis, upstream microservice). Kegagalan $\implies$ isolasi dari ingress load balancer tanpa restart proses.

---

## 🛠️ Production Configuration Blueprints

### 1. Edge Ingress Caddyfile Blueprint (Caddy 2.8+ HTTP/3 + Security Headers + Passive Healthcheck)
```caddy
{
    email ops@zolu.my.id
    admin off
    servers {
        protocols h1 h2 h3
        strict_sni_host insecure_off
    }
}

prod.zolu.my.id {
    # Automatic HTTP/3 Alt-Svc & TLS 1.3
    encode zstd gzip

    # Zero-Trust Edge Security Headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self';"
        -Server
    }

    # Upstream Reverse Proxy with Passive Health Checking & Load Balancing
    reverse_proxy 127.0.0.1:3012 127.0.0.1:3013 {
        lb_policy least_conn
        fail_duration 10s
        max_fails 3
        unhealthy_status 5xx
        
        transport http {
            keepalive 30s
            keepalive_idle_conns 100
        }
    }
}
```

### 2. Multi-Stage Distroless Dockerfile Blueprint
```dockerfile
# Stage 1: Build & Dependency Resolution
FROM node:22-alpine AS builder
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY . .
RUN npm run build --if-present

# Stage 2: Distroless Minimal Secure Runtime
FROM gcr.io/distroless/nodejs22-debian12:nonroot
WORKDIR /app
COPY --from=builder --chown=nonroot:nonroot /app/node_modules ./node_modules
COPY --from=builder --chown=nonroot:nonroot /app/dist ./dist
COPY --from=builder --chown=nonroot:nonroot /app/package.json ./package.json

USER nonroot:nonroot
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000
ENTRYPOINT ["/nodejs/bin/node", "dist/server.js"]
```

### 3. PM2 Zero-Downtime Cluster Blueprint (`ecosystem.config.js`)
```javascript
module.exports = {
  apps: [
    {
      name: "claudia-edge-service",
      script: "./dist/server.js",
      instances: "max",
      exec_mode: "cluster",
      wait_ready: true,
      listen_timeout: 8000,
      kill_timeout: 5000,
      max_memory_restart: "450M",
      exp_backoff_restart_delay: 100,
      env: {
        NODE_ENV: "production",
        PORT: 3000
      }
    }
  ]
};
```

---

## 💻 Algoritma & Executable Invariant Verification (Pure Python Standard Library)

Modul Python murni (stdlib zero-dependency) untuk memverifikasi Invarian Edge Ingress HTTP/3, Distroless Sandbox, PM2 Zero-Downtime Cluster, dan Tri-Probe Engine:

```python
"""
Neuron N032: Cloud-Native Edge Infrastructure & Zero-Downtime Operations
Pure Python Standard Library - Executable Invariant Verification Suite
"""

import sys
import time
import math
import hashlib
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =====================================================================
# 1. Edge Ingress Router (HTTP/3 QUIC & Dynamic Reverse Proxy)
# =====================================================================
class EdgeIngressRouter:
    """Simulasi Edge Ingress Router Caddy 2.8+ HTTP/3 QUIC & Load Balancer."""
    def __init__(self, rate_limit_rps: float = 100.0, burst: int = 20):
        self.rate_limit_rps = rate_limit_rps
        self.burst = burst
        self.token_buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_update)
        self.upstreams: Dict[str, Dict[str, Any]] = {}  # target -> {status, fails, cooldown_until, active_conns}
        self.tls_version = "TLS 1.3"
        self.alpn_protocols = ["h3", "h2", "http/1.1"]

    def register_upstream(self, target: str):
        self.upstreams[target] = {
            "status": "HEALTHY",
            "fails": 0,
            "cooldown_until": 0.0,
            "active_conns": 0
        }

    def check_rate_limit(self, client_ip: str, now: float) -> bool:
        """Token bucket rate limiter L7."""
        if client_ip not in self.token_buckets:
            self.token_buckets[client_ip] = (float(self.burst), now)
        
        tokens, last_time = self.token_buckets[client_ip]
        elapsed = max(0.0, now - last_time)
        tokens = min(float(self.burst), tokens + elapsed * self.rate_limit_rps)
        
        if tokens >= 1.0:
            self.token_buckets[client_ip] = (tokens - 1.0, now)
            return True
        else:
            self.token_buckets[client_ip] = (tokens, now)
            return False

    def select_upstream(self, now: float) -> Optional[str]:
        """Least connection load balancing dengan passive circuit breaker."""
        healthy_candidates = []
        for target, state in self.upstreams.items():
            if state["status"] == "UNHEALTHY" and now >= state["cooldown_until"]:
                state["status"] = "HEALTHY"
                state["fails"] = 0
            
            if state["status"] == "HEALTHY":
                healthy_candidates.append((state["active_conns"], target))
        
        if not healthy_candidates:
            return None
        
        healthy_candidates.sort(key=lambda x: x[0])
        chosen = healthy_candidates[0][1]
        self.upstreams[chosen]["active_conns"] += 1
        return chosen

    def report_response(self, target: str, status_code: int, now: float):
        if target not in self.upstreams:
            return
        state = self.upstreams[target]
        state["active_conns"] = max(0, state["active_conns"] - 1)
        
        if status_code >= 500:
            state["fails"] += 1
            if state["fails"] >= 3:
                state["status"] = "UNHEALTHY"
                state["cooldown_until"] = now + 10.0  # 10s cooldown
        else:
            state["fails"] = 0


# =====================================================================
# 2. Distroless Container Sandbox & Security Isolation
# =====================================================================
class DistrolessSandboxManager:
    """Verifikasi dan penegakan isolasi Linux Namespaces & Distroless Container."""
    def __init__(self, image_type: str, uid: int, gid: int, read_only_root: bool):
        self.image_type = image_type  # 'distroless', 'alpine', 'ubuntu'
        self.uid = uid
        self.gid = gid
        self.read_only_root = read_only_root
        self.namespaces = {"PID", "NET", "MNT", "IPC", "UTS", "USER"}
        self.capabilities_retained: Set[str] = set()
        self.seccomp_blocked_syscalls = {"ptrace", "sys_chroot", "kexec_load", "init_module"}
        self.tmpfs_mounts: Dict[str, str] = {}  # path -> options

    def add_tmpfs_mount(self, path: str, options: str):
        self.tmpfs_mounts[path] = options

    def retain_capability(self, cap: str):
        self.capabilities_retained.add(cap)

    def validate_security_invariants(self) -> Dict[str, bool]:
        """Memverifikasi bahwa container memenuhi standar Zero-Trust Distroless."""
        is_non_root = (self.uid == 65532 and self.gid == 65532) or (self.uid > 1000)
        is_read_only = self.read_only_root
        has_safe_tmpfs = "/tmp" in self.tmpfs_mounts and "noexec" in self.tmpfs_mounts["/tmp"]
        no_dangerous_caps = "CAP_SYS_ADMIN" not in self.capabilities_retained and "CAP_NET_ADMIN" not in self.capabilities_retained
        is_distroless = self.image_type.lower() == "distroless"
        
        return {
            "non_root_enforced": is_non_root,
            "read_only_rootfs": is_read_only,
            "tmpfs_noexec_mounted": has_safe_tmpfs,
            "least_privilege_caps": no_dangerous_caps,
            "distroless_minimal_attack_surface": is_distroless,
            "all_namespaces_isolated": len(self.namespaces) == 6
        }


# =====================================================================
# 3. PM2 Cluster Supervisor & Zero-Downtime Rolling Reload
# =====================================================================
class PM2ProcessWorker:
    """Representasi proses worker dalam cluster mode."""
    def __init__(self, pid: int, port: int):
        self.pid = pid
        self.port = port
        self.state = "STARTING"  # 'STARTING', 'READY', 'DRAINING', 'STOPPED'
        self.memory_bytes = 50 * 1024 * 1024  # 50MB baseline
        self.active_requests = 0
        self.created_at = time.time()

    def mark_ready(self):
        self.state = "READY"

    def start_draining(self):
        self.state = "DRAINING"


class PM2ClusterSupervisor:
    """Supervisor cluster zero-downtime rolling reload & memory protection."""
    def __init__(self, target_instances: int = 4, max_memory_mb: float = 450.0, kill_timeout_sec: float = 5.0):
        self.target_instances = target_instances
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.kill_timeout_sec = kill_timeout_sec
        self.workers: Dict[int, PM2ProcessWorker] = {}
        self.next_pid = 1000

    def spawn_worker(self, port: int) -> PM2ProcessWorker:
        self.next_pid += 1
        worker = PM2ProcessWorker(pid=self.next_pid, port=port)
        self.workers[worker.pid] = worker
        return worker

    def initialize_cluster(self, base_port: int = 3000):
        for i in range(self.target_instances):
            w = self.spawn_worker(port=base_port + i)
            w.mark_ready()

    def zero_downtime_rolling_reload(self, base_port: int = 3000) -> List[str]:
        """Protokol rolling reload: spawn worker baru, warm up, drain worker lama, terminate."""
        events = []
        old_pids = list(self.workers.keys())
        
        for i, old_pid in enumerate(old_pids):
            old_worker = self.workers[old_pid]
            # 1. Spawn replacement worker
            new_worker = self.spawn_worker(port=base_port + 100 + i)
            events.append(f"Spawned new worker PID {new_worker.pid}")
            
            # 2. Warm up & mark ready
            new_worker.mark_ready()
            events.append(f"Worker PID {new_worker.pid} is READY to accept traffic")
            
            # 3. Drain old worker
            old_worker.start_draining()
            events.append(f"Worker PID {old_worker.pid} entered DRAINING mode")
            
            # 4. Finish in-flight requests & stop
            old_worker.active_requests = 0
            old_worker.state = "STOPPED"
            del self.workers[old_worker.pid]
            events.append(f"Worker PID {old_worker.pid} gracefully STOPPED")
            
        return events

    def check_memory_ceilings(self) -> List[int]:
        """Periksa memory leak dan trigger restart jika melebihi ambang batas."""
        restarted = []
        for pid, worker in list(self.workers.items()):
            if worker.memory_bytes > self.max_memory_bytes:
                # Trigger graceful restart
                new_w = self.spawn_worker(worker.port)
                new_w.mark_ready()
                worker.state = "STOPPED"
                del self.workers[pid]
                restarted.append(pid)
        return restarted


# =====================================================================
# 4. Tri-Probe Health Engine (Startup, Liveness, Readiness)
# =====================================================================
class HealthProbeEngine:
    """Manajemen siklus hidup container via Tri-Probe Engine."""
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.startup_passed = False
        self.consecutive_liveness_fails = 0
        self.consecutive_readiness_fails = 0
        self.is_live = True
        self.is_ready = False

    def probe_startup(self, db_migrated: bool, config_loaded: bool) -> bool:
        if db_migrated and config_loaded:
            self.startup_passed = True
            self.is_ready = True
            return True
        return False

    def probe_liveness(self, event_loop_lag_ms: float) -> bool:
        """Liveness gagal jika event loop terblokir (> 500ms)."""
        if not self.startup_passed:
            return True  # Liveness ditahan selama startup
        
        if event_loop_lag_ms > 500.0:
            self.consecutive_liveness_fails += 1
            if self.consecutive_liveness_fails >= self.failure_threshold:
                self.is_live = False
        else:
            self.consecutive_liveness_fails = 0
            self.is_live = True
        return self.is_live

    def probe_readiness(self, downstream_healthy: bool) -> bool:
        """Readiness mengontrol apakah traffic boleh dialihkan ke container."""
        if not self.startup_passed:
            self.is_ready = False
            return False
            
        if not downstream_healthy:
            self.consecutive_readiness_fails += 1
            if self.consecutive_readiness_fails >= self.failure_threshold:
                self.is_ready = False
        else:
            self.consecutive_readiness_fails = 0
            self.is_ready = True
        return self.is_ready


# =====================================================================
# 5. Invariant Verification & Self-Check Suite
# =====================================================================
def verify_cloud_native_edge_invariants():
    """Unit test mandiri untuk memverifikasi kebenaran seluruh invarian N032."""
    now = 1000.0
    
    # 1. Test Edge Ingress Router & Circuit Breaker
    router = EdgeIngressRouter(rate_limit_rps=10.0, burst=5)
    router.register_upstream("127.0.0.1:3012")
    router.register_upstream("127.0.0.1:3013")
    
    # Rate limit check
    assert router.check_rate_limit("192.168.1.100", now) is True
    # Consume burst
    for _ in range(4):
        router.check_rate_limit("192.168.1.100", now)
    assert router.check_rate_limit("192.168.1.100", now) is False  # Exhausted burst
    
    # Upstream selection & circuit breaking
    up1 = router.select_upstream(now)
    assert up1 in ["127.0.0.1:3012", "127.0.0.1:3013"]
    
    # Trigger 3 consecutive 502 Bad Gateway failures on 3012
    router.report_response("127.0.0.1:3012", 502, now)
    router.report_response("127.0.0.1:3012", 502, now)
    router.report_response("127.0.0.1:3012", 502, now)
    assert router.upstreams["127.0.0.1:3012"]["status"] == "UNHEALTHY"
    
    # Next selection must route to 3013 only
    up2 = router.select_upstream(now)
    assert up2 == "127.0.0.1:3013"
    
    # 2. Test Distroless Sandbox Security
    sandbox = DistrolessSandboxManager(
        image_type="distroless",
        uid=65532,
        gid=65532,
        read_only_root=True
    )
    sandbox.add_tmpfs_mount("/tmp", "noexec,nosuid,nodev,size=64m")
    sandbox.retain_capability("CAP_NET_BIND_SERVICE")
    
    sec_report = sandbox.validate_security_invariants()
    assert all(sec_report.values()), f"Security violation detected: {sec_report}"
    
    # 3. Test PM2 Cluster Supervisor & Zero-Downtime Rolling Reload
    supervisor = PM2ClusterSupervisor(target_instances=2, max_memory_mb=450.0)
    supervisor.initialize_cluster(base_port=3000)
    assert len(supervisor.workers) == 2
    
    reload_events = supervisor.zero_downtime_rolling_reload(base_port=3000)
    assert len(reload_events) == 8
    assert len(supervisor.workers) == 2  # Active pool tetap 2 instance tanpa penurunan
    
    # Test memory threshold auto-restart
    first_worker = list(supervisor.workers.values())[0]
    first_worker.memory_bytes = 500 * 1024 * 1024  # Leak to 500MB (> 450MB)
    restarted = supervisor.check_memory_ceilings()
    assert len(restarted) == 1
    assert len(supervisor.workers) == 2
    
    # 4. Test Tri-Probe Health Engine
    probes = HealthProbeEngine(failure_threshold=3)
    assert probes.probe_startup(db_migrated=True, config_loaded=True) is True
    assert probes.is_ready is True
    
    # High lag -> Liveness fails after 3 strikes
    probes.probe_liveness(event_loop_lag_ms=600.0)
    probes.probe_liveness(event_loop_lag_ms=600.0)
    assert probes.is_live is True  # 2 fails, still alive
    probes.probe_liveness(event_loop_lag_ms=600.0)
    assert probes.is_live is False  # 3rd fail -> triggers restart
    
    # Downstream down -> Readiness drops
    probes.probe_readiness(downstream_healthy=False)
    probes.probe_readiness(downstream_healthy=False)
    probes.probe_readiness(downstream_healthy=False)
    assert probes.is_ready is False  # Traffic evicted from LB pool
    
    print("  [✓] Neuron N032: Cloud-Native Edge Infrastructure & Zero-Downtime Invariants verified successfully.")


if __name__ == "__main__":
    verify_cloud_native_edge_invariants()
```

---

## 🔒 Disiplin Eksekusi & Invarian Produksi
- **Zero-Downtime Invariant**: Setiap perubahan versi aplikasi wajib melalui rolling reload berjenjang; koneksi klien in-flight tidak boleh dihentikan paksa tanpa fase graceful drain.
- **Attack Surface Minimization**: Dilarang menyertakan build tools atau interactive shell pada production image. Gunakan distroless OCI image dan read-only rootfs secara konsisten.
- **Edge Transport Modernization**: Prioritaskan HTTP/3 QUIC dan TLS 1.3 0-RTT di Caddy untuk latensi koneksi ultra-rendah dan ketahanan perpindahan jaringan (*connection migration*).
- **Resource Boundary Containment**: Batasi penggunaan CPU dan memory per proses menggunakan cgroups v2 dan PM2 memory ceilings untuk mencegah cascaded node failure akibat memory leak.
