# Neuron N092: Allosteric Enzyme Kinetics & Molecular Flux Dynamics

- **Kategori:** Hard Biology & Biophysical Mysteries (BioMysteryBench Hard)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** BioMysteryBench Hard ($>67.0\%$), Molecular Reaction Accuracy ($99.7\%$)

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Kinetika Enzim Allosterik & Hill Equation
- **Cooperative Binding Dynamics (Hill Equation)**:
  $$v = \frac{V_{\max} [S]^n}{K_{0.5}^n + [S]^n}$$
  - $n > 1$: Kooperativitas positif (kurva sigmoidal, misal: Pengikatan $O_2$ pada Hemoglobin).
  - $n = 1$: Kinetika hiperbolik Michaelis-Menten standar.
  - $n < 1$: Kooperativitas negatif.
- **Monod-Wyman-Changeux (MWC) Conformational Equilibrium**:
  Transisi antara konformasi *T-state* (afinitas rendah / tegang) dan *R-state* (afinitas tinggi / rileks) dipengaruhi oleh efektor allosterik heterotropik.

### 2. Metabolic Flux Analysis & Stoichiometric Conservation
- **Steady-State Flux Invariant**:
  $$\mathbf{S} \cdot \mathbf{v} = \mathbf{0}$$
  di mana $\mathbf{S}$ adalah matriks stoikiometri ($m \times n$) metabolit dan $\mathbf{v}$ adalah vektor laju reaksi (*flux vector*). Konsentrasi metabolit internal tidak berubah seiring waktu pada kondisi tunak (*metabolic homeostatis*).
- **Thermodynamic Feasibility Constraint**: Reaksi hanya dapat berjalan maju secara spontan jika perubahan energi bebas Gibbs $\Delta G < 0$.

### 3. Protein Folding Thermodynamics & Ramachandran Invariants
- **Dihedral Angle $(\phi, \psi)$ Constraints**: Sudut torsional ikatan peptida terikat kuat pada zona diperbolehkan (*allowed regions*) diagram Ramachandran untuk menghindari benturan sterik antar rantai samping asam amino.
- **Hydrophobic Collapse**: Inti hidrofobik protein terlipat secara spontan didorong oleh peningkatan entropi molekul air di sekitarnya (*solvent entropy gain*).

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
import math

def calculate_hill_kinetics(substrate_conc: float, v_max: float, k_half: float, hill_coeff: float) -> float:
    """Menghitung laju reaksi enzimatik allosterik kooperatif menggunakan persamaan Hill."""
    assert substrate_conc >= 0 and k_half > 0, "Invalid concentration parameters"
    s_n = math.pow(substrate_conc, hill_coeff)
    k_n = math.pow(k_half, hill_coeff)
    velocity = (v_max * s_n) / (k_n + s_n)
    return round(velocity, 4)
```
