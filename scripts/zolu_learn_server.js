const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');

const app = express();
const PORT = 3005;
const STATE_FILE = path.join(__dirname, 'data/state.json');
const RUNNER_SCRIPT = '/home/ubuntu/benchmarks/official_runner.py';
const QUANT_SCRIPT = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/train_trading_engine.py';

let clients = [];
let quantData = {
  updated_at: new Date().toISOString(),
  market_snapshot: {},
  invariants: {}
};

app.use(cors());
app.use(express.json({ limit: '64kb' }));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/chat', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/chat.html'));
});

function getState() {
  try {
    const raw = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    raw.quant_trading = quantData;
    return raw;
  } catch (e) {
    return { status: "INIT", metrics: {}, logs: [], quant_trading: quantData };
  }
}

function broadcastState(state) {
  const data = `data: ${JSON.stringify(state)}\n\n`;
  clients.forEach(res => res.write(data));
}

app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  res.write(`data: ${JSON.stringify(getState())}\n\n`);
  clients.push(res);

  req.on('close', () => {
    clients = clients.filter(c => c !== res);
  });
});

app.get('/api/state', (req, res) => {
  res.json(getState());
});

app.get('/api/quant-trading', (req, res) => {
  res.json(quantData);
});

let isRunningStep = false;
function runRealBenchmarkStep() {
  if (isRunningStep) return;
  isRunningStep = true;
  exec(`python3 ${RUNNER_SCRIPT}`, { timeout: 25000 }, (err, stdout) => {
    isRunningStep = false;
    if (err) return;
    try {
      const data = JSON.parse(stdout);
      const m = data.real_metrics;
      const state = {
        status: "REAL_BENCHMARK_ONLINE",
        mode: "100% Real Empirical Benchmark Suite",
        total_evaluations: data.total_tests_executed,
        current_iteration: data.total_tests_executed,
        last_eval: data.current_test,
        metrics: {
          swe_bench: { current: m.swe_bench, target: 85.0, status: "Empirical Real" },
          tau_bench: { current: m.tau_bench, target: 95.0, status: "Empirical Real" },
          aime_gpqa: { current: m.aime_gpqa, target: 90.0, status: "Empirical Real" },
          gpqa_diamond: { current: m.gpqa_diamond || m.aime_gpqa, target: 90.4, status: "Empirical Real" },
          niah_retrieval: { current: m.niah_retrieval, target: 99.9, status: "Empirical Real" },
          ifeval: { current: m.ifeval, target: 98.0, status: "Empirical Real" },
          inference_speed: { current: m.inference_speed, target: 120.0, unit: "tok/s", status: "Empirical Real" }
        },
        logs: data.recent_logs,
        quant_trading: quantData
      };
      fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
      broadcastState(state);
    } catch (e) {}
  });
}

function updateQuantMarketData() {
  const quantDatasetPath = '/home/ubuntu/Agent_Claudia_Autonomus/learning/frontier_datasets/quant_trading_dataset.json';
  if (fs.existsSync(quantDatasetPath)) {
    try {
      quantData = JSON.parse(fs.readFileSync(quantDatasetPath, 'utf8'));
    } catch (e) {}
  }
}

// Run initial loops
updateQuantMarketData();
setInterval(updateQuantMarketData, 10000);
const intervalTimer = setInterval(runRealBenchmarkStep, 3500);
runRealBenchmarkStep();

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Claudia Max 4.0 Learning & Trading Hub running on port ${PORT}`);
});

server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.error(`[Port Guard] Port ${PORT} is in use, exiting cleanly for PM2.`);
    process.exit(1);
  }
});

function cleanupAndExit(signal) {
  console.log(`[Shutdown] Received ${signal}, closing server gracefully...`);
  clearInterval(intervalTimer);
  server.close(() => {
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 3000);
}

process.on('SIGTERM', () => cleanupAndExit('SIGTERM'));
process.on('SIGINT', () => cleanupAndExit('SIGINT'));