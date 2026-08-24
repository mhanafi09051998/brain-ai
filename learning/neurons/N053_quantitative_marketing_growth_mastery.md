# Neuron N053: Quantitative Marketing, Growth Science & Causal AdTech Mastery

- **Kategori**: Quantitative Marketing, AdTech Engineering, Causal Inference & Customer Intelligence
- **Tanggal Sintesis**: 2026-08-24
- **Subgoal**: Menguasai dan merekayasa arsitektur machine learning untuk pertumbuhan bisnis presisi tinggi: Marketing Mix Modeling (MMM Bayesian Adstock/Hill Saturation), Causal Uplift Modeling (Persuadables vs Sure Things), Customer Lifetime Value (BG/NBD & Gamma-Gamma), Multi-Touch Attribution (Markov Chains & Shapley Values), serta Recommender Systems.
- **Synaptic Links**: [N001](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N001_executive_decisions.md), [N004](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N004_ponytail_minimality.md), [N009](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N009_peak_algorithms_codex.md), [N011](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N011_mechanical_sympathy_perf.md), [N017](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N017_program_aided_math.md), [N021](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N021_quantitative_gold_crypto_trading.md), [N025](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N025_hft_orderbook_microstructure.md), [N033](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N033_python_high_performance.md), [N035](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N035_event_driven_streaming_cqrs.md), [N044](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N044_statistical_arbitrage_pairs.md), [N050](file:///D:/Agent_Claudia_Autonomus/learning/neurons/N050_systematic_backtesting_wfa.md)
- **Status**: Active Operational Invariant

---

## 1. Peta Repositori, Library & Benchmark Terbaik Dunia

| Domain | Repositori / Framework Terbaik Dunia | Standar Algoritma / Pendekatan | Kasus Penggunaan Kritis |
| :--- | :--- | :--- | :--- |
| **Marketing Mix Modeling (MMM)** | **Meta Robyn** / **Google Meridian** / **PyMC-Marketing** | Bayesian Ridge Regression, Geometric & Weibull Adstock Decay, Hill Saturation Curve | Optimasi alokasi anggaran lintas channel (Google Ads, Meta Ads, TikTok, Offline) tanpa bergantung pada cookie/IDFA pihak ketiga. |
| **Causal Uplift Modeling** | **Uber CausalML** / **Microsoft EconML** | Heterogeneous Treatment Effect (HTE), X-Learner, T-Learner, Causal Forests | Mengisolasi segmen *Persuadables* (hanya membeli jika diiklankan) dan mencegah pemborosan budget pada *Sure Things* (pasti beli tanpa iklan). |
| **Customer Lifetime Value (CLV)** | **Lifetimes (Cam Davidson-Pilon)** / **CLVTools** | BG/NBD (Beta-Geometric / Negative Binomial) + Gamma-Gamma Submodel | Memprediksi probabilitas pelanggan masih aktif ((\\text{alive})$), frekuensi belanja masa depan, dan nilai moneter seumur hidup. |
| **Multi-Touch Attribution (MTA)** | **ChannelAttribution** / **GameTheoretic Shapley** | High-Order Markov Chains (Removal Effect), Shapley Value Attribution | Menentukan bobot kontribusi sebenarnya dari setiap touchpoint (SEO -> FB Ad -> Email -> Direct) dalam konversi multi-channel. |
| **Personalized Recommendations** | **NVIDIA Merlin (Transformers4Rec)** / **RecBole** / **LightFM** | Matrix Factorization, Sequential Transformer for User Sessions, Two-Tower Embeddings | Personalisasi katalog produk, upsell/cross-sell otomatis di e-commerce & aplikasi dengan latensi < 20ms. |
| **Dynamic Pricing & Elasticity** | **Kaggle Grandmaster Pricing Kernels** / **Scikit-Optimize** | Log-Log Price Elasticity of Demand ($\\epsilon = \\frac{\\partial \\ln Q}{\\partial \\ln P}$), Constrained Revenue Optimization | Penetapan harga dinamis real-time untuk memaksimalkan total margin laba atau GMV pada produk fluktuatif. |

---

## 2. Inti Matematika & Invarian Rekayasa Marketing

### A. Marketing Mix Modeling: Adstock & Diminishing Returns (Hill Function)
Iklan tidak hanya berdampak seketika, tetapi memiliki efek sisa (*carryover/memory effect*) yang meluruh seiring waktu:

\\text{Adstock}_t = X_t + \\alpha \\cdot \\text{Adstock}_{t-1} \\quad (0 < \\alpha < 1)

Setiap channel iklan memiliki titik jenuh (*diminishing returns*). Menambah budget melampaui batas saturasi menghasilkan *wasted spend*:

\\text{Hill}(x; K, S) = \\frac{x^S}{K^S + x^S}
- $ (*half-saturation point*): Biaya yang dibutuhkan untuk mencapai 50% dari potensi konversi maksimal.
- $ (*slope/shape*): Kecepatan kejenuhan konversi channel.

### B. Causal Uplift Matrix: 4 Kuadran Targeting Presisi
Dalam periklanan berbayar, membagi audiens berdasarkan respon kausalitas menghemat 30%–60% ad spend:

| Kuadran Audiens | Definisi Respon | Tindakan Optimal Sistem |
| :--- | :--- | :--- |
| **1. Persuadables (Target Utama)** | Membeli **hanya jika** melihat iklan. | **Prioritaskan 80%+ Budget Iklan.** |
| **2. Sure Things (Organik Alami)** | Membeli **baik ada iklan maupun tidak**. | **Blokir / Exclude dari Audiens Iklan.** |
| **3. Lost Causes (Tidak Tertarik)** | Tidak akan pernah membeli, walau diiklankan. | **Blokir / Exclude dari Audiens Iklan.** |
| **4. Sleeping Dogs (Do-Not-Disturb)** | Berhenti berlangganan / komplain jika diiklankan. | **Blacklist Total dari Kampanye.** |

Uplift Score dihitung via Causal T-Learner:
\\tau(x) = E[Y | X=x, W=1] - E[Y | X=x, W=0]

### C. BG/NBD Customer Lifetime Value
Memodelkan dua proses acak simultan untuk pelanggan non-kontraktual:
1. **Proses Transaksi:** Selama aktif (*alive*), jumlah transaksi mengikuti *Poisson Process* dengan rate $\\lambda$. Heterogenitas antar pelanggan mengikuti distribusi Gamma(, \\alpha$).
2. **Proses Drop-out (Churn):** Setelah setiap transaksi, pelanggan memiliki probabilitas $ untuk tidak aktif lagi (*churn*), mengikuti distribusi Beta(, b$).

---

## 3. Kode Nukleus Produksi (Zero-Bloat Self-Contained Engine)

Berikut implementasi lengkap deterministik dalam Python murni untuk modul MMM Adstock, Causal Uplift Segmenter, dan BG/NBD CLV Calculator.

\\python
#!/usr/bin/env python3
"""
Claudia Quantitative Marketing, Growth Science and Causal AdTech Nucleus Engine
Pure, zero-external-dependency production algorithms for:
1. Marketing Mix Modeling (Geometric Adstock + Hill Saturation Response)
2. Causal Uplift Modeling and Audience Quadrant Segmentation
3. BG/NBD Customer Lifetime Value (P(Alive) and Expected Future Purchases)
"""

import math
import sys
from typing import List, Dict, Any, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except:
        pass

# ==========================================
# 1. MARKETING MIX MODELING (MMM) NUCLEUS
# ==========================================
class MarketingMixEngine:
    @staticmethod
    def geometric_adstock(spend_series: List[float], decay_rate: float) -> List[float]:
        """
        Calculate Geometric Adstock carryover decay.
        decay_rate: float between 0.0 (no memory) and 1.0 (infinite memory).
        """
        assert 0.0 <= decay_rate <= 1.0, "Decay rate must be in [0, 1]"
        adstocked = []
        prev = 0.0
        for spend in spend_series:
            current = spend + (prev * decay_rate)
            adstocked.append(round(current, 4))
            prev = current
        return adstocked

    @staticmethod
    def hill_saturation(adstock_value: float, half_sat_k: float, slope_s: float) -> float:
        """
        Calculate Diminishing Returns via Hill Function.
        half_sat_k: Spend needed to achieve 50% max response (half-saturation).
        slope_s: Hill slope/shape parameter (> 0).
        """
        assert half_sat_k > 0, "Half-saturation K must be > 0"
        assert slope_s > 0, "Slope S must be > 0"
        if adstock_value <= 0:
            return 0.0
        x_s = math.pow(adstock_value, slope_s)
        k_s = math.pow(half_sat_k, slope_s)
        return round(x_s / (k_s + x_s), 6)

    @classmethod
    def optimize_channel_budget(
        cls,
        total_budget: float,
        channel_configs: Dict[str, Dict[str, float]],
        step: float = 100.0
    ) -> Dict[str, Any]:
        """
        Greedy Marginal ROI Budget Allocator across Ad Channels.
        """
        channels = list(channel_configs.keys())
        allocations = {ch: 0.0 for ch in channels}
        remaining_budget = total_budget

        while remaining_budget >= step:
            best_ch = None
            best_marginal_gain = -1.0
            
            for ch in channels:
                curr_alloc = allocations[ch]
                cfg = channel_configs[ch]
                k, s, max_val = cfg["half_sat_k"], cfg["slope_s"], cfg["max_response"]
                
                resp_curr = cls.hill_saturation(curr_alloc, k, s) * max_val
                resp_next = cls.hill_saturation(curr_alloc + step, k, s) * max_val
                marginal_gain = resp_next - resp_curr
                
                if marginal_gain > best_marginal_gain:
                    best_marginal_gain = marginal_gain
                    best_ch = ch

            if best_ch is not None and best_marginal_gain > 0:
                allocations[best_ch] += step
                remaining_budget -= step
            else:
                break

        total_response = sum(
            cls.hill_saturation(allocations[ch], channel_configs[ch]["half_sat_k"], channel_configs[ch]["slope_s"]) * channel_configs[ch]["max_response"]
            for ch in channels
        )

        return {
            "total_budget_allocated": total_budget - remaining_budget,
            "allocations": allocations,
            "expected_total_conversions": round(total_response, 2)
        }

# ==========================================
# 2. CAUSAL UPLIFT TARGETING NUCLEUS
# ==========================================
class CausalUpliftEngine:
    """
    Segments audience into 4 Causal Quadrants to eliminate ad budget waste:
    1. PERSUADABLE: High uplift (targets of paid ads)
    2. SURE_THING: High baseline conversion regardless of ad (exclude to save money)
    3. LOST_CAUSE: Low conversion regardless of ad (exclude)
    4. SLEEPING_DOG: Negative uplift / disturbed by ad (blacklist)
    """
    @staticmethod
    def calculate_individual_uplift(p_treatment: float, p_control: float) -> float:
        """Treatment Effect: tau = P(Y=1|W=1) - P(Y=1|W=0)"""
        return round(p_treatment - p_control, 6)

    @classmethod
    def classify_customer(
        cls,
        p_treatment: float,
        p_control: float,
        uplift_threshold: float = 0.05,
        organic_threshold: float = 0.50
    ) -> Tuple[str, str]:
        tau = cls.calculate_individual_uplift(p_treatment, p_control)
        
        if tau < -0.02:
            return "SLEEPING_DOG", "DO_NOT_CONTACT (Risk of Churn/Spam report)"
        elif tau >= uplift_threshold and p_control < organic_threshold:
            return "PERSUADABLE", "TARGET_IMMEDIATELY (High Incrementality ROI)"
        elif p_control >= organic_threshold and tau < uplift_threshold:
            return "SURE_THING", "EXCLUDE_FROM_PAID_ADS (Organic Conversion Guaranteed)"
        else:
            return "LOST_CAUSE", "EXCLUDE_FROM_PAID_ADS (Zero conversion probability)"

# ==========================================
# 3. BG/NBD CUSTOMER LIFETIME VALUE NUCLEUS
# ==========================================
class BG_NBDEngine:
    """
    Beta-Geometric / Negative Binomial Distribution model for non-contractual CLV.
    Calculates P(Alive) and Expected Future Transactions.
    """
    @staticmethod
    def probability_alive(
        frequency: int,
        recency: float,
        tenure: float,
        r: float = 0.8,
        alpha: float = 4.0,
        a: float = 0.6,
        b: float = 2.5
    ) -> float:
        """
        P(Alive | frequency x, recency tx, tenure T)
        """
        if frequency == 0:
            return 1.0
            
        term1 = (a / (b + frequency - 1))
        term2 = math.pow((alpha + tenure) / (alpha + recency), r + frequency)
        p_alive = 1.0 / (1.0 + term1 * term2)
        return round(min(max(p_alive, 0.0), 1.0), 4)

    @classmethod
    def expected_future_purchases(
        cls,
        frequency: int,
        recency: float,
        tenure: float,
        t_future: float,
        r: float = 0.8,
        alpha: float = 4.0,
        a: float = 0.6,
        b: float = 2.5
    ) -> float:
        """
        Expected transactions in future window of duration t_future.
        """
        p_alv = cls.probability_alive(frequency, recency, tenure, r, alpha, a, b)
        # Expected baseline transaction rate
        lambda_rate = (r + frequency) / (alpha + tenure)
        expected_tx = p_alv * lambda_rate * t_future
        return round(max(expected_tx, 0.0), 3)

    @classmethod
    def calculate_clv(
        cls,
        expected_tx: float,
        avg_order_value: float,
        profit_margin: float = 0.30
    ) -> float:
        """Total Net Monetary Lifetime Value"""
        return round(expected_tx * avg_order_value * profit_margin, 2)

# ==========================================
# 4. SELF-CONTAINED DETERMINISTIC VERIFICATION
# ==========================================
def run_verification_tests():
    print("[*] Menjalankan Suite Verifikasi Deterministik Quantitative Marketing Engine...")
    
    # 1. Test Adstock
    spends = [100.0, 0.0, 0.0, 50.0]
    adstock = MarketingMixEngine.geometric_adstock(spends, decay_rate=0.5)
    assert adstock == [100.0, 50.0, 25.0, 62.5], f"Adstock mismatch: {adstock}"
    print("  [✓] Test 1: Geometric Adstock Decay Valid.")

    # 2. Test Hill Saturation
    sat_zero = MarketingMixEngine.hill_saturation(0.0, half_sat_k=100.0, slope_s=1.0)
    sat_half = MarketingMixEngine.hill_saturation(100.0, half_sat_k=100.0, slope_s=1.0)
    assert sat_zero == 0.0
    assert sat_half == 0.5, f"Half-saturation must be 0.5, got {sat_half}"
    print("  [✓] Test 2: Hill Diminishing Returns Function Valid.")

    # 3. Test Budget Allocation Optimizer
    channels = {
        "Google_Search": {"half_sat_k": 500.0, "slope_s": 1.2, "max_response": 200.0},
        "Meta_Ads": {"half_sat_k": 300.0, "slope_s": 1.0, "max_response": 150.0},
        "TikTok_Ads": {"half_sat_k": 800.0, "slope_s": 1.5, "max_response": 250.0}
    }
    alloc_res = MarketingMixEngine.optimize_channel_budget(total_budget=1500.0, channel_configs=channels, step=100.0)
    assert alloc_res["total_budget_allocated"] == 1500.0
    assert sum(alloc_res["allocations"].values()) == 1500.0
    print(f"  [✓] Test 3: Greedy Budget Allocator Valid (Allocations: {alloc_res['allocations']}).")

    # 4. Test Causal Uplift Quadrants
    seg1, act1 = CausalUpliftEngine.classify_customer(p_treatment=0.45, p_control=0.05)
    assert seg1 == "PERSUADABLE", f"Expected PERSUADABLE, got {seg1}"
    
    seg2, act2 = CausalUpliftEngine.classify_customer(p_treatment=0.82, p_control=0.80)
    assert seg2 == "SURE_THING", f"Expected SURE_THING, got {seg2}"
    
    seg3, act3 = CausalUpliftEngine.classify_customer(p_treatment=0.01, p_control=0.01)
    assert seg3 == "LOST_CAUSE", f"Expected LOST_CAUSE, got {seg3}"
    
    seg4, act4 = CausalUpliftEngine.classify_customer(p_treatment=0.05, p_control=0.20)
    assert seg4 == "SLEEPING_DOG", f"Expected SLEEPING_DOG, got {seg4}"
    print("  [✓] Test 4: Causal Uplift 4-Quadrant Classifier Valid.")

    # 5. Test BG/NBD CLV
    p_alv_active = BG_NBDEngine.probability_alive(frequency=5, recency=18.0, tenure=20.0)
    p_alv_dormant = BG_NBDEngine.probability_alive(frequency=1, recency=2.0, tenure=50.0)
    assert p_alv_active > p_alv_dormant, "Active customer must have higher P(Alive) than dormant customer"
    
    future_tx = BG_NBDEngine.expected_future_purchases(frequency=4, recency=15.0, tenure=18.0, t_future=12.0)
    clv_val = BG_NBDEngine.calculate_clv(future_tx, avg_order_value=250.0, profit_margin=0.40)
    assert clv_val > 0.0
    print(f"  [✓] Test 5: BG/NBD Customer Lifetime Value Valid (Expected Tx: {future_tx}, CLV: ${clv_val}).")

    print("\n✨ SEMUA TEST DETERMINISTIK QUANTITATIVE MARKETING ENGINE 100% SUKSES.\n")

if __name__ == "__main__":
    run_verification_tests()

\
---

## 4. Invarian Disiplin Rekayasa AdTech
1. **No Untargeted Blanket Spend**: Jangan pernah meluncurkan kampanye paid ads ke seluruh audiens tanpa filter *Causal Uplift* (hilangkan *Sure Things* dan *Lost Causes*).
2. **Adstock & Saturation Aware**: Optimasi budget wajib mematuhi batas *Hill Saturation Curve* (titik infleksi marjinal berkurang).
3. **Deterministic & Zero-Overhead**: Formula perhitungan CLV dan MMM wajib dieksekusi secara terdistribusi dengan latensi minimal.
