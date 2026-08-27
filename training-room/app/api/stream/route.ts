import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";
import { seedDatabase } from "@/lib/seed";

export const dynamic = "force-dynamic";

const logMessages: Record<string, string[]> = {
  terminal_coding: [
    "Optimized zero-copy shell pipe stream in sub-millisecond runtime",
    "Executed detached subprocess with automated stderr recovery"
  ],
  knowledge_work: [
    "Synthesized C4 architecture model for multi-region failover",
    "Parsed and structured SEC 10-K financial balance sheet"
  ],
  novel_problem_solving: [
    "Derived inductive topological rule for ARC grid task (100% match)",
    "Applied invariant spatial rotation matrix transform"
  ],
  agentic_search: [
    "Cross-verified 3 independent research citations in DOM graph",
    "Extracted tabular data from multi-hop web retrieval"
  ],
  multidisciplinary_no_tools: [
    "Solved closed-form quantum harmonic oscillator parity formula",
    "Calculated tensor contraction in non-Euclidean manifold"
  ],
  multidisciplinary_with_tools: [
    "Executed MCTS PUCT backpropagation on multi-step reasoning tree",
    "Validated chemical reaction stoichiometry with formal theorem prover"
  ],
  computer_use: [
    "Executed desktop GUI multi-window navigation (100% pixel accurate)",
    "Automated OS terminal keyboard event dispatch without latency"
  ],
  agentic_coding_deepswe: [
    "Solved multi-file AST dependency conflict in repo model (0 regressions)",
    "Refactored circular import bottleneck into clean DAG module"
  ],
  agentic_coding_frontier: [
    "Synthesized 2D Binary Indexed Tree range update in O(log^2 N)",
    "Optimized Li Chao segment tree dynamic convex hull query"
  ],
  business_workflows: [
    "Orchestrated transactional SAGA compensation across 4 microservices",
    "Executed idempotent billing webhook retry envelope"
  ],
  legal: [
    "Audited multi-jurisdiction indemnification clause liability bounds",
    "Extracted regulatory compliance constraints without statute drift"
  ],
  health: [
    "Classified 12-lead ECG arrhythmia with 99.4% clinical precision",
    "Audited pharmacokinetic drug-drug interaction contraindications"
  ],
  biology_hard: [
    "Resolved protein folding conformation sequence for CASP-16 benchmark",
    "Mapped CRISPR-Cas9 PAM recognition sequence constraint"
  ],
  biology_human: [
    "Solved complex genomic metabolic pathway correlation",
    "Validated enzymatic active site binding affinity"
  ]
};

export async function GET() {
  seedDatabase();
  const db = getDb();
  
  const allKeys = [
    "terminal_coding", "knowledge_work", "novel_problem_solving", "agentic_search",
    "multidisciplinary_no_tools", "multidisciplinary_with_tools", "computer_use",
    "agentic_coding_deepswe", "agentic_coding_frontier", "business_workflows",
    "legal", "health", "biology_hard", "biology_human"
  ];
  
  // Pick 2-4 metrics to update in this cycle
  const shuffled = [...allKeys].sort(() => 0.5 - Math.random());
  const activeKeys = shuffled.slice(0, Math.floor(Math.random() * 3) + 2);
  
  let totalAddedInBatch = 0;
  const timeStr = new Date().toTimeString().split(" ")[0];
  
  for (const key of activeKeys) {
    const added = Math.floor(Math.random() * 8) + 3;
    totalAddedInBatch += added;
    
    const isElo = key === "knowledge_work";
    const delta = isElo ? Math.floor(Math.random() * 2) + 1 : Number((Math.random() * 0.03 + 0.01).toFixed(2));
    
    db.prepare(`
      UPDATE benchmark_metrics 
      SET claudia_score = round(claudia_score + ?, 2),
          growth_delta = round(growth_delta + ?, 2),
          problems_solved = problems_solved + ?
      WHERE key = ?
    `).run(delta, delta, added, key);
    
    // Insert execution log
    const msgs = logMessages[key] || ["Executed benchmark problem batch"];
    const msg = msgs[Math.floor(Math.random() * msgs.length)];
    const metricObj = db.prepare("SELECT name FROM benchmark_metrics WHERE key = ?").get() as any;
    const tag = metricObj ? metricObj.name : key;
    
    db.prepare(`
      INSERT INTO execution_logs (timestamp, metric_tag, message)
      VALUES (?, ?, ?)
    `).run(timeStr, tag, msg);
  }
  
  // Clean old logs keep max 20
  db.prepare(`
    DELETE FROM execution_logs WHERE id NOT IN (
      SELECT id FROM execution_logs ORDER BY id DESC LIMIT 20
    )
  `).run();

  // Update Session
  db.prepare(`
    UPDATE training_sessions 
    SET total_problems = total_problems + ?,
        accuracy_rate = round(99.18 + (abs(random() % 12) / 100.0), 2),
        cycle_number = cycle_number + 1,
        updated_at = datetime('now')
    WHERE id = 1
  `).run(totalAddedInBatch);

  const session = db.prepare("SELECT * FROM training_sessions WHERE id = 1").get();
  const metrics = db.prepare("SELECT * FROM benchmark_metrics").all();
  const logs = db.prepare("SELECT * FROM execution_logs ORDER BY id DESC LIMIT 10").all();

  return NextResponse.json({
    status: "LIVE_STREAMING_ACTIVE",
    session,
    metrics,
    logs,
    updated_keys: activeKeys
  });
}
