import path from "path";

// @ts-ignore
const { DatabaseSync } = require("node:sqlite");

const dataDir = path.join(process.cwd(), "data");
const dbPath = path.join(dataDir, "training_room.sqlite");

// @ts-ignore
let dbInstance: any = null;

export function getDb() {
  if (!dbInstance) {
    dbInstance = new DatabaseSync(dbPath);
    
    // Initialize schema
    dbInstance.exec(`
      CREATE TABLE IF NOT EXISTS training_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_number INTEGER NOT NULL,
        total_problems INTEGER NOT NULL,
        accuracy_rate REAL NOT NULL,
        active_subagents INTEGER NOT NULL,
        updated_at TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS benchmark_metrics (
        key TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        benchmark_name TEXT NOT NULL,
        category TEXT NOT NULL,
        claudia_score REAL NOT NULL,
        growth_delta REAL NOT NULL,
        problems_solved INTEGER NOT NULL,
        unit TEXT NOT NULL,
        opus5_score TEXT NOT NULL,
        fable5_score TEXT NOT NULL,
        opus48_score TEXT NOT NULL,
        gpt56_score TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS execution_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        metric_tag TEXT NOT NULL,
        message TEXT NOT NULL
      );
    `);
  }
  return dbInstance;
}
