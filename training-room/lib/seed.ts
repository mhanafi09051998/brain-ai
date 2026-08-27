import { getDb } from "./db";

export function seedDatabase() {
  const db = getDb();
  
  // Seed Session
  const sessionCheck = db.prepare("SELECT count(*) as count FROM training_sessions").get() as { count: number };
  if (sessionCheck.count === 0) {
    db.prepare(`
      INSERT INTO training_sessions (cycle_number, total_problems, accuracy_rate, active_subagents, updated_at)
      VALUES (156, 14480, 99.21, 6, datetime('now'))
    `).run();
  }

  // Seed Benchmark Metrics
  const metricsCheck = db.prepare("SELECT count(*) as count FROM benchmark_metrics").get() as { count: number };
  if (metricsCheck.count === 0) {
    const insertMetric = db.prepare(`
      INSERT INTO benchmark_metrics (key, name, benchmark_name, category, claudia_score, growth_delta, problems_solved, unit, opus5_score, fable5_score, opus48_score, gpt56_score)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const initialMetrics = [
      ["terminal_coding", "Agentic terminal coding", "Frontier-Bench v0.1", "coding", 49.54, 0.04, 1295, "%", "43.3%", "33.7%", "21.1%", "34.4%"],
      ["knowledge_work", "Knowledge work", "GDPval-AA v2", "reasoning", 1946, 4, 1162, "Elo", "1861", "1747", "1593", "1736"],
      ["novel_problem_solving", "Novel problem-solving", "ARC-AGI-3", "reasoning", 38.28, 0.08, 902, "%", "30.2%", "—", "1.5%", "7.8%"],
      ["agentic_search", "Agentic search", "BrowseComp", "reasoning", 94.66, 0.06, 1435, "%", "90.8%", "87.4%", "84.3%", "90.4%"],
      ["multidisciplinary_no_tools", "Multidisciplinary (no tools)", "Humanity's Last Exam", "reasoning", 61.45, 0.05, 962, "%", "56.3%", "56.5%", "49.8%", "—"],
      ["multidisciplinary_with_tools", "Multidisciplinary (with tools)", "Humanity's Last Exam", "reasoning", 72.18, 0.08, 1358, "%", "64.7%", "63.9%", "57.9%", "—"],
      ["computer_use", "Computer use", "OSWorld 2.0", "coding", 77.86, 0.06, 1124, "%", "70.6%", "66.1%", "55.7%", "62.6%"],
      ["agentic_coding_deepswe", "Agentic coding", "DeepSWE v1.1", "coding", 78.30, 0.10, 1698, "%", "68.8%", "69.7%", "59.0%", "72.7%"],
      ["agentic_coding_frontier", "Agentic coding", "FrontierCode v1.1, Main", "coding", 59.46, 0.06, 1236, "%", "53.4%", "53.5%", "46.5%", "47.5%"],
      ["business_workflows", "Business workflows", "AutomationBench", "domain", 33.05, 0.05, 792, "%", "26.0%", "17.4%", "17.0%", "18.1%"],
      ["legal", "Legal", "Legal Agent Benchmark", "domain", 17.85, 0.05, 648, "%", "11.7%", "13.3%", "10.4%", "2.5%"],
      ["health", "Health", "HealthBench Professional", "domain", 71.48, 0.08, 934, "%", "59.8%", "66.0%", "57.4%", "60.5%"],
      ["biology_hard", "Biology (hard)", "BioMysteryBench", "domain", 56.28, 0.08, 822, "%", "49.4%", "46.5%", "42.4%", "—"],
      ["biology_human", "Biology (human solved)", "BioMysteryBench", "domain", 95.45, 0.05, 1304, "%", "90.1%", "89.0%", "88.5%", "—"]
    ];

    for (const m of initialMetrics) {
      insertMetric.run(...m);
    }
  }

  // Seed Execution Logs
  const logsCheck = db.prepare("SELECT count(*) as count FROM execution_logs").get() as { count: number };
  if (logsCheck.count === 0) {
    const insertLog = db.prepare("INSERT INTO execution_logs (timestamp, metric_tag, message) VALUES (?, ?, ?)");
    insertLog.run("14:24:02", "DeepSWE v1.1", "Solved multi-file AST dependency conflict in django/orm/models.py (0 regressions)");
    insertLog.run("14:24:05", "ARC-AGI-3", "Inductive topological invariant verified for task #085a3c (100% matrix match)");
    insertLog.run("14:24:08", "Frontier-Bench", "Executed zero-copy shell socket pipe in sub-millisecond runtime (exit code 0)");
    insertLog.run("14:24:11", "Humanity's Last Exam", "Derived closed-form quantum harmonic oscillator parity formula");
  }
}
