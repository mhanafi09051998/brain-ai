/**
 * Solana High-Velocity Sweet Spot Autonomous Trading Daemon
 * Target: $70k - $220k MC & High Velocity Volume (>= $60k/hr)
 */

const path = require('path');
const fs = require('fs');
const https = require('https');
const { execSync } = require('child_process');

require('dotenv').config({ path: '/home/ubuntu/.config/gmgn/.env' });
require('dotenv').config({ path: path.resolve(__dirname, '.env') });

const { PublicKey } = require('@solana/web3.js');
const WalletManager = require('./wallet');
const JupiterClient = require('./jupiter');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;
if (!BOT_TOKEN || !CHAT_ID) {
  console.error('[daemon] TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID wajib diset di environment.');
  process.exit(1);
}
const STATE_FILE = path.resolve(__dirname, '../data/gmgn_dlmm_state.json');

const TRADE_SOL_AMOUNT = 0.30; // $30.00 Modal Scalp

const GMGN_API_KEY = process.env.GMGN_API_KEY || 'gmgn_bccff8182bde5d0df6aaad50d88e8e53';
const GMGN_PRIVATE_KEY = process.env.GMGN_PRIVATE_KEY || '';

const EXEC_ENV = {
  ...process.env,
  GMGN_API_KEY: GMGN_API_KEY,
  GMGN_PRIVATE_KEY: GMGN_PRIVATE_KEY,
  HOME: '/home/ubuntu'
};

function sendTelegram(text) {
  try {
    const payload = JSON.stringify({ chat_id: CHAT_ID, text: text, parse_mode: 'Markdown' });
    const req = https.request({
      hostname: 'api.telegram.org',
      port: 443,
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
    });
    req.on('error', e => console.error('Telegram error:', e.message));
    req.write(payload);
    req.end();
  } catch (e) {}
}

class HighVelocitySweetSpotScalper {
  constructor() {
    this.wallet = new WalletManager();
    this.connection = this.wallet.connection;
    this.jup = new JupiterClient();
    this.state = this.loadState();
    this.isProcessing = false;
    this.cooldownTokens = this.state.cooldownTokens || {};
  }

  loadState() {
    try {
      if (fs.existsSync(STATE_FILE)) {
        return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
      }
    } catch (e) {}
    return {
      activePosition: null,
      lastHeartbeat: Date.now(),
      totalProfitRealized: 0.30,
      cooldownTokens: {}
    };
  }

  saveState() {
    try {
      const dir = path.dirname(STATE_FILE);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      this.state.cooldownTokens = this.cooldownTokens;
      fs.writeFileSync(STATE_FILE, JSON.stringify(this.state, null, 2), 'utf8');
    } catch (e) {}
  }

  /**
   * 10-Point Forensic & High Velocity Screener
   */
  async scanBestCandidate() {
    try {
      const rawTrending = execSync('gmgn-cli market trending --chain sol --interval 1h --limit 60', {
        encoding: 'utf8',
        env: EXEC_ENV
      });
      const jsonT = JSON.parse(rawTrending);
      const list = (jsonT.data && jsonT.data.rank) || [];
      const now = Date.now();

      for (const t of list) {
        if (this.cooldownTokens[t.address] && (now - this.cooldownTokens[t.address] < 7200000)) {
          continue;
        }

        const bundler = Number(t.bundler_rate || 0);
        const devHold = Number(t.dev_team_hold_rate || 0);
        const ratRate = Number(t.rat_trader_amount_rate || 0);
        const top10 = Number(t.top_10_holder_rate || 0);
        const smartDegen = Number(t.smart_degen_count || 0);
        const liq = Math.round(Number(t.liquidity || 0));
        const vol = Math.round(Number(t.volume || 0));
        const mc = Math.round(Number(t.market_cap || 0));

        // 1. Anti-Rugpull Filters
        const isSafeContract = t.is_honeypot === 0 && 
                               t.renounced_mint == 1 && 
                               t.renounced_freeze_account == 1 && 
                               (t.burn_status === 'burn' || (t.burn_ratio && t.burn_ratio >= 0.9));

        const isZeroDev = devHold === 0 && ratRate === 0;

        // 2. High Velocity Sweet Spot ($65k - $220k MC & High Volume >= $60k/hr)
        const isHighVelocitySweetSpot = mc >= 65000 && mc <= 220000 && liq >= 15000 && vol >= 60000;

        // 3. Smart Money & Anti-Sniper
        const isSmartMoney = bundler <= 0.18 && top10 <= 0.28 && smartDegen >= 3;

        // 4. Pullback check
        const athPrice = Number(t.ath_price || t.history_highest_market_cap / (t.total_supply || 1e9) || t.price);
        const currentPrice = Number(t.price);
        const dipFromAthPct = athPrice > 0 ? ((athPrice - currentPrice) / athPrice) * 100 : 0;
        const isPullback = dipFromAthPct >= 10.0;

        if (isSafeContract && isZeroDev && isHighVelocitySweetSpot && isSmartMoney && isPullback) {
          return {
            name: t.name,
            symbol: t.symbol,
            address: t.address,
            price: currentPrice,
            market_cap: mc,
            liquidity: liq,
            volume: vol,
            smart_degens: smartDegen,
            bundler_rate: (bundler * 100).toFixed(1) + '%',
            dipFromAth: dipFromAthPct.toFixed(1) + '%'
          };
        }
      }
    } catch (e) {}
    return null;
  }

  async executeOpenPosition(candidate) {
    if (this.state.activePosition !== null) return;

    console.log(`\n🚀 [AUTO-ENTRY ($30)] Membuka posisi untuk ${candidate.symbol} (${candidate.address})...`);
    const b = await this.wallet.getBalances();

    if (b.sol < TRADE_SOL_AMOUNT + 0.015) {
      console.log('Saldo SOL dompet kurang dari 0.315 SOL.');
      return;
    }

    try {
      const q = await this.jup.getQuote({
        inputToken: 'SOL',
        outputToken: candidate.address,
        amount: TRADE_SOL_AMOUNT,
        slippageBps: 150
      });

      if (!q.success) return;

      const swapRes = await this.jup.executeSwap({
        quoteResponse: q.quoteResponse,
        keypair: this.wallet.keypair,
        connection: this.connection
      });

      if (swapRes && swapRes.txid) {
        this.state.activePosition = {
          tokenAddress: candidate.address,
          name: candidate.name,
          symbol: candidate.symbol,
          entryPrice: candidate.price,
          highWatermark: candidate.price,
          entrySolAmount: TRADE_SOL_AMOUNT,
          tokenAmountOut: q.outAmountUi,
          entryTx: swapRes.txid,
          entryTime: Date.now()
        };
        this.saveState();

        sendTelegram(`🚀 *[AUTO-SCALP DIBUKA (HIGH VELOCITY)] Posisi Baru (${candidate.symbol})*\n\n• Token: *${candidate.name} ($${candidate.symbol})*\n• Contract: \`${candidate.address}\`\n• Modal Masuk: *${TRADE_SOL_AMOUNT.toFixed(2)} SOL* (~$30.00)\n• Market Cap: *\$${Math.round(candidate.market_cap/1000)}k*\n• Volume 1 Jam: *\$${Math.round(candidate.volume/1000)}k*\n• Smart Money: *${candidate.smart_degens} Dompet*\n• Bundler: *${candidate.bundler_rate}*\n\n🎯 *Target Setup:*\n• Hard Take Profit: *+80%*\n• Trailing Stop: *8% dari Puncak* (Aktif di +12%)\n• Hard Stop Loss: *-15%*\n\n🔗 *Solscan Tx:* https://solscan.io/tx/${swapRes.txid}`);
      }
    } catch (e) {
      console.error('Error auto-opening position:', e.message);
    }
  }

  async executeClosePosition(reason, currentPrice) {
    const pos = this.state.activePosition;
    if (!pos) return;

    try {
      const owner = this.wallet.keypair.publicKey;
      let tokenAmt = 0;

      const t2022 = await this.connection.getParsedTokenAccountsByOwner(owner, {
        programId: new PublicKey('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb')
      });
      for (const acc of t2022.value) {
        if (acc.account.data.parsed.info.mint === pos.tokenAddress) {
          tokenAmt = acc.account.data.parsed.info.tokenAmount.uiAmount;
          break;
        }
      }

      if (!tokenAmt) {
        const spl = await this.connection.getParsedTokenAccountsByOwner(owner, {
          programId: new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
        });
        for (const acc of spl.value) {
          if (acc.account.data.parsed.info.mint === pos.tokenAddress) {
            tokenAmt = acc.account.data.parsed.info.tokenAmount.uiAmount;
            break;
          }
        }
      }

      if (!tokenAmt || tokenAmt <= 0) tokenAmt = pos.tokenAmountOut;

      const exitQuote = await this.jup.getQuote({
        inputToken: pos.tokenAddress,
        outputToken: 'SOL',
        amount: tokenAmt,
        slippageBps: 200
      });

      if (exitQuote.success) {
        const exitSwap = await this.jup.executeSwap({
          quoteResponse: exitQuote.quoteResponse,
          keypair: this.wallet.keypair,
          connection: this.connection
        });

        if (exitSwap && exitSwap.txid) {
          const bFinal = await this.wallet.getBalances();
          const pnlPct = ((currentPrice - pos.entryPrice) / pos.entryPrice) * 100;

          sendTelegram(`⚡ *[AUTO-EXIT SELESAI] Posisi Ditutup & Profit Diamankan!*\n\n• Token: *${pos.name} ($${pos.symbol})*\n• Alasan: *${reason}*\n• Realized Return: *${pnlPct >= 0 ? '+' : ''}${pnlPct.toFixed(2)}%*\n• Saldo SOL Phantom: *${bFinal.sol.toFixed(4)} SOL*\n\n🔗 *Tx Exit:* https://solscan.io/tx/${exitSwap.txid}\n\n_Modal aman di SOL. Engine langsung memburu token High-Velocity berikutnya..._`);

          this.cooldownTokens[pos.tokenAddress] = Date.now();
          this.state.activePosition = null;
          this.saveState();
        }
      }
    } catch (e) {
      console.error('Error executing auto close:', e.message);
    }
  }

  async loop() {
    if (this.isProcessing) return;
    this.isProcessing = true;

    try {
      if (!this.state.activePosition) {
        const candidate = await this.scanBestCandidate();
        if (candidate) {
          await this.executeOpenPosition(candidate);
        }
      } else {
        const pos = this.state.activePosition;
        const currentPrice = await this.fetchTokenPrice(pos.tokenAddress);

        if (currentPrice > 0) {
          if (currentPrice > (pos.highWatermark || pos.entryPrice)) {
            pos.highWatermark = currentPrice;
            const peakPnlPct = (pos.highWatermark - pos.entryPrice) / pos.entryPrice;
            this.saveState();

            if (peakPnlPct >= 0.20 && (!pos.lastPeakNotified || peakPnlPct - pos.lastPeakNotified >= 0.20)) {
              pos.lastPeakNotified = peakPnlPct;
              this.saveState();
              sendTelegram(`🚀 *[PEAK MILESTONE] $${pos.symbol}*\n• Puncak: \$${currentPrice.toFixed(6)}\n• Peak PnL: *+${(peakPnlPct * 100).toFixed(2)}%* 🔥\n• Trailing Lock: Mengunci profit jika turun 8% dari titik ini.`);
            }
          }

          const currentPnlPct = (currentPrice - pos.entryPrice) / pos.entryPrice;
          const peakPrice = pos.highWatermark || pos.entryPrice;
          const peakPnlPct = (peakPrice - pos.entryPrice) / pos.entryPrice;
          const drawdownFromPeak = (peakPrice - currentPrice) / peakPrice;

          if (currentPnlPct <= -0.15) {
            await this.executeClosePosition('HARD_STOP_LOSS (-15%)', currentPrice);
          } else if (peakPnlPct >= 0.12 && drawdownFromPeak >= 0.08) {
            await this.executeClosePosition(`TRAILING_STOP (Peak: +${(peakPnlPct * 100).toFixed(2)}%, Retrace 8%)`, currentPrice);
          } else if (currentPnlPct >= 0.80) {
            await this.executeClosePosition('HARD_TAKE_PROFIT (+80%)', currentPrice);
          }
        }
      }
    } catch (err) {
      console.error('High-Velocity loop error:', err.message);
    } finally {
      this.isProcessing = false;
    }
  }

  async fetchTokenPrice(address) {
    try {
      const raw = execSync(`gmgn-cli token info --chain sol --address ${address}`, {
        encoding: 'utf8',
        env: EXEC_ENV
      });
      const json = JSON.parse(raw);
      const priceVal = (json.price && json.price.price) || json.price || (json.data && json.data.price) || 0;
      return Number(priceVal);
    } catch (e) {
      return 0;
    }
  }

  start() {
    console.log('🚀 [High-Velocity Sweet Spot Scalper Engine] Resmi aktif...');
    setInterval(() => this.loop(), 1500);
    this.loop();
  }
}

module.exports = HighVelocitySweetSpotScalper;
