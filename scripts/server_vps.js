require('dotenv').config();
const express = require('express');
const cors = require('cors');

const WalletManager = require('./wallet');
const JupiterClient = require('./jupiter');
const PythOracle = require('./pyth');
const TradingEngine = require('./engine');
const TelegramNotifier = require('./telegram');
const DlmmManager = require('./dlmm');
const TokocryptoBridge = require('./tokocrypto');
const { TOKENS, PYTH_FEED_IDS } = require('./constants');

const app = express();
const PORT = process.env.PORT || 3085;

// Middleware
app.use(cors());
app.use(
  express.json({
    // Keep the exact bytes so the webhook can verify its HMAC over what was signed.
    verify: (req, _res, buf) => {
      req.rawBody = buf;
    },
  })
);

// Initialize subsystems
const wallet = new WalletManager();
const jupiter = new JupiterClient();
const pyth = new PythOracle({
  updateIntervalMs: Number(process.env.PYTH_UPDATE_INTERVAL_MS || 3000)
});
const telegram = new TelegramNotifier();
const engine = new TradingEngine(wallet, jupiter, pyth);
const dlmm = new DlmmManager(wallet, jupiter, pyth, telegram);
const tokocrypto = new TokocryptoBridge();

// Start autonomous engine, price feeds & KUANTITATIF Concentrated Yield Pool
engine.start();
dlmm.start();

// Balance caching
let cachedBalances = {
  publicKey: wallet.address,
  sol: 2.0584,
  lamports: 2058468746,
  usdc: 108.6,
  usdt: 0,
  rpcUrl: wallet.rpcUrl
};

async function updateBalancesBackground() {
  try {
    const b = await wallet.getBalances();
    if (b && b.sol !== undefined) cachedBalances = b;
  } catch (err) {}
}

updateBalancesBackground();
setInterval(updateBalancesBackground, 5000);

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (req.path !== '/health' && req.path !== '/api/oracle/prices') {
      console.log(`[HTTP] ${req.method} ${req.path} ${res.statusCode} (${duration}ms)`);
    }
  });
  next();
});

// 1. Healthcheck Endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'solana-trading-engine',
    uptimeSeconds: Math.floor(process.uptime()),
    timestamp: new Date().toISOString()
  });
});

// 2. Comprehensive Status Endpoint
app.get('/api/status', (req, res) => {
  try {
    const oraclePrices = pyth.getAllPrices();
    const openPositions = engine.getOpenPositions();
    const tradeHistory = engine.getTradeHistory();
    const dlmmStatus = dlmm.getStatus();

    res.json({
      status: 200,
      service: 'solana-trading-engine',
      engine: { status: engine.status, mode: engine.config.dryRun ? 'DRY_RUN' : 'LIVE', dryRun: engine.config.dryRun, config: engine.config },
      dlmm: dlmmStatus,
      wallet: { publicKey: wallet.address, solBalance: cachedBalances.sol, lamports: cachedBalances.lamports, usdcBalance: cachedBalances.usdc, usdtBalance: cachedBalances.usdt, rpcUrl: cachedBalances.rpcUrl },
      oracle: { lastUpdated: oraclePrices.lastUpdated, prices: oraclePrices.prices },
      trading: { openPositionsCount: openPositions.length, openPositions, totalTradesCount: tradeHistory.length, recentTrades: tradeHistory.slice(0, 10) },
      system: { uptimeSeconds: Math.floor(process.uptime()), memoryUsageMb: Math.round(process.memoryUsage().heapUsed / 1024 / 1024), nodeVersion: process.version }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 3. KUANTITATIF Endpoints
app.get('/api/dlmm/status', (req, res) => res.json({ success: true, data: dlmm.getStatus() }));
app.post('/api/dlmm/rebalance', (req, res) => {
  try {
    const { midPrice } = req.body;
    dlmm.rebalance(Number(midPrice) || 109.21);
    res.json({ success: true, pool: dlmm.getStatus() });
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

// 4. Wallet & Oracle Endpoints
app.get('/api/wallet', (req, res) => res.json({ success: true, address: wallet.address, balances: cachedBalances }));
app.get('/api/oracle/prices', async (req, res) => {
  try {
    const all = pyth.getAllPrices();
    if (!all.prices || Object.keys(all.prices).length === 0) await pyth.fetchLatestPrices();
    res.json({ success: true, ...pyth.getAllPrices() });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 5. Jupiter & Trade Execution Endpoints
app.post('/api/trade/quote', async (req, res) => {
  try {
    const { inputToken = 'SOL', outputToken = 'USDC', amount = 1, slippageBps = 50 } = req.body;
    const quote = await jupiter.getQuote({ inputToken, outputToken, amount, slippageBps });
    if (!quote.success) return res.status(400).json(quote);
    res.json(quote);
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/trade/execute', async (req, res) => {
  try {
    const result = await engine.openPosition(req.body);
    res.json({ success: true, data: result });
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

app.post('/api/trade/close', async (req, res) => {
  try {
    const { positionId, reason = 'MANUAL_USER_CLOSE' } = req.body;
    if (!positionId) return res.status(400).json({ success: false, error: 'positionId is required' });
    const result = await engine.closePosition(positionId, reason);
    res.json(result);
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

app.post('/api/config', (req, res) => {
  try {
    res.json({ success: true, config: engine.updateConfig(req.body) });
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

app.get('/api/positions', (req, res) => res.json({ success: true, positions: engine.getOpenPositions() }));
app.get('/api/trades', (req, res) => res.json({ success: true, trades: engine.getTradeHistory() }));

// 6. Tokocrypto Virtual Account Payment Gateway
app.post('/api/deposit/va/create', async (req, res) => {
  try {
    const result = await tokocrypto.createVirtualAccount(req.body);
    res.json({ success: true, data: result });
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

app.get('/api/deposit/va/status/:referenceId', async (req, res) => {
  try {
    const result = await tokocrypto.checkDepositStatus(req.params.referenceId);
    res.json(result);
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

app.get('/api/deposit/va/list', (req, res) => {
  try {
    const txs = tokocrypto.listTransactions(req.query.telegramId);
    res.json({ success: true, transactions: txs });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/deposit/va/webhook', async (req, res) => {
  try {
    const result = await tokocrypto.handleWebhook(req.body, req.headers, telegram, req.rawBody);
    res.json(result);
  } catch (err) {
    const unauthorized = err.code === 'WEBHOOK_UNAUTHORIZED';
    if (!unauthorized) console.error('[Tokocrypto Webhook Error]:', err.message);
    else console.warn('[Tokocrypto Webhook] rejected unsigned/invalid request');
    res.status(unauthorized ? 401 : 400).json({ success: false, error: err.message });
  }
});

// Start listening
const server = app.listen(PORT, '127.0.0.1', () => {
  console.log(`====================================================`);
  console.log(`🚀 Solana Trading Engine & Tokocrypto VA running on port ${PORT}`);
  console.log(`🔑 Wallet Public Key: ${wallet.address}`);
  console.log(`💳 Tokocrypto Payment Bridge: ACTIVE (HMAC-SHA256 Ready)`);
  console.log(`====================================================`);
});

const shutdown = () => {
  console.log('[Server] Shutting down gracefully...');
  engine.stop();
  dlmm.stop();
  pyth.stopPolling();
  server.close(() => process.exit(0));
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);