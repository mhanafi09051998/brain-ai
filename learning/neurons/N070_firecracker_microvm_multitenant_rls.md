# N070: Firecracker MicroVM Sandboxing, Jailer Confinement & Multi-Tenant RLS Sharding

- **Kategori:** Systems Virtualization, Multi-Tenancy Architecture, Kernel Security & Isolation
- **Tanggal Sintesis:** 2026-08-27
- **Status:** Active Operational Invariant
- **Synaptic Links:** [`N014`](file:///D:/GEMINI-HANAFI/learning/neurons/N014_zero_trust_security_and_cryptography.md), [`N023`](file:///D:/GEMINI-HANAFI/learning/neurons/N023_zero_day_kernel_defense.md), [`N037`](file:///D:/GEMINI-HANAFI/learning/neurons/N037_wasm_wasi_microvm_sandboxing.md)

---

## 🎯 1. Multi-Tenant Isolation Architecture

```
[Untrusted Multi-Tenant Workload]
               │
               ▼
┌────────────────────────────────────────────────────────┐
│ COMPUTE LAYER: Firecracker MicroVM + Jailer Boundary   │
│  - Cold Start < 5ms | Base Memory ~5MB per VM         │
│  - Namespaces: PID, NET, MNT, IPC, UTS, USER           │
│  - cgroups v2: cpu.max, memory.max, memory.high        │
│  - Seccomp-BPF: Whitelisted KVM ioctl, epoll, VirtIO   │
│  - Chroot Jail + Dropped Privileges (UID/GID 10001)    │
└────────────────────────────────────────────────────────┘
               │
               │ (gRPC / mTLS over virtio-vsock / Unix Socket)
               ▼
┌────────────────────────────────────────────────────────┐
│ DATA LAYER: PostgreSQL Multi-Tenant Isolation Engine   │
│  - Tier 1 (Shared Schema): Row-Level Security (RLS)    │
│    FORCE ROW LEVEL SECURITY + SET LOCAL tenant_id      │
│  - Tier 2 (Enterprise): Schema-per-Tenant Routing      │
│    search_path = 'tenant_xyz', 'public'                │
│  - Connection Pool Sanitation: PgBouncer DISCARD ALL   │
└────────────────────────────────────────────────────────┘
```

---

## 📐 2. Core Mathematical & Security Invariants

### 2.1. MicroVM Provisioning Density Invariant
Kapasitas maksimal MicroVM instan pada bare-metal node dihitung deterministik:

$$N_{\text{vms}} = \min \left( \left\lfloor \frac{M_{\text{host}} - M_{\text{kernel\_reserve}}}{M_{\text{vm\_overhead}} + M_{\text{guest\_limit}}} \right\rfloor, \left\lfloor \frac{C_{\text{cores}} \times \Phi_{\text{oversubscription}}}{C_{\text{vcpu\_per\_vm}}} \right\rfloor \right)$$

*Di mana $M_{\text{vm\_overhead}} \approx 5\text{MB}$, cold boot latency $T_{\text{boot}} \le 5\text{ms}$ memanfaatkan uncompressed minimal `vmlinux` kernel.*

### 2.2. Jailer Seccomp-BPF & Namespace Confinement
Eksekusi VMM Firecracker wajib di-enforce dalam sandbox Jailer sebelum membuka KVM:
1. **Namespaces**: `CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWIPC | CLONE_NEWUTS | CLONE_NEWUSER`.
2. **Resource Capping (cgroups v2)**:
   - `cpu.max = "100000 100000"` (1 vCPU quota per 100ms period).
   - `memory.high` memicu proactive asynchronous page reclaim sebelum `memory.max` memicu OOM killer.
3. **Seccomp-BPF Action**: `SECCOMP_RET_KILL_PROCESS` untuk syscall di luar whitelist minimal (`epoll_wait`, `read`, `write`, `ioctl` KVM).

### 2.3. Postgres Row-Level Security (RLS) Policy & Leak Guard
Mencegah data leakage lintas tenant pada database pooling:

```sql
-- 1. Enable RLS and force it even for table owner (prevent accidental superuser leaks)
ALTER TABLE tenant_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_documents FORCE ROW LEVEL SECURITY;

-- 2. Tenant isolation policy using session-level config
CREATE POLICY tenant_isolation_policy ON tenant_documents
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
```

---

## 🔍 3. Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Preventive Invariant |
| :--- | :--- | :--- |
| **RLS Session Leak via Connection Pooling** | PgBouncer / Connection Pool mengembalikan koneksi yang masih memiliki `SET app.current_tenant_id` dari request sebelumnya. | **Strict Transaction Scope**: Gunakan `SET LOCAL app.current_tenant_id = '...'` di dalam block `BEGIN ... COMMIT`. Terapkan `DISCARD ALL` saat pool release. |
| **Host Kernel Privilege Escalation** | Kerentanan 0-day KVM dieksploitasi oleh guest VM code. | **Defense-in-Depth**: VMM berjalan sebagai non-root unprivileged UID di dalam chroot jail kosong tanpa perangkat fisik (hanya VirtIO over MMIO). |
| **Noisy Neighbor Memory Thrashing** | Satu tenant mengonsumsi buffer memori berlebihan, memperlambat tenant lain. | Gunakan cgroups v2 `memory.high` throttling dan swap limit zero (`memory.swap.max = 0`). |
| **Search Path Injection (Schema Routing)** | Tenant ID tidak disanitasi saat menyusun query `SET search_path`. | Gunakan identifier quoting eksplisit: `SET LOCAL search_path = quote_ident($1), 'public'` via parameter binding. |

---

## ⚡ 4. Reference Implementation: Multi-Tenant RLS Context Manager & Jailer Runner

### 4.1. PostgreSQL RLS Transactional Context (Python Async)

```python
"""Multi-tenant isolation harness with scoped transaction settings and pool leak guard."""
import uuid
from contextlib import asynccontextmanager
import asyncpg

class TenantIsolationManager:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @asynccontextmanager
    async def tenant_scope(self, tenant_id: uuid.UUID):
        """Enforces tenant RLS within an isolated transaction scope."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # SET LOCAL ensures config is automatically purged upon COMMIT/ROLLBACK
                await conn.execute("SET LOCAL app.current_tenant_id = $1;", str(tenant_id))
                try:
                    yield conn
                finally:
                    # Invariant defense: Explicitly clear setting to prevent ambient leakage
                    await conn.execute("RESET app.current_tenant_id;")

    async def execute_isolated_query(self, tenant_id: uuid.UUID, query: str, *args):
        async with self.tenant_scope(tenant_id) as conn:
            return await conn.fetch(query, *args)
```

### 4.2. Firecracker Jailer Execution Recipe (Production Invariant)

```bash
#!/usr/bin/env bash
set -euo pipefail

VM_ID="tenant-vm-$(uuidgen | cut -d'-' -f1)"
CHROOT_BASE="/srv/jailer"
UID_GID="10001"

# Invariant: Launch Firecracker exclusively via the Jailer binary
/usr/bin/jailer \
    --id "${VM_ID}" \
    --exec-file /usr/bin/firecracker \
    --uid "${UID_GID}" \
    --gid "${UID_GID}" \
    --chroot-base-dir "${CHROOT_BASE}" \
    --cgroup-version 2 \
    --daemonize \
    -- \
    --api-sock /run/firecracker.socket \
    --seccomp-level 2
```

---

## 🔒 5. Disiplin Eksekusi (Zero-Overengineering & Ponytail Invariants)

1. **Hardware-Assisted Over Containerization:** Untuk untrusted code execution (user scripts, plugin sandbox), gunakan Firecracker KVM MicroVM, bukan unprivileged Docker/runc containers.
2. **Zero Ambient Authority in Data Access:** Database pool tidak boleh mempercayai klaim tenant di memory aplikasi; database engine wajib memvalidasi setiap baris via Postgres RLS Policy.
3. **Single Root Fix Discipline:** Cegah kebocoran multi-tenant pada layer atomik database (`SET LOCAL` + RLS `FORCE`) dan kernel boundary (Jailer cgroups/seccomp), bukan validasi parsial di puluhan API handler.
4. **File Size Limit:** Seluruh dokumen dan reference code $<300$ baris per file.
