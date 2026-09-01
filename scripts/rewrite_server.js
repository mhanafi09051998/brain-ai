const fs = require('fs');

const serverPath = '/home/ubuntu/apps/solana-trading-engine/src/server.js';

const newServer = `require('dotenv').config();
const express = require('express');
const cors = require('cors');

const WalletManager = require('./wallet');
const JupiterClient = require('./jupiter');
const PythOracle = require('./pyth');
const TelegramNotifier = require('./telegram');
const DlmmManager = require('./dlmm');
const TokocryptoBridge = require('./tokocrypto');
const { TOKENS, PYTH_FEED_IDS } = require('./constants');
const { startBotPolling } = require('./watcher/telegramBot');

const app = express();
const PORT = process.env.PORT || 3085;

app.use(cors());
app.use(express.json({
  verify: (req, _res, buf) => { req.rawBody = buf; }
}));

// Initialize subsystems
const wallet = new WalletManager();
const jupiter = new JupiterClient();
const pyth = new PythOracle({ updateIntervalMs: Number(process.env.PYTH_UPDATE_INTERVAL_MS || 3000) });
const telegram = new TelegramNotifier();
const dlmm = new DlmmManager(wallet, jupiter, pyth, telegram);
const tokocrypto = new TokocryptoBridge();

// Start LP Pool sync & Telegram bot
dlmm.start();
startBotPolling();

// Balance caching
let cachedBalances = { publicKey: wallet.address, sol: 0, usdc: 0, usdt: 0, rpcUrl: wallet.rpcUrl };
async function updateBalancesBackground() {
  try {
    const b = await wallet.getBalances();
    if (b && b.sol !== undefined) cachedBalances = b;
  } catch (err) {}
}
updateBalancesBackground();
setInterval(updateBalancesBackground, 5000);

// 1. Health
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'solana-lp-engine', uptimeSeconds: Math.floor(process.uptime()) });
});

// 2. Status
app.get('/api/status', (req, res) => {
  res.json({
    status: 200,
    service: 'solana-lp-engine',
    dlmm: dlmm.getStatus(),
    wallet: { publicKey: wallet.address, sol: cachedBalances.sol, usdc: cachedBalances.usdc },
    system: { uptimeSeconds: Math.floor(process.uptime()), memoryMb: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) }
  });
});

// 3. DLMM
app.get('/api/dlmm/status', (req, res) => res.json({ success: true, data: dlmm.getStatus() }));

// 4. Wallet
app.get('/api/wallet', (req, res) => res.json({ success: true, address: wallet.address, balances: cachedBalances }));

// 5. Tokocrypto VA
app.post('/api/deposit/va/create', async (req, res) => {
  try { res.json({ success: true, data: await tokocrypto.createVirtualAccount(req.body) }); }
  catch (err) { res.status(400).json({ success: false, error: err.message }); }
});
app.get('/api/deposit/va/status/:referenceId', async (req, res) => {
  try { res.json(await tokocrypto.checkDepositStatus(req.params.referenceId)); }
  catch (err) { res.status(400).json({ success: false, error: err.message }); }
});
app.get('/api/deposit/va/list', (req, res) => {
  try { res.json({ success: true, transactions: tokocrypto.listTransactions(req.query.telegramId) }); }
  catch (err) { res.status(500).json({ success: false, error: err.message }); }
});
app.post('/api/deposit/va/webhook', async (req, res) => {
  try { res.json(await tokocrypto.handleWebhook(req.body, req.headers, telegram, req.rawBody)); }
  catch (err) { res.status(err.code === 'WEBHOOK_UNAUTHORIZED' ? 401 : 400).json({ success: false, error: err.message }); }
});

// Start
const server = app.listen(PORT, '127.0.0.1', () => {
  console.log('====================================================');
  console.log('🚀 Solana LP Engine running on port ' + PORT);
  console.log('🔑 Wallet: ' + wallet.address);
  console.log('====================================================');
});

const shutdown = () => {
  dlmm.stop();
  pyth.stopPolling();
  server.close(() => process.exit(0));
};
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
`;

fs.writeFileSync(serverPath, newServer, 'utf8');
console.log('server.js rewritten — clean LP-only engine');
