const fs = require('fs');
const path = require('path');
const { PublicKey } = require('@solana/web3.js');
const DLMM = require('@meteora-ag/dlmm');

class DlmmManager {
  constructor(wallet, jupiter, pyth, telegram) {
    this.wallet = wallet;
    this.jupiter = jupiter;
    this.pyth = pyth;
    this.telegram = telegram;
    this.pair = 'USDC/USDT';
    this.poolPubkey = new PublicKey('ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq');
    this.dlmmPool = null;
    this.status = 'ACTIVE';
    
    this.poolState = {
      pair: 'USDC/USDT',
      status: 'ACTIVE',
      poolAddress: 'ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq',
      positionPubKey: 'HF6nw7Quxyx5wW4SX82yxd1bLnPzqtw4tXNM5WAPQJc5',
      walletAddress: this.wallet ? this.wallet.address : '',
      midPrice: 1.00,
      lowerBound: 0.9990,
      upperBound: 1.0010,
      totalCapitalUsd: 902.56,
      walletSolBalance: 0.095,
      walletUsdcBalance: 23.63,
      walletUsdtBalance: 23.88,
      totalFeeEarnedUsd: 0.00,
      currentEquityUsd: 902.56,
      unrealizedPnlUsd: 0.00,
      lastSyncTime: Date.now(),
      onChainSynced: true
    };

    this.dataPath = path.resolve(__dirname, '../data/dlmm_state.json');
    this.syncInterval = null;
    this.loadState();
  }

  loadState() {
    try {
      if (fs.existsSync(this.dataPath)) {
        const saved = JSON.parse(fs.readFileSync(this.dataPath, 'utf8'));
        if (saved && saved.pair === 'USDC/USDT') this.poolState = { ...this.poolState, ...saved };
      }
    } catch (e) {}
  }

  saveState() {
    try {
      const dir = path.dirname(this.dataPath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(this.dataPath, JSON.stringify(this.poolState, null, 2), 'utf8');
    } catch (e) {}
  }

  async start() {
    this.status = 'ACTIVE';
    await this.syncOnChainMeteora();
    this.syncInterval = setInterval(() => this.syncOnChainMeteora(), 15000);
  }

  stop() {
    this.status = 'STOPPED';
    if (this.syncInterval) clearInterval(this.syncInterval);
    this.saveState();
  }

  async syncOnChainMeteora() {
    try {
      if (!this.wallet || !this.wallet.connection) return;
      const DLMMClass = DLMM.default || DLMM;
      if (!this.dlmmPool) {
        this.dlmmPool = await DLMMClass.create(this.wallet.connection, this.poolPubkey);
      }

      const { userPositions } = await this.dlmmPool.getPositionsByUserAndLbPair(this.wallet.publicKey);
      const b = await this.wallet.getBalances();

      this.poolState.walletSolBalance = Number(b.sol.toFixed(4));
      this.poolState.walletUsdcBalance = Number(b.usdc.toFixed(2));
      this.poolState.walletUsdtBalance = Number(b.usdt.toFixed(2));
      this.poolState.midPrice = 1.00;

      if (userPositions && userPositions.length > 0) {
        const pos = userPositions[0];
        this.poolState.positionPubKey = pos.publicKey.toBase58();
        
        let totalXAmount = 0;
        let totalYAmount = 0;
        let feeXAmount = 0;
        let feeYAmount = 0;

        if (pos.positionData?.positionBinData) {
          for (const bin of pos.positionData.positionBinData) {
            totalXAmount += Number(bin.positionXAmount || 0) / 1e6;
            totalYAmount += Number(bin.positionYAmount || 0) / 1e6;
            feeXAmount += Number(bin.positionFeeXAmount || 0) / 1e6;
            feeYAmount += Number(bin.positionFeeYAmount || 0) / 1e6;
          }
        }

        const liquidityUsd = totalXAmount + totalYAmount;
        const claimableFeeUsd = feeXAmount + feeYAmount;

        this.poolState.totalCapitalUsd = Number(liquidityUsd.toFixed(2));
        this.poolState.totalFeeEarnedUsd = Number(claimableFeeUsd.toFixed(4));
        this.poolState.currentEquityUsd = Number((liquidityUsd + claimableFeeUsd).toFixed(2));
        this.poolState.lowerBound = 0.9990;
        this.poolState.upperBound = 1.0010;
      }

      this.poolState.lastSyncTime = Date.now();
      this.poolState.onChainSynced = true;
      this.saveState();
    } catch (err) {
      console.warn('[DLMM-OnChain] Sync warning:', err.message);
    }
  }

  getStatus() {
    return { status: this.status, pool: this.poolState };
  }
}

module.exports = DlmmManager;
