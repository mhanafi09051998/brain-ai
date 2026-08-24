# Neuron N042: Crypto On-Chain Forensics & Whale Orderflow Analysis

Prinsip arsitektur forensik on-chain, pelacakan pergerakan *whale orderflow*, metriks valuasi makro siklus pasar kripto, dinamika cadangan bursa sentral (CEX), serta deteksi eksploitasi MEV / front-running mempool:

- **Kategori**: Crypto On-Chain Forensics, Whale Orderflow Tracking, Macro Cycle Valuation & Mempool MEV Architecture
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Mengurai klaster kepemilikan alamat multi-input UTXO dan akun EVM, mendeteksi perpindahan modal institusional via rasio arus masuk/keluar CEX, mengukur puncak dan dasar siklus harga menggunakan MVRV-Z, SOPR, NVT, dan SSR, serta merekonstruksi serangan *sandwich* dan *priority gas auctions* (PGA) di dalam mempool secara deterministik.
- **Synaptic Links**: [`N001`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [`N004`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [`N007`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N007_self_improving_loop.md), [`N009`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [`N014`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N014_zero_trust_security_and_cryptography.md), [`N021`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [`N025`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [`N035`](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N035_event_driven_streaming_cqrs.md)
- **Status**: Active Operational Invariant

---

## 1. Whale Wallet Clustering & Address Graph Forensics

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     UTXO Multi-Input Transaction                        │
│                                                                         │
│  [ Input A: 2.5 BTC ] ───┐                                              │
│  [ Input B: 1.0 BTC ] ───┼──► [ CIOH Engine ] ──► Entity Cluster α      │
│  [ Input C: 4.0 BTC ] ───┘         │              (Total: 7.5 BTC)      │
│                                    ▼                                    │
│                         ┌───────────────────────┐                       │
│                         │ Change Detection Rule │                       │
│                         └──────────┬────────────┘                       │
│                                    │                                    │
│                 ┌──────────────────┴──────────────────┐                 │
│                 ▼                                     ▼                 │
│  [ Output 1: 7.0 BTC (Payment) ]     [ Output 2: 0.499 BTC (Change) ]   │
│  Destination: Merchant / Exchange    Assigned to Entity Cluster α       │
└─────────────────────────────────────────────────────────────────────────┘
```

### A. UTXO Clustering Heuristics & Entity Resolution
1. **Common Input Ownership Heuristic (CIOH)**:
   - Dalam model UTXO (Bitcoin, Litecoin), transaksi yang mengonsumsi lebih dari satu UTXO masukan ($	ext{Input}_1, 	ext{Input}_2, \dots, 	ext{Input}_k$) diasumsikan dikendalikan oleh entitas privat tunggal yang sama karena memerlukan tanda tangan kunci privat yang dikoordinasikan secara bersamaan.
   - *Invarian Graf*: Semua alamat masukan digabungkan ke dalam satu komponen terhubung (*disjoint set union* / DSU).
2. **Change Address Identification Heuristics**:
   - **One-Time Fresh Address Heuristic**: Alamat kembalian (*change address*) umumnya baru pertama kali muncul di rantai (*zero previous transactions*), sedangkan alamat tujuan pembayaran sering kali memiliki riwayat transaksi sebelumnya.
   - **Script Type Homogeneity**: Dompet modern mempertahankan tipe skrip yang konsisten (misal: jika semua input adalah `P2WPKH` / Native SegWit, kembalian akan berformat `P2WPKH`, bukan `P2PKH` legacy).
   - **Round Payment vs Odd Change**: Alamat tujuan biasanya menerima nilai nominal bulat (misal: $1.0	ext{ BTC}$, $0.5	ext{ BTC}$), sementara kembalian menampung sisa pecahan ganjil dikurangi biaya transaksi ($V_{	ext{change}} = \sum V_{	ext{in}} - V_{	ext{pay}} - 	ext{Fee}$).
3. **CoinJoin / CoinShuffle Anomaly Filter**:
   - Jika transaksi memiliki banyak input dari banyak alamat dan menghasilkan beberapa output dengan denominasi nilai persis identik (misal $10 	imes 0.1	ext{ BTC}$ output), transaksi tersebut diklasifikasikan sebagai *CoinJoin mixer*.
   - *Invarian Keamanan*: Jangan gabungkan input CoinJoin ke dalam klaster CIOH untuk mencegah polusi graf (*Sybil cluster poisoning*).

### B. EVM Account-Based Graph Forensics & Whale Tiers
1. **Deposit Forwarder / Sweep Sweeper Pattern**:
   - Bursa sentral (CEX) membuat alamat *deposit proxy* per pengguna. Pola akumulasi terdeteksi ketika ribuan alamat deposit mentransfer seluruh saldo ERC-20 / ETH ke satu alamat *Hot Wallet Aggregator* terpusat dalam interval waktu singkat.
2. **Whale Entity Stratification Invariants**:
   - **Megawhale Tier**: Entitas dengan saldo $\ge 10,000	ext{ BTC}$ atau $\ge 100,000	ext{ ETH}$ (Institutional Custody, ETF Issuers, Sovereign Funds).
   - **Whale Tier**: Saldo $1,000	ext{ BTC} - 9,999	ext{ BTC}$ atau $10,000	ext{ ETH} - 99,999	ext{ ETH}$ (Hedge Funds, High-Net-Worth Entities, Market Makers).
   - **Shark Tier**: Saldo $100	ext{ BTC} - 999	ext{ BTC}$ (Early Adopters, Mid-Sized Desks).
   - **Retail / Fish Tier**: Saldo $< 10	ext{ BTC}$.

---

## 2. CEX Net Inflows/Outflows & Exchange Reserve Dynamics

```
                           ┌─────────────────────────┐
                           │      Whale Wallets      │
                           └────────────┬────────────┘
                                        │
                    Deposit (Inflow)    │   Withdrawal (Outflow)
               [ Impending Sell Risk ]  │   [ Supply Shock / Accumulation ]
                                        ▼
                           ┌─────────────────────────┐
                           │   CEX Hot/Cold Vaults   │
                           │   Reserve(t) = R(t-1)   │
                           │     + NetFlow(t)        │
                           └────────────┬────────────┘
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │ Whale-to-Exchange Ratio │
                           │  Top10_Inflow / Total   │
                           │   (> 0.85 = Dump Alert) │
                           └─────────────────────────┘
```

### A. Exchange Netflow & Reserve Invariants
1. **Netflow Fundamental Equation**:
   $$	ext{NetFlow}(t) = \sum_{i=1}^N 	ext{Inflow}_{CEX, i}(t) - \sum_{j=1}^M 	ext{Outflow}_{CEX, j}(t)$$
   $$	ext{Reserve}(t) = 	ext{Reserve}(t_0) + \int_{t_0}^t 	ext{NetFlow}(	au) \, d	au$$
2. **Directional Flow Interpretation**:
   - $	ext{NetFlow}(t) \gg 0$ (*Exchange Inflow Spike*): Whale memindahkan aset liquid ke bursa. Likuiditas jual siap dieksekusi di buku order $	o$ Tekanan turun tajam (*bearish divergence / impending dump*).
   - $	ext{NetFlow}(t) \ll 0$ (*Exchange Outflow Drain*): Whale menarik koin dari bursa ke *cold storage* multi-sig. Cadangan bursa mengering (*liquid supply contraction*) $	o$ *Supply shock* / fase akumulasi institusi (*bullish structural base*).

### B. Whale-to-Exchange Flow Ratio
1. **Formulasi Rasio Dominasi Whale**:
   $$	ext{WhaleFlowRatio}(t) = rac{\sum_{k=1}^{10} 	ext{Inflow}_{k}(t)}{\sum_{a=1}^{N} 	ext{Inflow}_{a}(t)}$$
2. **Threshold Operasional**:
   - Jika $	ext{WhaleFlowRatio}(t) > 0.85$ bersamaan dengan volume inflow bursa $> 2\sigma$ di atas rata-rata 30 hari: picu sinyal *Institutional Sell Offloading Guard*.

---

## 3. Macro On-Chain Valuation & Cycle Metrics

```
     MVRV-Z Score Metric                     SOPR (Spent Output Profit Ratio)
┌─────────────────────────────┐        ┌────────────────────────────────────────┐
│ MVRV = MarketCap / RealCap  │        │ SOPR = SpentValue / CreatedValue       │
│                             │        │                                        │
│  Z > 3.8 : Macro Top Bubble │        │ SOPR > 1.0 : Selling in Profit         │
│  Z < 0.1 : Macro Bottom Zone│        │ SOPR = 1.0 : Bull Market Support Line  │
│                             │        │ SOPR < 1.0 : Capitulation at Loss      │
└─────────────────────────────┘        └────────────────────────────────────────┘
```

### A. Market-Value-to-Realized-Value (MVRV & MVRV-Z Score)
1. **Realized Capitalization ($	ext{Cap}_{	ext{realized}}$)**:
   - Berbeda dari Market Cap standar ($P_{	ext{spot}} 	imes 	ext{TotalSupply}$), Realized Cap menilai setiap UTXO berdasarkan harga spot pada saat UTXO tersebut terakhir kali berpindah tangan di blockchain:
     $$	ext{Cap}_{	ext{realized}} = \sum_{i=1}^U 	ext{UTXO}_i 	imes P_{	ext{timestamp}(	ext{UTXO}_i)}$$
2. **MVRV Ratio**:
   $$	ext{MVRV} = rac{	ext{Cap}_{	ext{market}}}{	ext{Cap}_{	ext{realized}}}$$
3. **MVRV-Z Score Normalization**:
   $$	ext{MVRV-Z} = rac{	ext{Cap}_{	ext{market}} - 	ext{Cap}_{	ext{realized}}}{\sigma(	ext{Cap}_{	ext{market}})}$$
   - $	ext{MVRV-Z} > 3.5 - 5.0$: Keuntungan belum terealisasi (*unrealized profit*) berada di level ekstrem historis. Probabilitas puncak siklus makro (*blow-off top*) $\ge 95\%$.
   - $	ext{MVRV-Z} < 0.1$ (atau negatif): Nilai pasar lebih rendah dari rata-rata harga beli historis agregat. Fase kapitulasi total / dasar siklus akumulasi generasi (*generational accumulation floor*).

### B. Spent Output Profit Ratio (SOPR & aSOPR)
1. **SOPR Formulation**:
   $$	ext{SOPR} = rac{\sum_{i=1}^M 	ext{ValueAtSpent}_i}{\sum_{i=1}^M 	ext{ValueAtCreation}_i} = rac{\sum_{i=1}^M 	ext{UTXO}_i \cdot P_{	ext{spent}, i}}{\sum_{i=1}^M 	ext{UTXO}_i \cdot P_{	ext{created}, i}}$$
2. **Adjusted SOPR (aSOPR)**:
   - Mengabaikan seluruh UTXO yang berumur $< 1	ext{ jam}$ ($\Delta t < 3600	ext{s}$) untuk memfilter transaksi relay internal, bot arbitrase kilat, dan kebisingan lalu-lintas jaringan.
3. **Regime Invariants**:
   - $	ext{SOPR} > 1.0$: Koin bergerak dalam kondisi laba terealisasi.
   - Dalam *Bull Market*, garis $	ext{SOPR} = 1.0$ bertindak sebagai *support* psikologis kuat (pemegang menolak merealisasikan kerugian).
   - Dalam *Bear Market*, garis $	ext{SOPR} = 1.0$ bertindak sebagai *resistance* tangguh (pemegang menjual aset pada titik impas / *break-even relief rally*).

### C. Network Value to Transactions (NVT Ratio & NVT Signal)
1. **NVT Ratio (Crypto P/E Equivalent)**:
   $$	ext{NVT} = rac{	ext{Cap}_{	ext{market}}}{	ext{Daily On-Chain Volume (USD)}}$$
2. **NVT Signal (NVTS)**:
   $$	ext{NVTS} = rac{	ext{Cap}_{	ext{market}}}{	ext{SMA}_{90}(	ext{Daily On-Chain Volume (USD)})}$$
   - Nilai NVTS tinggi menandakan valuasi spekulatif yang melompat jauh melampaui utilitas throughput transaksi jaringan. Nilai NVTS rendah menandakan aset *undervalued* terhadap volume transfer ekonomi aktual.

### D. Stablecoin Supply Ratio (SSR)
1. **Definisi SSR**:
   $$	ext{SSR} = rac{	ext{Cap}_{	ext{BTC/Crypto}}}{\sum 	ext{Cap}_{	ext{Stablecoins}} (	ext{USDT} + 	ext{USDC} + 	ext{DAI} + \dots)}$$
2. **Daya Beli Pasokan (Dry Powder Invariant)**:
   - **Low SSR**: Pasokan stablecoin melimpah relatif terhadap kapitalisasi pasar kripto. Daya beli cadangan (*buying power*) tinggi $	o$ Bahan bakar likuiditas besar untuk reli harga.
   - **High SSR**: Pasokan stablecoin menipis relatif terhadap kapitalisasi pasar kripto. Likuiditas kering $	o$ Rentan terhadap kerapuhan likuiditas dan pembalikan tren turun.

---

## 4. Mempool Forensics & Front-Running / MEV Detection

```
           Mempool Pending State                  Mined Block Execution Order
┌───────────────────────────────────────────┐    ┌─────────────────────────────────────────┐
│ Tx Victim: Swap 10 ETH -> TOKEN           │    │ 1. Tx Front-Run (Attacker Buy)          │
│   MaxFee: 50 gwei, Tip: 2 gwei            │    │    Tip: 15 gwei (Pumps AMM Price)       │
│                                           │    ├─────────────────────────────────────────┤
│ Tx Attacker FR: Buy TOKEN                 │───►│ 2. Tx Victim (Executes at Max Slippage) │
│   MaxFee: 70 gwei, Tip: 15 gwei           │    │    Price Pushed to Upper Tolerance      │
│                                           │    ├─────────────────────────────────────────┤
│ Tx Attacker BR: Sell TOKEN                │    │ 3. Tx Back-Run (Attacker Sell)          │
│   MaxFee: 65 gwei, Tip: 1 gwei (Bundle)   │    │    Extracts Arbitrage Delta Profit      │
└───────────────────────────────────────────┘    └─────────────────────────────────────────┘
```

### A. EIP-1559 Mempool Transaction Ordering
1. **Effective Gas Price Resolution**:
   $$P_{	ext{eff}} = \min(f_{	ext{max}}, f_{	ext{base}} + p_{	ext{tip}})$$
2. **Priority Gas Auctions (PGA)**:
   - Penambang / Block Builder (Searchers via MEV-Boost / Flashbots) menyortir transaksi secara monotonik menurun berdasarkan $p_{	ext{tip}}$ tertinggi untuk posisi eksekusi terdepan.

### B. Sandwich Attack Forensic Invariants
1. **Topologi Serangan Tripartit**:
   - **Tx 1 (Front-run $T_f$)**: Pembelian agresif token target oleh penyerang dengan $P_{	ext{eff}}(T_f) > P_{	ext{eff}}(T_v)$, menaikkan harga spot pada Constant Product AMM ($x \cdot y = k$).
   - **Tx 2 (Victim $T_v$)**: Transaksi korban dieksekusi pada harga yang terdistorsi hingga batas toleransi *slippage* maksimum ($P_{	ext{exec}} \le P_{	ext{initial}} 	imes (1 + 	ext{Slippage}_{	ext{max}})$).
   - **Tx 3 (Back-run $T_b$)**: Penjualan kembali token oleh penyerang tepat setelah transaksi korban ($P_{	ext{eff}}(T_b) \le P_{	ext{eff}}(T_f)$) untuk mengantongi selisih keuntungan bebas risiko.
2. **Deteksi MEV Deterministik**:
   - Jika dalam 1 blok terdapat pasangan transaksi: $	ext{SwapIn}(T_f) 	o 	ext{SwapIn}(T_v) 	o 	ext{SwapOut}(T_b)$ pada AMM pool yang sama, dengan $	ext{Recipient}(T_f) == 	ext{Recipient}(T_b)$, tandai transaksi tersebut sebagai *Exploited MEV Sandwich Attack*.

---

## 5. Pure Python 3.12+ Executable Test Invariants (Zero-Dependency)

Implementasi mandiri lengkap: **UTXO Cluster Engine (CIOH & Change Detection)**, **CEX NetFlow & Whale-to-Exchange Analyzer**, **On-Chain Valuation Engine (MVRV-Z, SOPR, NVT, SSR)**, dan **Mempool MEV Sandwich Detector**:


```python
"""
Neuron N042: Crypto On-Chain Forensics & Whale Orderflow Analysis Suite.
Pure Python 3.12+ Standard Library (Zero External Dependencies).
"""

from __future__ import annotations
import math
import statistics
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


# ==============================================================================
# 1. UTXO ADDRESS CLUSTERING ENGINE (CIOH & CHANGE DETECTION)
# ==============================================================================

class DisjointSetUnion:
    """Disjoint Set Union (Union-Find) with Path Compression & Rank Optimization."""
    def __init__(self) -> None:
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> None:
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1


@dataclass(frozen=True)
class TxOutput:
    address: str
    value_sat: int
    script_type: str  # e.g., 'p2wpkh', 'p2pkh', 'p2sh'
    is_fresh_address: bool


@dataclass(frozen=True)
class UTXOTransaction:
    txid: str
    inputs: List[Tuple[str, int]]  # List of (input_address, value_sat)
    outputs: List[TxOutput]
    fee_sat: int
    is_coinjoin: bool = False


class UTXOClusterEngine:
    """Clustering engine applying Common Input Ownership & Change Address Heuristics."""
    def __init__(self) -> None:
        self.dsu = DisjointSetUnion()
        self.cluster_balances: Dict[str, int] = {}
        self.processed_txs: Set[str] = set()

    def is_coinjoin_candidate(self, outputs: List[TxOutput]) -> bool:
        """Detects CoinJoin mixer transactions (multiple identical denominations)."""
        if len(outputs) < 3:
            return False
        denominations: Dict[int, int] = {}
        for out in outputs:
            denominations[out.value_sat] = denominations.get(out.value_sat, 0) + 1
        return any(count >= 3 for count in denominations.values())

    def identify_change_output(self, tx: UTXOTransaction) -> Optional[TxOutput]:
        """Heuristic rule: Change address is fresh, matches input script, odd remainder."""
        if len(tx.outputs) != 2 or tx.is_coinjoin:
            return None
        
        out0, out1 = tx.outputs[0], tx.outputs[1]
        if out0.is_fresh_address and not out1.is_fresh_address:
            return out0
        if out1.is_fresh_address and not out0.is_fresh_address:
            return out1
            
        # Round payment amount vs odd change remainder
        is_out0_round = (out0.value_sat % 10_000_000 == 0)
        is_out1_round = (out1.value_sat % 10_000_000 == 0)
        if is_out0_round and not is_out1_round:
            return out1
        if is_out1_round and not is_out0_round:
            return out0

        return None

    def process_transaction(self, tx: UTXOTransaction) -> None:
        """Clusters addresses and updates entity graph."""
        if tx.txid in self.processed_txs:
            return
        self.processed_txs.add(tx.txid)

        # 1. Check CoinJoin invariant
        if tx.is_coinjoin or self.is_coinjoin_candidate(tx.outputs):
            return  # Do NOT merge inputs in CoinJoin to prevent Sybil pollution

        # 2. Common Input Ownership Heuristic (CIOH)
        if len(tx.inputs) > 1:
            first_addr = tx.inputs[0][0]
            for in_addr, _ in tx.inputs[1:]:
                self.dsu.union(first_addr, in_addr)

        # 3. Change Address Heuristic
        change_out = self.identify_change_output(tx)
        if change_out and tx.inputs:
            primary_input_addr = tx.inputs[0][0]
            self.dsu.union(primary_input_addr, change_out.address)

    def get_cluster_id(self, address: str) -> str:
        return self.dsu.find(address)


# ==============================================================================
# 2. CEX NETFLOW & WHALE-TO-EXCHANGE FLOW TRACKER
# ==============================================================================

@dataclass
class FlowAlert:
    timestamp: int
    alert_type: str
    severity: str
    net_flow: float
    whale_ratio: float
    message: str


class CEXFlowTracker:
    """Tracks Centralized Exchange Reserves, Inflow/Outflow velocity, and Whale Ratios."""
    def __init__(self, initial_reserve: float = 1_000_000.0) -> None:
        self.reserve: float = initial_reserve
        self.history: List[Dict[str, float]] = []

    def record_flow(
        self, timestamp: int, inflows: List[float], outflows: List[float]
    ) -> Tuple[float, float, Optional[FlowAlert]]:
        total_inflow = sum(inflows)
        total_outflow = sum(outflows)
        net_flow = total_inflow - total_outflow
        self.reserve += net_flow

        sorted_inflows = sorted(inflows, reverse=True)
        top_10_sum = sum(sorted_inflows[:10])
        whale_ratio = (top_10_sum / total_inflow) if total_inflow > 0 else 0.0

        record = {
            'timestamp': float(timestamp),
            'inflow': total_inflow,
            'outflow': total_outflow,
            'net_flow': net_flow,
            'reserve': self.reserve,
            'whale_ratio': whale_ratio,
        }
        self.history.append(record)

        alert: Optional[FlowAlert] = None
        if whale_ratio >= 0.85 and net_flow > 5_000.0:
            alert = FlowAlert(
                timestamp=timestamp,
                alert_type='WHALE_DUMP_WARNING',
                severity='HIGH',
                net_flow=net_flow,
                whale_ratio=whale_ratio,
                message=f'Heavy Whale Inflow Spike ({whale_ratio*100:.1f}% top dominance). High selling risk.',
            )
        elif net_flow < -10_000.0:
            alert = FlowAlert(
                timestamp=timestamp,
                alert_type='MASSIVE_OUTFLOW_ACCUMULATION',
                severity='MEDIUM',
                net_flow=net_flow,
                whale_ratio=whale_ratio,
                message='Large CEX reserve drainage to cold storage. Supply shock accumulating.',
            )

        return net_flow, whale_ratio, alert


# ==============================================================================
# 3. ON-CHAIN VALUATION ENGINE (MVRV-Z, SOPR, NVT, SSR)
# ==============================================================================

@dataclass(frozen=True)
class SpentUTXO:
    utxo_id: str
    value_btc: float
    price_at_creation: float
    price_at_spent: float
    lifespan_seconds: int


class OnChainValuationEngine:
    """Calculates macro cycle valuation metrics: MVRV-Z, SOPR, aSOPR, NVT, SSR."""

    @staticmethod
    def calculate_mvrv_z(
        current_market_cap: float,
        realized_cap: float,
        historical_market_caps: List[float],
    ) -> Tuple[float, float]:
        if realized_cap <= 0:
            raise ValueError('Realized cap must be strictly positive')
        
        mvrv_ratio = current_market_cap / realized_cap
        
        if len(historical_market_caps) < 2:
            stdev = current_market_cap * 0.2
        else:
            stdev = statistics.stdev(historical_market_caps)
            if stdev == 0:
                stdev = 1.0

        mvrv_z_score = (current_market_cap - realized_cap) / stdev
        return mvrv_ratio, mvrv_z_score

    @staticmethod
    def calculate_sopr(
        spent_utxos: List[SpentUTXO],
        filter_lifespan_seconds: int = 0
    ) -> float:
        total_spent_value_usd = 0.0
        total_created_value_usd = 0.0

        for u in spent_utxos:
            if u.lifespan_seconds < filter_lifespan_seconds:
                continue
            total_spent_value_usd += u.value_btc * u.price_at_spent
            total_created_value_usd += u.value_btc * u.price_at_creation

        if total_created_value_usd == 0:
            return 1.0
        return total_spent_value_usd / total_created_value_usd

    @staticmethod
    def calculate_nvt_ratio(
        market_cap: float,
        daily_volume_usd: float,
        volume_history_90d: Optional[List[float]] = None,
    ) -> Tuple[float, Optional[float]]:
        if daily_volume_usd <= 0:
            raise ValueError('Daily volume must be positive')
        
        nvt_ratio = market_cap / daily_volume_usd
        nvt_signal = None
        if volume_history_90d and len(volume_history_90d) > 0:
            sma_vol = sum(volume_history_90d) / len(volume_history_90d)
            if sma_vol > 0:
                nvt_signal = market_cap / sma_vol

        return nvt_ratio, nvt_signal

    @staticmethod
    def calculate_ssr(
        crypto_market_cap: float,
        total_stablecoin_market_cap: float
    ) -> float:
        if total_stablecoin_market_cap <= 0:
            raise ValueError('Stablecoin market cap must be positive')
        return crypto_market_cap / total_stablecoin_market_cap


# ==============================================================================
# 4. MEMPOOL FORENSICS & FRONT-RUNNING / MEV SANDWICH DETECTOR
# ==============================================================================

@dataclass
class MempoolTx:
    tx_hash: str
    sender: str
    recipient: str
    max_fee_per_gas: int
    priority_fee_per_gas: int
    action: str  # 'SWAP_BUY' or 'SWAP_SELL'
    token_address: str
    amount_in: float
    min_amount_out: float
    gas_limit: int = 200_000

    def effective_gas_price(self, base_fee: int) -> int:
        return min(self.max_fee_per_gas, base_fee + self.priority_fee_per_gas)


@dataclass
class SandwichExploit:
    victim_tx: str
    frontrun_tx: str
    backrun_tx: str
    attacker_address: str
    extracted_profit_est: float
    token_address: str


class MempoolMEVDetector:
    """Forensic engine detecting Priority Gas Auctions and Sandwich Attacks."""
    def __init__(self, base_fee: int = 30) -> None:
        self.base_fee = base_fee

    def detect_sandwich_pattern(
        self, mined_block_txs: List[MempoolTx]
    ) -> List[SandwichExploit]:
        exploits: List[SandwichExploit] = []
        n = len(mined_block_txs)
        if n < 3:
            return exploits

        for i in range(n - 2):
            tx_front = mined_block_txs[i]
            tx_victim = mined_block_txs[i + 1]
            tx_back = mined_block_txs[i + 2]

            if not (tx_front.token_address == tx_victim.token_address == tx_back.token_address):
                continue

            if tx_front.sender != tx_back.sender or tx_front.sender == tx_victim.sender:
                continue

            if (
                tx_front.action == 'SWAP_BUY'
                and tx_victim.action == 'SWAP_BUY'
                and tx_back.action == 'SWAP_SELL'
            ):
                front_eff = tx_front.effective_gas_price(self.base_fee)
                victim_eff = tx_victim.effective_gas_price(self.base_fee)
                if front_eff >= victim_eff:
                    profit_estimate = tx_front.amount_in * 0.04
                    exploits.append(
                        SandwichExploit(
                            victim_tx=tx_victim.tx_hash,
                            frontrun_tx=tx_front.tx_hash,
                            backrun_tx=tx_back.tx_hash,
                            attacker_address=tx_front.sender,
                            extracted_profit_est=profit_estimate,
                            token_address=tx_front.token_address,
                        )
                    )
        return exploits


# ==============================================================================
# 5. DETERMINISTIC INVARIANT TEST SUITE
# ==============================================================================

def run_all_n042_invariants() -> None:
    print("=== [Neuron N042: On-Chain Forensics & Whale Orderflow Test Suite] ===")

    # Test 1: UTXO Clustering & CIOH Heuristic
    cluster_engine = UTXOClusterEngine()
    
    tx1 = UTXOTransaction(
        txid='0xaa11',
        inputs=[('addr_alice_1', 200_000_000), ('addr_alice_2', 300_000_000)],
        outputs=[
            TxOutput('addr_merchant', 400_000_000, 'p2wpkh', is_fresh_address=False),
            TxOutput('addr_alice_change', 99_990_000, 'p2wpkh', is_fresh_address=True),
        ],
        fee_sat=10_000,
        is_coinjoin=False,
    )
    cluster_engine.process_transaction(tx1)
    
    c1 = cluster_engine.get_cluster_id('addr_alice_1')
    c2 = cluster_engine.get_cluster_id('addr_alice_2')
    c_change = cluster_engine.get_cluster_id('addr_alice_change')
    assert c1 == c2 == c_change, 'CIOH & Change Heuristic must cluster Alice addresses into one entity!'

    # Test 2: CoinJoin Filter
    cj_outputs = [
        TxOutput(f'addr_mix_{i}', 10_000_000, 'p2wpkh', is_fresh_address=True) for i in range(5)
    ]
    tx_coinjoin = UTXOTransaction(
        txid='0xcoinjoin',
        inputs=[('addr_bob', 10_500_000), ('addr_charlie', 10_500_000), ('addr_dave', 10_500_000)],
        outputs=cj_outputs,
        fee_sat=15_000,
        is_coinjoin=True,
    )
    cluster_engine.process_transaction(tx_coinjoin)
    assert cluster_engine.get_cluster_id('addr_bob') != cluster_engine.get_cluster_id('addr_charlie'), (
        'CoinJoin transaction must NEVER cluster distinct input signers!'
    )
    print("  [PASS] 1. UTXO Cluster & CoinJoin Filtering Invariants: PASSED")

    # Test 3: CEX NetFlow & Whale-to-Exchange Dominance Alert
    cex_tracker = CEXFlowTracker(initial_reserve=500_000.0)
    inflows_normal = [10.0, 15.0, 5.0, 20.0, 8.0]
    outflows_normal = [50.0]
    net_f, ratio, alert = cex_tracker.record_flow(1700000000, inflows_normal, outflows_normal)
    assert net_f == 8.0
    assert alert is None

    inflows_whale = [10_000.0, 2_000.0, 1_000.0] + [5.0] * 50
    outflows_whale = [1_000.0]
    net_f_w, ratio_w, alert_w = cex_tracker.record_flow(1700003600, inflows_whale, outflows_whale)
    assert alert_w is not None
    assert alert_w.alert_type == 'WHALE_DUMP_WARNING'
    assert ratio_w > 0.85
    print("  [PASS] 2. CEX NetFlow & Whale Dump Ratio Detection: PASSED")

    # Test 4: MVRV-Z Score, SOPR, NVT, SSR Metrics
    val_engine = OnChainValuationEngine()
    hist_mcaps = [500e9, 600e9, 700e9, 800e9, 900e9, 1000e9]
    mvrv, mvrv_z = val_engine.calculate_mvrv_z(
        current_market_cap=1200e9, realized_cap=600e9, historical_market_caps=hist_mcaps
    )
    assert math.isclose(mvrv, 2.0, rel_tol=1e-3), f'Expected MVRV 2.0, got {mvrv}'
    assert mvrv_z > 2.0, f'Expected high positive Z-score, got {mvrv_z}'

    spent_outputs = [
        SpentUTXO('u1', value_btc=1.0, price_at_creation=30_000.0, price_at_spent=60_000.0, lifespan_seconds=86400),
        SpentUTXO('u2', value_btc=2.0, price_at_creation=40_000.0, price_at_spent=50_000.0, lifespan_seconds=86400),
        SpentUTXO('u_noise', value_btc=10.0, price_at_creation=60_000.0, price_at_spent=60_000.0, lifespan_seconds=300),
    ]
    sopr_raw = val_engine.calculate_sopr(spent_outputs, filter_lifespan_seconds=0)
    asopr = val_engine.calculate_sopr(spent_outputs, filter_lifespan_seconds=3600)
    assert sopr_raw > 1.0, 'SOPR should reflect net realized profit'
    assert asopr > 1.0, 'aSOPR should filter short-term noise and reflect true realized profit'

    nvt, nvts = val_engine.calculate_nvt_ratio(
        market_cap=1_000_000_000.0, daily_volume_usd=50_000_000.0, volume_history_90d=[40e6, 50e6, 60e6]
    )
    assert math.isclose(nvt, 20.0, rel_tol=1e-3)
    assert nvts is not None and math.isclose(nvts, 20.0, rel_tol=1e-3)

    ssr = val_engine.calculate_ssr(crypto_market_cap=1_200e9, total_stablecoin_market_cap=150e9)
    assert math.isclose(ssr, 8.0, rel_tol=1e-3)
    print("  [PASS] 3. Macro On-Chain Valuation Engine (MVRV-Z, SOPR, NVT, SSR): PASSED")

    # Test 5: Mempool MEV Front-Running & Sandwich Attack Detection
    mev_detector = MempoolMEVDetector(base_fee=30)
    mined_txs = [
        MempoolTx('0xfr', '0xAttacker', '0xPool', 100, 50, 'SWAP_BUY', '0xTokenX', 10.0, 1000.0),
        MempoolTx('0xvic', '0xVictim', '0xPool', 60, 10, 'SWAP_BUY', '0xTokenX', 5.0, 480.0),
        MempoolTx('0xbr', '0xAttacker', '0xPool', 50, 5, 'SWAP_SELL', '0xTokenX', 10.0, 10.0),
    ]
    exploits = mev_detector.detect_sandwich_pattern(mined_txs)
    assert len(exploits) == 1, 'Should detect exactly 1 sandwich exploit'
    assert exploits[0].victim_tx == '0xvic'
    assert exploits[0].attacker_address == '0xAttacker'
    print("  [PASS] 4. Mempool MEV Sandwich Attack Forensic Engine: PASSED")

    print("[ALL N042 FORENSIC INVARIANTS DETERMINISTICALLY VERIFIED - ZERO DEFECTS]")


if __name__ == '__main__':
    run_all_n042_invariants()
```
