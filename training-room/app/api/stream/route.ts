import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";
import { seedDatabase } from "@/lib/seed";

export const dynamic = "force-dynamic";

export async function GET() {
  seedDatabase();
  const db = getDb();
  
  // Increment live simulated background batch
  db.prepare(`
    UPDATE training_sessions 
    SET total_problems = total_problems + abs(random() % 6 + 2),
        accuracy_rate = 99.18 + (abs(random() % 10) / 100.0),
        cycle_number = cycle_number + 1,
        updated_at = datetime('now')
    WHERE id = 1
  `).run();

  const session = db.prepare("SELECT * FROM training_sessions WHERE id = 1").get();
  const metrics = db.prepare("SELECT * FROM benchmark_metrics").all();
  const logs = db.prepare("SELECT * FROM execution_logs ORDER BY id DESC LIMIT 10").all();

  return NextResponse.json({
    status: "LIVE_STREAMING_ACTIVE",
    session,
    metrics,
    logs
  });
}
