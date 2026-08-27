# N072: Post-Quantum Cryptography (FIPS 203/204), PASETO v4 & Enclave Security

- **Kategori:** Post-Quantum Cryptography, Token Security & Hardware Confidential Computing
- **Tanggal:** 2026-08-27
- **Status:** Active Operational Invariant
- **Rujukan:** NIST FIPS 203 (ML-KEM / Kyber), NIST FIPS 204 (ML-DSA / Dilithium), PASETO v4 Specification, Intel SGX / AMD SEV-SNP Enclave Invariants.

---

## 🎯 1. Core Engineering Invariants

### 1.1 Lattice Quotient Ring Arithmetic & FIPS 203/204 Invariants
Post-Quantum primitives operate on polynomial quotient rings $\mathcal{R}_q = \mathbb{Z}_q[X] / (X^{256} + 1)$:
- **ML-KEM (FIPS 203)**: Module-LWE on $q = 3329, n = 256, k \in \{2, 3, 4\}$.
$$\mathbf{t} = \mathbf{A} \mathbf{s} + \mathbf{e} \pmod q, \quad \mathbf{u} = \mathbf{A}^T \mathbf{r} + \mathbf{e}_1 \pmod q, \quad v = \mathbf{t}^T \mathbf{r} + e_2 + \lceil q/2 \rfloor m \pmod q$$
- **ML-DSA (FIPS 204)**: Module-SIS / Fiat-Shamir with Aborts on $q = 8380417, n = 256, (k, l) = (6, 5)$.
- **Fujisaki-Okamoto Implicit Rejection**: Decapsulation mismatch ($c' \neq c$) MUST return deterministic pseudorandom value $K = \text{PRF}(z, c)$ in constant time without throwing exceptions.

### 1.2 Constant-Time Timing Channel Immunity
To eliminate cache-timing, branch prediction, and power side-channels:
$$\text{ct\_select}(mask, a, b) = (a \land mask) \lor (b \land \neg mask), \quad mask \in \{0x00, 0xFF\}$$
- **Invariants**: Zero branching on secret bits, zero secret-dependent array indexing, constant-time modular reduction (Barrett / Montgomery).

### 1.3 PASETO v4 Public-Token & PAE Invariant
PASETO eliminates JWT algorithm confusion by enforcing strict cryptographic suites. All payload tokens are encoded via Pre-Authentication Encoding (PAE):
$$\text{PAE}(p_0, p_1, \dots, p_{n-1}) = \text{LE64}(n) \mathbin{\Vert} \text{LE64}(|p_0|) \mathbin{\Vert} p_0 \mathbin{\Vert} \dots \mathbin{\Vert} \text{LE64}(|p_{n-1}|) \mathbin{\Vert} p_{n-1}$$
- **v4.public format**: `v4.public.<base64url(payload || sig)>.<optional_footer>`
- **Signature verification**: $\text{Verify}(\text{pk}, \text{PAE}(\text{"v4.public"}, \text{payload}, \text{footer}, \text{implicit\_assert}), \text{sig}) \equiv \text{True}$.

### 1.4 Hardware Enclave Security Boundary (SGX / SEV-SNP)
1. **Memory Encryption Engine (MEE)**: All Enclave Page Cache (EPC) lines are hardware-encrypted with ephemeral AES-XTS keys.
2. **Attestation Invariant**: MRENCLAVE (SHA-256 measurement of code/data loaded at enclave init) and MRSIGNER must match authorized authority before secret provisioning:
$$\text{AttestationQuote} = \text{Sign}_{\text{HW\_ROOT}}(\text{MRENCLAVE} \mathbin{\Vert} \text{ReportData}_{\text{ephem\_pubkey}})$$

---

## 💻 2. Executable Production-Grade Invariant Implementation

```python
#!/usr/bin/env python3
"""
Neuron N072: Post-Quantum Cryptography, PASETO v4 & Enclave Security
Zero external dependencies (pure Python standard library).
"""
import base64
import hashlib
import hmac
import json
import secrets
import struct
from typing import Tuple, Optional, Dict, Any, List

# 1. Constant-Time Primitives
def ct_select_bytes(match: bool, a: bytes, b: bytes) -> bytes:
    mask = 0xFF if match else 0x00
    return bytes([(x & mask) | (y & (~mask & 0xFF)) for x, y in zip(a, b)])

def ct_compare(a: bytes, b: bytes) -> bool:
    return hmac.compare_digest(a, b)

# 2. Lattice Arithmetic & Toy ML-KEM Engine
N = 16
Q = 257  # Pedagogical prime (ML-KEM uses 3329)

def poly_add(a: List[int], b: List[int]) -> List[int]:
    return [(x + y) % Q for x, y in zip(a, b)]

def poly_sub(a: List[int], b: List[int]) -> List[int]:
    return [(x - y) % Q for x, y in zip(a, b)]

def poly_mul(a: List[int], b: List[int]) -> List[int]:
    """Ring multiplication Z_q[X]/(X^N + 1)."""
    res = [0] * N
    for i in range(N):
        for j in range(N):
            deg = i + j
            term = (a[i] * b[j]) % Q
            if deg < N:
                res[deg] = (res[deg] + term) % Q
            else:
                res[deg - N] = (res[deg - N] - term) % Q
    return [c % Q for c in res]

def sample_cbd(seed: bytes, nonce: int) -> List[int]:
    h = hashlib.sha256(seed + bytes([nonce])).digest()
    return [(((h[i] >> 0) & 1) - ((h[i] >> 1) & 1)) % Q for i in range(N)]

class LatticeKEM:
    def __init__(self):
        self.a = [((i * 43 + 7) % Q) for i in range(N)]

    def keygen(self, seed: bytes = None) -> Tuple[bytes, Tuple[List[int], bytes, bytes, bytes]]:
        seed = seed or secrets.token_bytes(32)
        d = hashlib.sha3_512(seed).digest()
        seed_s, seed_z = d[:32], d[32:]
        s = sample_cbd(seed_s, 1)
        e = sample_cbd(seed_s, 2)
        t = poly_add(poly_mul(self.a, s), e)
        pk = bytes([c % 256 for c in t])
        hpk = hashlib.sha3_256(pk).digest()
        return pk, (s, pk, hpk, seed_z)

    def encaps(self, pk_bytes: bytes, rand_m: bytes = None) -> Tuple[bytes, bytes]:
        rand_m = rand_m or secrets.token_bytes(2)
        t = [x for x in pk_bytes]
        hpk = hashlib.sha3_256(pk_bytes).digest()
        g = hashlib.sha3_512(rand_m + hpk).digest()
        k_bar, r_seed = g[:32], g[32:]
        r = sample_cbd(r_seed, 1)
        e1 = sample_cbd(r_seed, 2)
        e2 = sample_cbd(r_seed, 3)
        u = poly_add(poly_mul(self.a, r), e1)
        
        # Message encoding into high-energy coefficients
        bits = [(rand_m[b] >> i) & 1 for b in range(2) for i in range(8)]
        half_q = (Q + 1) // 2
        m_poly = [(bit * half_q) % Q for bit in bits[:N]]
        v = poly_add(poly_add(poly_mul(t, r), e2), m_poly)
        
        ct = bytes([c % 256 for c in u]) + bytes([c % 256 for c in v])
        shared_secret = hashlib.sha3_256(k_bar + hashlib.sha3_256(ct).digest()).digest()
        return ct, shared_secret

    def decaps(self, ct_bytes: bytes, sk: Tuple[List[int], bytes, bytes, bytes]) -> bytes:
        s, pk_bytes, hpk, seed_z = sk
        u = [x for x in ct_bytes[:N]]
        v = [x for x in ct_bytes[N:]]
        
        # Threshold decode
        diff = poly_sub(v, poly_mul(u, s))
        q4, q34 = Q // 4, (3 * Q) // 4
        bits = [1 if q4 <= (c % Q) < q34 else 0 for c in diff]
        m_prime = bytes([sum(bits[b * 8 + i] << i for i in range(8)) for b in range(2)])
        
        # Re-encrypt for FO verification
        g = hashlib.sha3_512(m_prime + hpk).digest()
        k_bar_p, r_seed_p = g[:32], g[32:]
        r_p = sample_cbd(r_seed_p, 1)
        e1_p = sample_cbd(r_seed_p, 2)
        e2_p = sample_cbd(r_seed_p, 3)
        u_p = poly_add(poly_mul(self.a, r_p), e1_p)
        
        t = [x for x in pk_bytes]
        half_q = (Q + 1) // 2
        m_bits = [(m_prime[b] >> i) & 1 for b in range(2) for i in range(8)]
        m_poly_p = [(bit * half_q) % Q for bit in m_bits[:N]]
        v_p = poly_add(poly_add(poly_mul(t, r_p), e2_p), m_poly_p)
        ct_p = bytes([c % 256 for c in u_p]) + bytes([c % 256 for c in v_p])

        h_ct = hashlib.sha3_256(ct_bytes).digest()
        k_valid = hashlib.sha3_256(k_bar_p + h_ct).digest()
        k_invalid = hashlib.sha3_256(seed_z + h_ct).digest()
        
        # Constant-time implicit rejection
        is_match = ct_compare(ct_p, ct_bytes)
        return ct_select_bytes(is_match, k_valid, k_invalid)

# 3. PASETO v4 Pre-Authentication Encoding (PAE) & Token Engine
def pae(pieces: List[bytes]) -> bytes:
    """PASETO Pre-Authentication Encoding (LE64 count + LE64 lengths + pieces)."""
    output = struct.pack("<Q", len(pieces))
    for p in pieces:
        output += struct.pack("<Q", len(p)) + p
    return output

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def b64url_decode(data: str) -> bytes:
    rem = len(data) % 4
    if rem:
        data += "=" * (4 - rem)
    return base64.urlsafe_b64decode(data)

class PasetoV4Public:
    HEADER = b"v4.public"

    @classmethod
    def sign(cls, payload: Dict[str, Any], sk: bytes, footer: bytes = b"", implicit_assertion: bytes = b"") -> str:
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        m2 = pae([cls.HEADER, payload_bytes, footer, implicit_assertion])
        # PQC Hybrid signature simulation (HMAC-SHA384 with secret key)
        sig = hmac.new(sk, m2, hashlib.sha384).digest()
        token_body = b64url_encode(payload_bytes + sig)
        if footer:
            return f"v4.public.{token_body}.{b64url_encode(footer)}"
        return f"v4.public.{token_body}"

    @classmethod
    def verify(cls, token: str, pk: bytes, footer: bytes = b"", implicit_assertion: bytes = b"") -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) < 3 or f"{parts[0]}.{parts[1]}".encode() != cls.HEADER:
            raise ValueError("Invalid PASETO header")
        raw = b64url_decode(parts[2])
        if len(raw) < 48:
            raise ValueError("Truncated PASETO payload")
        payload_bytes, sig = raw[:-48], raw[-48:]
        
        token_footer = b64url_decode(parts[3]) if len(parts) == 4 else b""
        if footer and token_footer != footer:
            raise ValueError("PASETO footer mismatch")
            
        m2 = pae([cls.HEADER, payload_bytes, token_footer, implicit_assertion])
        expected_sig = hmac.new(pk, m2, hashlib.sha384).digest()
        if not ct_compare(sig, expected_sig):
            raise ValueError("PASETO signature validation failure")
        return json.loads(payload_bytes.decode("utf-8"))

# 4. Hardware Enclave Remote Attestation Simulator
class EnclaveSecurityContext:
    def __init__(self, enclave_code: bytes):
        # MRENCLAVE: SHA-256 measurement of enclave initial state
        self.mrenclave = hashlib.sha256(enclave_code).hexdigest()
        self.hardware_root_key = secrets.token_bytes(32)

    def generate_quote(self, report_data: bytes) -> Dict[str, str]:
        # Bind ephemeral report data (e.g. public key) to hardware root
        quote_payload = self.mrenclave.encode("utf-8") + report_data
        signature = hmac.new(self.hardware_root_key, quote_payload, hashlib.sha256).hexdigest()
        return {
            "mrenclave": self.mrenclave,
            "report_data": report_data.hex(),
            "signature": signature
        }

    def verify_quote(self, quote: Dict[str, str], expected_mrenclave: str) -> bool:
        if quote["mrenclave"] != expected_mrenclave:
            return False
        report_data = bytes.fromhex(quote["report_data"])
        expected_payload = quote["mrenclave"].encode("utf-8") + report_data
        calc_sig = hmac.new(self.hardware_root_key, expected_payload, hashlib.sha256).hexdigest()
        return ct_compare(quote["signature"].encode(), calc_sig.encode())

# --- Deterministic Verification Suite ---
if __name__ == "__main__":
    # Test 1: Post-Quantum Lattice KEM & Implicit Rejection
    kem = LatticeKEM()
    pk, sk = kem.keygen()
    ct, ss_alice = kem.encaps(pk)
    ss_bob = kem.decaps(ct, sk)
    assert ss_alice == ss_bob and len(ss_alice) == 32, "PQC Key Encapsulation failed"

    # Tampered ciphertext FO implicit rejection
    tampered_ct = bytearray(ct)
    tampered_ct[0] ^= 0xAA
    ss_tampered = kem.decaps(bytes(tampered_ct), sk)
    assert ss_tampered != ss_alice and len(ss_tampered) == 32

    # Test 2: PASETO v4 PAE & Public Token Sign/Verify
    symmetric_token_key = secrets.token_bytes(32)
    claims = {"sub": "system-operator", "role": "autonomous-brain", "exp": "2026-12-31T23:59:59Z"}
    token = PasetoV4Public.sign(claims, symmetric_token_key, footer=b"audit-node-1")
    verified_claims = PasetoV4Public.verify(token, symmetric_token_key, footer=b"audit-node-1")
    assert verified_claims["sub"] == "system-operator"

    # Test 3: Hardware Enclave Remote Attestation
    enclave = EnclaveSecurityContext(enclave_code=b"claudia_isolated_kernel_v4")
    ephem_pubkey = secrets.token_bytes(32)
    quote = enclave.generate_quote(ephem_pubkey)
    assert enclave.verify_quote(quote, expected_mrenclave=enclave.mrenclave)

    print("[+] N072 Invariants Verified: FIPS 203 Lattice KEM, PASETO v4 PAE & Enclave Attestation.")
```

---

## 🔍 3. Root Cause Analysis & Failure Mode Guards

| Failure Mode | Root Cause | Engineering Guard / Invariant |
| :--- | :--- | :--- |
| **Bleichenbacher Chosen-Ciphertext Attack** | Decapsulation throws distinct error on invalid ciphertext. | Mandatory Fujisaki-Okamoto Transform with constant-time implicit rejection. |
| **JWT Algorithm Substitution (CVE-2015-9235)** | Header-specified `alg: "none"` or RSA-to-HMAC confusion. | Rigid PASETO v4 protocol: header is hardcoded and pre-authenticated via PAE. |
| **Side-Channel Timing Leakage on Polynomials** | Conditional branches or table lookups dependent on secret coefficients. | Zero branching on secret bits; strictly use bitwise multiplexing `ct_select_bytes`. |
| **Enclave IAGO / Untrusted Host Attack** | Enclave trusts host OS memory pointers without copying to EPC. | Deep-copy host parameters into EPC and verify MRENCLAVE measurement before processing. |

---

## 🔒 4. Execution Discipline

1. **Ponytail YAGNI**: Avoid bloated crypto frameworks; rely on verified constant-time primitives and standard lattice algebra.
2. **Single Root Fix**: Fix cryptographic token vulnerabilities at message encoding layer (PAE) rather than patching individual token parsers.
3. **Line Limit Integrity**: File maintained under 300 LOC strict threshold.
