---
name: incident-root-cause-debugging
description: Empirical incident management and architectural debugging protocol for production outages, root-cause isolation, git bisect triage, minimal diff remediation, safe rollbacks, and post-mortem invariant synthesis.
---

# Incident Response & Root Cause Debugging Protocol

High-precision, empirical triage and debugging framework for isolating root causes during production incidents, eliminating speculative churn, executing zero-downtime rollbacks, and codifying architectural invariants.

---

## 1. The Non-Overthinking Incident Triage Algorithm

Production outages demand deterministic diagnosis over speculative branching. The objective is to move from symptom to isolated mechanical failure in the minimum number of steps.

```
+------------------+     +------------------------+     +----------------------+     +------------------+
| 1. Empirical     | --> | 2. Freeze & State      | --> | 3. Isolate Single    | --> | 4. Minimal Diff  |
| Capture & Verify |     |    Preservation        |     |    Root Condition    |     |    Remediation   |
+------------------+     +------------------------+     +----------------------+     +------------------+
```

### A. Step 1: Empirical Capture & Reproduction
Reject all anecdotal or subjective failure reports ("the app feels slow", "some users report 500 errors"). Convert symptoms into raw, verifiable telemetry:

1. **Exact Timestamp & Span ID / Request ID**: Match client-side failure to server trace.
2. **Raw Log Extraction**:
   ```bash
   # Systemd service journal (last 200 lines with timestamps, no pager truncation)
   journalctl -u <service_name> -n 200 --no-pager --output=short-iso

   # PM2 error streams
   pm2 logs <app_name> --err --lines 100 --nostream

   # Nginx error log filtered for 5xx origins
   tail -n 200 /var/log/nginx/error.log | grep -E "\[error\]|\[crit\]"

   # Docker container runtime error output
   docker logs --tail 200 --timestamps <container_id>
   ```
3. **Deterministic Reproducer Construction**:
   Construct the exact minimal `curl` command or automated test script that triggers the failure with 100% fidelity:
   ```bash
   curl -s -w "\nHTTP_STATUS: %{http_code}\nTIME_TOTAL: %{time_total}s\n" \
     -X POST "http://127.0.0.1:3000/api/v1/resource" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TEST_TOKEN" \
     -d '{"target_id": "exact-failing-payload"}'
   ```

### B. Step 2: State Capture Before Mutation
**Rule**: Never blindly restart, kill, or mutate a failing system without capturing ephemeral state. A blind restart clears the memory leak, deadlock state, or process table needed for root-cause diagnosis.

```bash
# 1. Capture process hierarchy and resource consumption
ps aux --sort=-%mem | head -n 20
ps aux --sort=-%cpu | head -n 20

# 2. Check open file descriptors, socket allocations, and connection states
lsof -p <PID> | wc -l
ss -tulpn | grep :<PORT>
netstat -an | awk '/tcp/ {print $6}' | sort | uniq -c

# 3. Capture thread/heap dump if runtime permits
# Node.js:
kill -USR1 <PID> # Triggers inspector or heap dump if configured
# Go:
curl -s http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutines.txt
# JVM:
jstack <PID> > thread_dump.txt
```

### C. Step 3: Single Root-Cause Condition Isolation
Trace backward from the stack trace or fault point to isolate the exact conditional boundary:

- **The Single-Condition Rule**: Every production failure stems from exactly one root mechanical condition (e.g., unhandled null pointer on empty database result, exhaustion of connection pool workers, or unescaped URI component).
- **Reject Speculative Branching**: Do not pursue parallel hypothetical causes ("maybe it's DNS, or maybe the cache is stale, or maybe we should upgrade Node.js"). Follow the data path:
  1. Input $\to$ 2. Validation $\to$ 3. State/DB Operation $\to$ 4. Network I/O $\to$ 5. Output.
- **Empirical 5-Whys Validation**:
  ```
  Symptom: 502 Bad Gateway from Nginx reverse proxy.
  Why 1: Node.js backend crashed on SIGSEGV / out of memory.
  Why 2: Process memory hit 1.4GB heap allocation ceiling.
  Why 3: Query SELECT * FROM audit_logs loaded 4.2 million rows into memory.
  Why 4: Pagination query omitted LIMIT/OFFSET clause when 'filter_date' was null.
  Root Cause: Missing fallback boundary check on date filter parameter.
  ```

---

## 2. Binary Search Debugging & Regression Bisection

When an issue appears after recent changes or across environment boundaries, isolate the fault vector using binary search.

### A. Git Bisect Automation with Deterministic Test Scripts
Never guess which commit broke production. Automate `git bisect` using an executable test script that returns standard POSIX exit codes (`0` = good, `1` = bad, `125` = skip/unbuildable).

```bash
# 1. Initialize bisection range
git bisect start
git bisect bad HEAD              # Current broken commit
git bisect good v1.4.0           # Last known working release/tag

# 2. Run automated bisection with reproducer script
git bisect run ./scripts/reproduce-issue.sh

# 3. Inspect the isolated regression commit
git show
git bisect reset
```

#### Reproducer Script Standard (`reproduce-issue.sh`)
```bash
#!/usr/bin/env bash
set -e

# Step 1: Clean build
npm run build --silent || exit 125 # Exit 125 tells bisect to skip unbuildable commit

# Step 2: Execute targeted unit/integration test reproducing bug
npm test -- test/regression/issue-reproduce.test.ts --silent
TEST_EXIT=$?

if [ $TEST_EXIT -eq 0 ]; then
  exit 0 # Good commit
else
  exit 1 # Bad commit (regression isolated)
fi
```

### B. Isolating Environmental vs. Codebase Failures
Use the 4-Quadrant Isolation Matrix to distinguish environment drift from codebase bugs:

| | **Code Constant** | **Code Changed** |
|---|---|---|
| **Env Constant** | **Latent Bug Triggered by Data / Clock / Boundary**<br>- Expired TLS certificate<br>- Leap year / epoch boundary<br>- DB table lock / sequence exhaustion | **Regression in Code**<br>- Git bisect immediately<br>- Minimal code patch |
| **Env Changed** | **Infrastructure Drift / Upstream Failure**<br>- Cloudflare DNS/routing changes<br>- OS library/package upgrade<br>- Disk full / Inode exhaustion<br>- Upstream API contract break | **Compound Regression**<br>- Revert code first, isolate env independently |

#### Environment Triage Diagnostic Sweep
```bash
# Storage and Inodes
df -h
df -i

# Memory, Swap, and OOM-Killer activity
free -m
dmesg -T | grep -E -i "oom|out of memory|killed process"

# Clock synchronization and drift
timedatectl status

# DNS Resolution latency and reachability
dig +trace api.internal.domain
curl -Iv https://upstream-dependency.com/health
```

---

## 3. The Minimal Diff Philosophy

In production incident remediation, **every additional line of code added to a hotfix increases failure risk exponentially**. Refactoring during an outage is architectural malpractice.

### A. The Core Invariants of Minimal Diff Fixes
1. **Zero Aesthetic Refactoring**: Variable renames, formatting re-alignments, moving functions between files, and lint fixes across untouched lines are strictly prohibited in hotfixes.
2. **Single-Site Repair**: Fix only the failing condition or guard clause.
3. **The Minimality Ladder**:
   - Level 1: Configuration / environment variable toggle (zero build overhead, instant rollback).
   - Level 2: One-line boundary check or guard clause (`if (!record) return null;`, `LIMIT 50`).
   - Level 3: Existing utility reuse (call existing battle-tested sanitizer/helper).
   - Level 4: Minimal isolated function patch (under 10 lines).

### B. Anti-Pattern vs. High-Precision Diff Comparison

#### Anti-Pattern: Speculative Refactor During Outage
```diff
--- a/src/services/billing.service.ts
+++ b/src/services/billing.service.ts
@@ -12,18 +12,32 @@
-export class BillingService {
-  async processPayment(userId: string, amount: number) {
-    const user = await db.users.findById(userId);
-    return stripe.charges.create({ customer: user.stripeId, amount });
-  }
-}
+export interface PaymentContext {
+  userId: string;
+  amountInCents: number;
+  currency?: string;
+}
+
+export class BillingService {
+  private readonly defaultCurrency = 'USD';
+
+  constructor(private readonly paymentGateway: StripeGateway) {}
+
+  async processPayment(context: PaymentContext): Promise<TransactionResult> {
+    const user = await this.resolveCustomer(context.userId);
+    if (!user?.stripeId) throw new BillingException('Missing stripe ID');
+    return this.paymentGateway.execute({
+      customer: user.stripeId,
+      amount: context.amountInCents,
+      currency: context.currency ?? this.defaultCurrency
+    });
+  }
```
*Risk*: Modifies interface signatures, introduces new classes, alters runtime dependencies across downstream callers.

#### High-Precision Minimal Diff: Root Cause Fix
```diff
--- a/src/services/billing.service.ts
+++ b/src/services/billing.service.ts
@@ -14,3 +14,5 @@ export class BillingService {
   async processPayment(userId: string, amount: number) {
     const user = await db.users.findById(userId);
+    if (!user || !user.stripeId) {
+      throw new Error(`Payment failed: customer ${userId} has no valid Stripe ID`);
+    }
     return stripe.charges.create({ customer: user.stripeId, amount });
   }
```
*Result*: Exact bug resolved in 4 lines. Zero blast radius on existing callers.

---

## 4. Safe Rollback & Mitigation Invariants

When root-cause isolation exceeds the Mean-Time-To-Mitigate (MTTM) budget, immediate, non-destructive rollback must take precedence over live debugging.

### A. Non-Destructive Deployment Architecture
Zero-downtime rollbacks require atomic pointer switching rather than git checkouts on live servers.

```
/srv/app/
├── current -> /srv/app/releases/20260901_180000 (Active release)
└── releases/
    ├── 20260901_120000 (Previous stable release - rollback target)
    └── 20260901_180000 (Current buggy release)
```

#### Instant Atomic Rollback Command
```bash
# 1. Atomically switch symlink to previous verified release
ln -sfn /srv/app/releases/20260901_120000 /srv/app/current

# 2. Reload application runtime without dropping active connections
pm2 reload ecosystem.config.js --update-env

# 3. Empirically verify health endpoint
curl -f http://127.0.0.1:3000/api/health || echo "HEALTHCHECK_FAILED"
```

### B. Database Backward-Compatibility Invariant (The Expand & Contract Rule)
A rollback will fail catastrophically if the new release introduced destructive database schema changes that broken the old code.

**The Golden Rule**: Application code version $N$ and version $N-1$ must both run concurrently against database schema $M$.

```
Phase 1 (Release 1): EXPAND
- Add new nullable column / new table
- Code writes to both old and new columns, reads from old
- Safe to rollback: Old code works with nullable column present

Phase 2 (Background): MIGRATE
- Asynchronous backfill script migrates historical records
- No application downtime, no schema locks

Phase 3 (Release 2): SWITCH READS
- Code reads from new column
- Safe to rollback: Fallback code still has access to dual-written data

Phase 4 (Release 3): CONTRACT
- Drop legacy column / constraint in separate maintenance release
```

#### Prohibited Actions During Incident Hotfixes
1. `DROP TABLE` or `DROP COLUMN` in production during incident mitigation.
2. `ALTER TABLE ADD COLUMN ... NOT NULL` without `DEFAULT` value (locks table and breaks older releases).
3. Renaming columns or tables synchronously.

---

## 5. Post-Mortem & Autonomous Learning Synthesis

An incident is not closed until the latent architectural gap is permanently closed through an automated invariant.

### A. Fluff-Free Incident Post-Mortem Standard

Every post-mortem document must contain only factual, non-defensive technical statements:

```markdown
# Incident Report: [YYYY-MM-DD] - [Brief Failure Descriptor]

## 1. Metrics & Timeline (UTC)
- T0 (Incident Ingress): 14:02:11 - Deploy commit `8f2a1c` activated.
- T1 (Alert Fired): 14:04:30 - Cloudflare 5xx rate exceeded 1.5% threshold.
- T2 (Root Cause Isolated): 14:11:05 - Stack trace verified unhandled null in `billing.service.ts:15`.
- T3 (Mitigation Deployed): 14:14:20 - Hotfix commit `3c4d5e` deployed via minimal diff.
- T4 (Full Resolution): 14:16:00 - 5xx rate returned to baseline (0.001%).

## 2. Exact Mechanical Root Cause
A null user record occurred when users deleted their accounts during pending background webhook events. The webhook processor called `db.users.findById` without checking for null return value before reading `user.stripeId`, causing uncaught exception and process crashes.

## 3. What Failed in the Pipeline
- Unit test suite lacked a test case where `findById` returns `null`.
- TypeScript strict null checks (`strictNullChecks: true`) were disabled in `tsconfig.json`.

## 4. Permanent Remediation Invariants
1. [Code] Added guard clause and null safety test in `billing.service.test.ts`.
2. [Compiler] Enabled `"strictNullChecks": true` in project root `tsconfig.json`.
3. [CI] Added automated check rejecting pull requests with disabled strict compiler options.
```

### B. Autonomous Self-Learning Loop
When an incident is resolved:
1. **Extract Invariant**: Transform the isolated root cause into a deterministic check or rule.
2. **Codify into Knowledge Base**: Update `SKILL.md` or `AGENTS.md` with the verified pattern.
3. **Verify Zero Hallucination**: Only document failure modes and solutions that were empirically reproduced and verified with tool output.
