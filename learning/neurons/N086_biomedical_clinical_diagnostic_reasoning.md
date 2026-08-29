# Neuron N086: Biomedical Clinical Diagnosis & Molecular Pathway Invariants

- **Kategori:** Health & Biomedical Sciences (HealthBench Professional & BioMysteryBench)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** HealthBench ($>80.0\%$), BioMysteryBench ($>70.0\%$)

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Bayesian Clinical Diagnostic Invariants
- **Pre-Test to Post-Test Probability (Fagan's Nomogram)**:
  $$\text{Post-Test Odds} = \text{Pre-Test Odds} \times \text{Likelihood Ratio (LR)}$$
  $$\text{LR}^+ = \frac{\text{Sensitivity}}{1 - \text{Specificity}}, \quad \text{LR}^- = \frac{1 - \text{Sensitivity}}{\text{Specificity}}$$
- **Rule-Out vs Rule-In Criteria**:
  - Uji dengan sensitivitas tinggi ($>95\%$) mengesampingkan penyakit jika negatif (*SnNOut*).
  - Uji dengan spesifisitas tinggi ($>95\%$) mengonfirmasi diagnosis jika positif (*SpPIn*).

### 2. Pharmacokinetics & Drug Interaction Invariants
- **Cytochrome P450 (CYP450) Enzyme Modulation**:
  - *Inhibitor CYP3A4* (misal: Ketokonazol, Klaritromisin) meningkatkan kadar serum substrat sempit (misal: Statin, Imunosupresan) $\implies$ risiko toksisitas.
  - *Inducer CYP3A4* (misal: Rifampisin, Karbamazepin) menurunkan efikasi obat target.
- **Renal & Hepatic Clearance Sizing**: Penyesuaian dosis berbasis *Glomerular Filtration Rate (eGFR / Cockcroft-Gault)* untuk obat indeks terapi sempit (Digoksin, Aminoglikosida).

### 3. Molecular Biology & Genetic Pathways
- **Central Dogma Invariants**: Transkripsi ($DNA \to RNA$), Splicing Intron/Exon, dan Translasi Kodon Triplet dengan toleransi mutasi (Synonymous, Missense, Nonsense, Frameshift).
- **Epigenetic & Signal Transduction Networks**: MAPK/ERK, PI3K/Akt/mTOR, dan regulasi checkpoint imun (PD-1/PD-L1) dalam dinamika onkologi seluler.

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
def compute_bayesian_post_test_probability(pre_test_prob: float, sensitivity: float, specificity: float) -> dict[str, float]:
    """Menghitung probabilitas pasca-uji klinis berbasis teorema Bayes."""
    pre_odds = pre_test_prob / (1.0 - pre_test_prob)
    lr_pos = sensitivity / (1.0 - specificity)
    lr_neg = (1.0 - sensitivity) / specificity
    
    post_odds_pos = pre_odds * lr_pos
    post_prob_pos = post_odds_pos / (1.0 + post_odds_pos)
    
    post_odds_neg = pre_odds * lr_neg
    post_prob_neg = post_odds_neg / (1.0 + post_odds_neg)
    
    return {
        "post_test_prob_positive": round(post_prob_pos, 4),
        "post_test_prob_negative": round(post_prob_neg, 4),
        "lr_positive": round(lr_pos, 2),
        "lr_negative": round(lr_neg, 2)
    }
```
