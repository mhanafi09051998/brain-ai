# N078: Zero-Knowledge Proofs, R1CS Arithmetic Circuits & Verifiable State Transitions

- **Category:** Applied Cryptography & Verifiable Computation
- **Date:** 2026-08-27
- **Status:** Active Operational Invariant

---

## 🎯 Core Invariants & Mathematical Framework

### 1. Rank-1 Constraint Systems (R1CS) over Finite Field $\mathbb{F}_p$
Every verifiable computational statement is flattened into an arithmetic circuit over a prime Galois field $\mathbb{F}_p$.
- **Witness Vector:** $\mathbf{w} = [1, x_1, \dots, x_l, w_1, \dots, w_m]^T \in \mathbb{F}_p^{1+l+m}$, where $\mathbf{x}$ are public inputs and $\mathbf{w}_{\text{priv}}$ are private witness variables.
- **R1CS Bilinear System Invariant:** An assignment $\mathbf{w}$ satisfies $n$ constraints if and only if:
  $$\langle \mathbf{A}_i, \mathbf{w} \rangle \cdot \langle \mathbf{B}_i, \mathbf{w} \rangle = \langle \mathbf{C}_i, \mathbf{w} \rangle \pmod p \quad \forall i \in \{1, \dots, n\}$$
  In matrix form: $(\mathbf{A}\mathbf{w}) \circ (\mathbf{B}\mathbf{w}) = \mathbf{C}\mathbf{w}$, where $\circ$ is the Hadamard (entrywise) vector product.

### 2. Quadratic Arithmetic Programs (QAP) & Polynomial Divisibility
Using Lagrange interpolation on evaluation points $\{r_1, \dots, r_n\} \subset \mathbb{F}_p$, constraint matrices map to polynomials $A_j(x), B_j(x), C_j(x)$:
- **Linear Combination Polynomials:**
  $$A(x) = \sum_{j=0}^{m+l} w_j A_j(x), \quad B(x) = \sum_{j=0}^{m+l} w_j B_j(x), \quad C(x) = \sum_{j=0}^{m+l} w_j C_j(x)$$
- **Target Vanishing Polynomial:** $T(x) = \prod_{i=1}^n (x - r_i)$.
- **Divisibility Invariant (Soundness Guarantee):** Witness $\mathbf{w}$ is valid $\iff P(x) = A(x)B(x) - C(x)$ is exactly divisible by $T(x)$ in $\mathbb{F}_p[x]$:
  $$A(x)B(x) - C(x) = H(x) \cdot T(x) \pmod p$$
  Where $H(x) \in \mathbb{F}_p[x]$ is the degree-$(n-2)$ quotient polynomial.

### 3. SNARK Architectures: Groth16 vs. PlonK KZG Commitments
- **Groth16:** Minimal proof overhead ($3$ curve elements: $A \in \mathbb{G}_1, B \in \mathbb{G}_2, C \in \mathbb{G}_1$). Pairing check:
  $$e(A, B) = e(\alpha, \beta) + e\left(\sum_{i=0}^l x_i \frac{\beta A_i(x) + \alpha B_i(x) + C_i(x)}{\gamma}, \gamma\right) + e(C, \delta)$$
  *Tradeoff:* Requires per-circuit toxic waste $\tau = (\alpha, \beta, \gamma, \delta, x)$ ceremony.
- **PlonK:** Universal and updatable Structured Reference String (SRS) $[x^i]_1$. Utilizes permutation grand-product arguments $Z(X)$ for wire routing and KZG polynomial commitments evaluated at Fiat-Shamir challenge $\zeta \in \mathbb{F}_p$.

### 4. Zero-Knowledge Verifiable State Transition Invariant
For a state transition $S_{k+1} = \mathcal{F}(S_k, \text{Tx})$:
$$\text{VerifyProof}\left(\text{PublicInputs}(S_k, S_{k+1}, \text{Hash}(\text{Tx})), \pi\right) = 1 \implies \exists \text{Tx} \text{ s.t. } S_{k+1} = \mathcal{F}(S_k, \text{Tx})$$
Verification complexity is $O(|\text{public\_inputs}| + \log n)$, independent of witness execution trace length.

---

## 💻 Zero-Dependency Production Implementation

```python
"""
N078: Finite Field Arithmetic, R1CS Engine, QAP Divisibility & Verifiable State Transitions.
Pure Python standard library implementation with zero external dependencies.
"""
from typing import List, Tuple, Optional

# Prime field modulus: BN254 scalar subfield prime
FIELD_MODULUS = 21888242871839275222246405745257275088548364400416034343698204186575808495617

class FieldElement:
    """Galois Field F_p element with complete modular arithmetic."""
    __slots__ = ('val',)
    def __init__(self, val: int):
        self.val = val % FIELD_MODULUS

    def __add__(self, other):
        o = other.val if isinstance(other, FieldElement) else other
        return FieldElement(self.val + o)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        o = other.val if isinstance(other, FieldElement) else other
        return FieldElement(self.val - o)

    def __rsub__(self, other):
        o = other.val if isinstance(other, FieldElement) else other
        return FieldElement(o - self.val)

    def __neg__(self):
        return FieldElement(-self.val)

    def __mul__(self, other):
        o = other.val if isinstance(other, FieldElement) else other
        return FieldElement(self.val * o)

    def __rmul__(self, other):
        return self.__mul__(other)

    def inv(self):
        if self.val == 0:
            raise ZeroDivisionError("Field division by zero")
        return FieldElement(pow(self.val, FIELD_MODULUS - 2, FIELD_MODULUS))

    def __truediv__(self, other):
        o = other if isinstance(other, FieldElement) else FieldElement(other)
        return self * o.inv()

    def __eq__(self, other):
        o = other.val if isinstance(other, FieldElement) else other % FIELD_MODULUS
        return self.val == o

    def __repr__(self):
        return f"F({self.val})"

class Polynomial:
    """Dense polynomial over F_p with standard operations."""
    def __init__(self, coeffs: List[FieldElement]):
        self.coeffs = [c if isinstance(c, FieldElement) else FieldElement(c) for c in coeffs]
        self._trim()

    def _trim(self):
        while len(self.coeffs) > 1 and self.coeffs[-1].val == 0:
            self.coeffs.pop()

    def degree(self) -> int:
        return len(self.coeffs) - 1

    def eval(self, x: FieldElement) -> FieldElement:
        res = FieldElement(0)
        p = FieldElement(1)
        for c in self.coeffs:
            res = res + (c * p)
            p = p * x
        return res

    def __add__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c = []
        for i in range(n):
            v1 = self.coeffs[i] if i < len(self.coeffs) else FieldElement(0)
            v2 = other.coeffs[i] if i < len(other.coeffs) else FieldElement(0)
            c.append(v1 + v2)
        return Polynomial(c)

    def __sub__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c = []
        for i in range(n):
            v1 = self.coeffs[i] if i < len(self.coeffs) else FieldElement(0)
            v2 = other.coeffs[i] if i < len(other.coeffs) else FieldElement(0)
            c.append(v1 - v2)
        return Polynomial(c)

    def __mul__(self, other):
        res = [FieldElement(0)] * (len(self.coeffs) + len(other.coeffs) - 1)
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                res[i + j] = res[i + j] + (a * b)
        return Polynomial(res)

    def divmod(self, divisor: 'Polynomial') -> Tuple['Polynomial', 'Polynomial']:
        """Polynomial long division: returns (quotient, remainder)."""
        if divisor.degree() == 0 and divisor.coeffs[0].val == 0:
            raise ZeroDivisionError("Polynomial division by zero")
        quotient = [FieldElement(0)] * max(1, self.degree() - divisor.degree() + 1)
        rem = [c for c in self.coeffs]

        while len(rem) >= len(divisor.coeffs) and any(c.val != 0 for c in rem):
            deg_diff = len(rem) - len(divisor.coeffs)
            lead_coeff = rem[-1] / divisor.coeffs[-1]
            quotient[deg_diff] = lead_coeff

            for i, c in enumerate(divisor.coeffs):
                rem[deg_diff + i] = rem[deg_diff + i] - (lead_coeff * c)
            while len(rem) > 1 and rem[-1].val == 0:
                rem.pop()

        return Polynomial(quotient), Polynomial(rem)

class R1CS:
    """Rank-1 Constraint System builder and validator: <A_i, w> * <B_i, w> = <C_i, w>."""
    def __init__(self, num_vars: int):
        self.num_vars = num_vars  # w = [1, x_public..., w_private...]
        self.A: List[List[FieldElement]] = []
        self.B: List[List[FieldElement]] = []
        self.C: List[List[FieldElement]] = []

    def add_constraint(self, a_row: List[int], b_row: List[int], c_row: List[int]):
        self.A.append([FieldElement(x) for x in a_row])
        self.B.append([FieldElement(x) for x in b_row])
        self.C.append([FieldElement(x) for x in c_row])

    def is_satisfied(self, witness: List[int]) -> bool:
        w = [FieldElement(x) for x in witness]
        for i in range(len(self.A)):
            a_val = sum((self.A[i][j] * w[j]).val for j in range(self.num_vars)) % FIELD_MODULUS
            b_val = sum((self.B[i][j] * w[j]).val for j in range(self.num_vars)) % FIELD_MODULUS
            c_val = sum((self.C[i][j] * w[j]).val for j in range(self.num_vars)) % FIELD_MODULUS
            if (a_val * b_val) % FIELD_MODULUS != c_val:
                return False
        return True

def lagrange_interpolation(points: List[Tuple[FieldElement, FieldElement]]) -> Polynomial:
    """Computes interpolating polynomial passing through given (x, y) coordinates."""
    total_poly = Polynomial([FieldElement(0)])
    n = len(points)
    for i in range(n):
        xi, yi = points[i]
        basis = Polynomial([FieldElement(1)])
        denom = FieldElement(1)
        for j in range(n):
            if i != j:
                xj, _ = points[j]
                basis = basis * Polynomial([-xj, FieldElement(1)])
                denom = denom * (xi - xj)
        term = basis * Polynomial([yi / denom])
        total_poly = total_poly + term
    return total_poly

def r1cs_to_qap(r1cs: R1CS, witness: List[int]) -> Tuple[Polynomial, Polynomial, Polynomial, Polynomial, Polynomial]:
    """Converts R1CS and witness to QAP polynomials: returns (A(x), B(x), C(x), T(x), H(x))."""
    n_constraints = len(r1cs.A)
    roots = [FieldElement(i + 1) for i in range(n_constraints)]
    w = [FieldElement(x) for x in witness]

    # Vanishing polynomial T(x) = prod(x - r_i)
    t_poly = Polynomial([FieldElement(1)])
    for r in roots:
        t_poly = t_poly * Polynomial([-r, FieldElement(1)])

    # Construct A(x), B(x), C(x) by interpolating column matrices
    a_poly = Polynomial([FieldElement(0)])
    b_poly = Polynomial([FieldElement(0)])
    c_poly = Polynomial([FieldElement(0)])

    for j in range(r1cs.num_vars):
        pts_a = [(roots[i], r1cs.A[i][j]) for i in range(n_constraints)]
        pts_b = [(roots[i], r1cs.B[i][j]) for i in range(n_constraints)]
        pts_c = [(roots[i], r1cs.C[i][j]) for i in range(n_constraints)]
        poly_aj = lagrange_interpolation(pts_a)
        poly_bj = lagrange_interpolation(pts_b)
        poly_cj = lagrange_interpolation(pts_c)

        a_poly = a_poly + (poly_aj * Polynomial([w[j]]))
        b_poly = b_poly + (poly_bj * Polynomial([w[j]]))
        c_poly = c_poly + (poly_cj * Polynomial([w[j]]))

    p_poly = (a_poly * b_poly) - c_poly
    h_poly, rem = p_poly.divmod(t_poly)
    return a_poly, b_poly, c_poly, t_poly, h_poly

if __name__ == "__main__":
    # Example: Prove knowledge of private x, y such that x * y = 35 and x + y = 12
    # Witness vector w = [1 (ONE), out_prod=35, out_sum=12, x=5, y=7] (size 5)
    r1cs = R1CS(num_vars=5)
    # Constraint 1: x * y = out_prod -> (0, 0, 0, 1, 0) * (0, 0, 0, 0, 1) = (0, 1, 0, 0, 0)
    r1cs.add_constraint([0, 0, 0, 1, 0], [0, 0, 0, 0, 1], [0, 1, 0, 0, 0])
    # Constraint 2: (x + y) * 1 = out_sum -> (0, 0, 0, 1, 1) * (1, 0, 0, 0, 0) = (0, 0, 1, 0, 0)
    r1cs.add_constraint([0, 0, 0, 1, 1], [1, 0, 0, 0, 0], [0, 0, 1, 0, 0])

    valid_witness = [1, 35, 12, 5, 7]
    invalid_witness = [1, 35, 12, 6, 6]  # 6*6=36 != 35

    assert r1cs.is_satisfied(valid_witness), "Valid witness rejected by R1CS"
    assert not r1cs.is_satisfied(invalid_witness), "Invalid witness falsely accepted by R1CS"

    # QAP Divisibility Proof Check
    a_p, b_p, c_p, t_p, h_p = r1cs_to_qap(r1cs, valid_witness)
    diff = (a_p * b_p) - c_p
    reconstructed = h_p * t_p
    _, rem = diff.divmod(t_p)
    assert rem.degree() == 0 and rem.coeffs[0].val == 0, "QAP Divisibility Invariant Failed: P(x) != H(x)*T(x)"
    print(f"N078 Self-Check Passed: R1CS Validated, QAP Exact Quotient Deg={h_p.degree()}, Remainder={rem.coeffs[0].val}")
```

---

## 🔍 Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Prevention & Algorithmic Guard |
| :--- | :--- | :--- |
| **Underconstrained Circuit (Missing Wire Constraint)** | Developer omits constraint on intermediate witness variable, allowing prover to forge state. | Automated static symbolic execution checking all witness degrees of freedom against constraint rank. |
| **Public Input Malleability** | Public parameters not bound cryptographically to proof transcript (weak Fiat-Shamir). | Hash public inputs directly into challenge generation: $\zeta = \mathcal{H}_{\text{sponge}}(\text{SRS}, \mathbf{x}, \pi_{\text{comm}})$. |
| **Field Overflow / Wrap Exploits** | Circuit assumes arithmetic order ($a < b$) without enforcing explicit binary bit-range checks. | Decompose integer values into binary wire commitments: $\sum_{i=0}^{k-1} 2^i b_i = v$ and enforce $b_i(1 - b_i) = 0$. |
| **Trusted Setup Toxic Waste Breach** | Multi-party computation (MPC) ceremony failure leaks toxic secret $(\tau)$, enabling arbitrary forged proofs. | Migrate to universal, transparent, or updatable powers-of-tau ceremonies (PlonK/KZG or STARKs with FRI). |
| **Unsound Polynomial Division Remainder** | Prover constructs non-divisible $P(x)$, but verifier only evaluates at predictable query points. | Schwartz-Zippel Lemma invariant: Verify commitment identity at random secret evaluation challenge $\zeta \in \mathbb{F}_p$. |

---

## 🔒 Execution Discipline & Operational Invariants

1. **Ponytail YAGNI:** Eliminate heavy C++ / Rust cryptographic dependencies for foundational verification; execute complete R1CS validation and QAP polynomial algebra via deterministic field arithmetic.
2. **Single Root Fix:** When circuit soundness breaks, enforce missing linear wire constraints at the R1CS layer rather than wrapping verification with heuristic off-chain assert checks.
3. **Line Count Guard:** Strictly bounded below 300 lines of mathematically rigorous zero-knowledge invariant specifications.
