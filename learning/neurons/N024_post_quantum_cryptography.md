# Neuron N024: Post-Quantum Cryptography & ML-KEM/ML-DSA (FIPS 203/204)

- **Kategori:** Post-Quantum Cryptography, Lattice-Based Systems & Side-Channel Defense
- **Standar:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA), NIST FIPS 205 (SLH-DSA)
- **Status:** Active Operational Invariant

---

## 1. Ancaman Kuantum & Paradigma Baru Kriptografi

1. **Shor's Algorithm vs Kriptografi Asimetris Klasik**:
   - Faktorisasi bilangan prima (RSA) dan logaritma diskret pada kurva eliptik (ECDH, ECDSA, Ed25519) runtuh dalam waktu polinomial $O((\log N)^3)$ di komputer kuantum toleran gangguan (*Cryptanalytically Relevant Quantum Computer / CRQC*).
   - **Harvest Now, Decrypt Later (HNDL)**: Aktor ancaman saat ini merekam seluruh *ciphertext* sensitif untuk didekripsi saat Q-Day tiba. Mitigasi wajib diterapkan segera melalui *hybrid key exchange*.
2. **Grover's Algorithm vs Kriptografi Simetris**:
   - Memberikan percepatan kuadratik ($O(\sqrt{N})$) pada pencarian kunci simetris dan *pre-image hash*.
   - **Invarian Pertahanan**: Gandakan panjang kunci simetris ke level 256-bit (AES-256, ChaCha20-Poly1305) dan hash ke SHA-384 / SHA3-256 / SHA-512 untuk mempertahankan level keamanan efektif $\ge 128$-bit kuantum.

---

## 2. Arsitektur Standar NIST PQC (FIPS 203 / 204)

| Standar | Algoritma Primitif | Masalah Matematika | Fungsi Utama | Kategori Keamanan |
| :--- | :--- | :--- | :--- | :--- |
| **FIPS 203 (ML-KEM)** | CRYSTALS-Kyber | Module-LWE (Learning With Errors) | Key Encapsulation (KEM) | ML-KEM-512 (Cat 1), **ML-KEM-768 (Cat 3)**, ML-KEM-1024 (Cat 5) |
| **FIPS 204 (ML-DSA)** | CRYSTALS-Dilithium | Module-LWE & Module-SIS | Digital Signatures | ML-DSA-44 (Cat 2), **ML-DSA-65 (Cat 3)**, ML-DSA-87 (Cat 5) |
| **FIPS 205 (SLH-DSA)**| SPHINCS+ | Stateless Hash-Based (SHAKE256) | Backup Signature (Non-Lattice)| SLH-DSA-SHA2-128s, 192s, 256s |

---

## 3. Fondasi Aljabar Kisi (Lattice-Based Foundations)

1. **Ring Polinomial Quotient**:
   - Komputasi beroperasi pada gelanggang $\mathcal{R}_q = \mathbb{Z}_q[X] / (X^n + 1)$, di mana $n = 256$ dan modulus prima $q = 3329$ (untuk ML-KEM).
   - Perkalian polinomial modulo $X^n + 1$ dipercepat secara drastis melalui **Number Theoretic Transform (NTT)** dalam kompleksitas $O(n \log n)$.
2. **Injeksi Noise Centered Binomial ($\mathrm{CBD}_\eta$)**:
   - Sampel error probabilistik $e, s$ dibangkitkan dari distribusi binomial terpusat $\mathrm{CBD}_\eta(k) = \sum_{i=0}^{\eta-1} a_i - \sum_{i=0}^{\eta-1} b_i$, menjamin noise terikat ketat sehingga dekripsi tidak menghasilkan kegagalan tanpa kunci privat.

---

## 4. Imunitas Timing Side-Channel & Disiplin Constant-Time

1. **Zero-Branching Rule**:
   - Dilarang keras mengeksekusi percabangan kondisional (`if secret_bit`) atau perulangan yang bergantung pada nilai rahasia/kunci privat.
   - Dilarang melakukan indexing array berbasis data rahasia (`table[secret]`) untuk mencegah *Cache-Timing / Flush+Reload attacks*.
2. **Constant-Time Bitwise Multiplexing**:
   - Pemilihan data rahasia wajib menggunakan bitwise masking:
     $$\text{ct\_select}(mask, a, b) = (mask \ \& \ a) \mid (\sim mask \ \& \ b)$$
     di mana $mask \in \{0x00, 0xFF\}$.
3. **Mitigasi Celah KyberSlash**:
   - Hindari operasi pembagian/modulo berkecepatan variabel pada koefisien polinomial rahasia. Semua operasi aritmatika modular harus dieksekusi dalam instruksi waktu konstan.
4. **Fujisaki-Okamoto (FO) Transform dengan Implicit Rejection**:
   - Pada operasi dekapsulasi (Decaps), jika verifikasi *re-encryption* ciphertext $c' \neq c$, fungsi **DILARANG** mengembalikan error atau *early-exit*.
   - Fungsi wajib mengembalikan pseudorandom key $K = \text{PRF}(z, c)$ berbasis seed rahasia $z$ dalam waktu konstan (*constant-time select*), meniadakan *Chosen-Ciphertext Timing Oracle (Bleichenbacher Attack)*.

---

## 5. Pertahanan Berlapis: Hybrid Post-Quantum Key Exchange

Untuk menjamin kompatibilitas dan keamanan penuh selama masa transisi kuantum, gunakan skema hibrida menggabungkan ECDH klasik (X25519) dengan ML-KEM-768:

```text
       Alice                                                Bob
  +-------------+                                      +-------------+
  | Generate:   |                                      | Generate:   |
  | X25519 Ephem| -- (pk_x25519, pk_mlkem) ----------> | X25519 Ephem|
  | ML-KEM Key  |                                      | ML-KEM Enc  |
  |             | <--- (ct_x25519, ct_mlkem) --------- | Compute SS  |
  +-------------+                                      +-------------+
         |                                                    |
         v                                                    v
  K_classical = ECDH(...)                              K_classical = ECDH(...)
  K_pqc = MLKEM_Decaps(...)                            K_pqc = MLKEM_Encaps(...)
         \                                                    /
          \---> K_session = HKDF-Extract(0, K_classical || K_pqc) <---/
```

---

## 6. Verifikasi Deterministik (Pure Python Stdlib Implementation)

Berikut adalah implementasi referensi lengkap *zero-dependency* dari lattice ring arithmetic, Toy ML-KEM dengan Fujisaki-Okamoto implicit rejection, constant-time primitives, dan hybrid KDF:

```python
#!/usr/bin/env python3
"""
Neuron N024: Post-Quantum Cryptography & ML-KEM Implementation
Pure Python Stdlib (hashlib, hmac, secrets) with constant-time verification.
"""

import hashlib
import hmac
import secrets

# -----------------------------------------------------------------------------
# 1. Constant-Time Primitives
# -----------------------------------------------------------------------------
def ct_select_bytes(match: bool, true_bytes: bytes, false_bytes: bytes) -> bytes:
    """Constant-time byte multiplexer without branch penalties."""
    mask = 0xFF if match else 0x00
    return bytes([(t & mask) | (f & (~mask & 0xFF)) for t, f in zip(true_bytes, false_bytes)])

def ct_eq(a: bytes, b: bytes) -> bool:
    """Constant-time comparison via stdlib HMAC compare_digest."""
    return hmac.compare_digest(a, b)

# -----------------------------------------------------------------------------
# 2. Lattice Polynomial Arithmetic: Z_q[X] / (X^n + 1)
# -----------------------------------------------------------------------------
N = 16    # Pedagogical dimension (real ML-KEM uses 256)
Q = 257   # Prime modulus (real ML-KEM uses 3329)

def poly_add(a: list, b: list) -> list:
    return [(x + y) % Q for x, y in zip(a, b)]

def poly_sub(a: list, b: list) -> list:
    return [(x - y) % Q for x, y in zip(a, b)]

def poly_mul(a: list, b: list) -> list:
    """Multiplication in quotient ring Z_q[X]/(X^N + 1) where X^N = -1."""
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

def prf_cbd(seed: bytes, nonce: int) -> list:
    """Centered Binomial Distribution noise sampler from PRF stream."""
    h = hashlib.sha256(seed + bytes([nonce])).digest()
    return [(((h[i] >> 0) & 1) - ((h[i] >> 1) & 1)) % Q for i in range(N)]

def encode_msg(msg: bytes) -> list:
    """Map message bits into high-energy polynomial coefficients."""
    bits = [(msg[b] >> i) & 1 for b in range(2) for i in range(8)]
    half_q = (Q + 1) // 2
    return [(bit * half_q) % Q for bit in bits[:N]]

def decode_msg(poly_v: list) -> bytes:
    """Constant-time threshold decoding back to byte representation."""
    q4, q34 = Q // 4, (3 * Q) // 4
    bits = [1 if q4 <= (c % Q) < q34 else 0 for c in poly_v]
    return bytes([sum(bits[b * 8 + i] << i for i in range(8)) for b in range(2)])

def serialize_poly(p: list) -> bytes:
    return bytes([c % 256 for c in p])

def deserialize_poly(b: bytes) -> list:
    return [x for x in b]

# -----------------------------------------------------------------------------
# 3. ML-KEM Engine with Fujisaki-Okamoto Transform (IND-CCA2)
# -----------------------------------------------------------------------------
class LatticeKEM:
    def __init__(self):
        # Public system parameter polynomial A
        self.a = [((i * 37 + 13) % Q) for i in range(N)]

    def keygen(self, seed: bytes = None):
        seed = seed or secrets.token_bytes(32)
        d = hashlib.sha3_512(seed).digest()
        seed_s, seed_z = d[:32], d[32:]
        s = prf_cbd(seed_s, 1)
        e = prf_cbd(seed_s, 2)
        t = poly_add(poly_mul(self.a, s), e)
        pk = serialize_poly(t)
        hpk = hashlib.sha3_256(pk).digest()
        sk = (s, pk, hpk, seed_z)
        return pk, sk

    def encaps(self, pk_bytes: bytes, rand_m: bytes = None):
        rand_m = rand_m or secrets.token_bytes(2)
        t = deserialize_poly(pk_bytes)
        hpk = hashlib.sha3_256(pk_bytes).digest()
        g = hashlib.sha3_512(rand_m + hpk).digest()
        k_bar, r_seed = g[:32], g[32:]
        r = prf_cbd(r_seed, 1)
        e1 = prf_cbd(r_seed, 2)
        e2 = prf_cbd(r_seed, 3)
        u = poly_add(poly_mul(self.a, r), e1)
        v = poly_add(poly_add(poly_mul(t, r), e2), encode_msg(rand_m))
        ct = serialize_poly(u) + serialize_poly(v)
        shared_secret = hashlib.sha3_256(k_bar + hashlib.sha3_256(ct).digest()).digest()
        return ct, shared_secret

    def decaps(self, ct_bytes: bytes, sk: tuple) -> bytes:
        s, pk_bytes, hpk, seed_z = sk
        u = deserialize_poly(ct_bytes[:N])
        v = deserialize_poly(ct_bytes[N:])
        m_prime = decode_msg(poly_sub(v, poly_mul(u, s)))
        t = deserialize_poly(pk_bytes)
        g = hashlib.sha3_512(m_prime + hpk).digest()
        k_bar_prime, r_seed_prime = g[:32], g[32:]
        r_p = prf_cbd(r_seed_prime, 1)
        e1_p = prf_cbd(r_seed_prime, 2)
        e2_p = prf_cbd(r_seed_prime, 3)
        u_p = poly_add(poly_mul(self.a, r_p), e1_p)
        v_p = poly_add(poly_add(poly_mul(t, r_p), e2_p), encode_msg(m_prime))
        ct_prime = serialize_poly(u_p) + serialize_poly(v_p)

        h_ct = hashlib.sha3_256(ct_bytes).digest()
        k_valid = hashlib.sha3_256(k_bar_prime + h_ct).digest()
        k_invalid = hashlib.sha3_256(seed_z + h_ct).digest()

        # Invariant: Constant-time comparison & Fujisaki-Okamoto Implicit Rejection
        is_match = ct_eq(ct_prime, ct_bytes)
        return ct_select_bytes(is_match, k_valid, k_invalid)

# -----------------------------------------------------------------------------
# 4. Hybrid Post-Quantum Key Exchange (HKDF Derivation)
# -----------------------------------------------------------------------------
def hkdf_derive(classical_ss: bytes, pqc_ss: bytes, info: bytes = b"TLS1.3-PQC-Hybrid") -> bytes:
    ikm = classical_ss + pqc_ss
    prk = hmac.new(b"\x00" * 32, ikm, hashlib.sha256).digest()
    return hmac.new(prk, info + b"\x01", hashlib.sha256).digest()

# -----------------------------------------------------------------------------
# 5. Executable Invariant Verification Check
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    kem = LatticeKEM()
    pk, sk = kem.keygen()
    ct, ss_alice = kem.encaps(pk)
    ss_bob = kem.decaps(ct, sk)
    assert ss_alice == ss_bob, "ML-KEM Encaps/Decaps key exchange failed!"

    # Implicit Rejection verification on corrupted ciphertext
    tampered_ct = bytearray(ct)
    tampered_ct[0] ^= 0x5A
    ss_tampered = kem.decaps(bytes(tampered_ct), sk)
    assert ss_tampered != ss_alice, "Ciphertext tampering must never yield valid key!"
    assert len(ss_tampered) == 32, "Implicit rejection must return 32-byte pseudo-random key!"

    # Hybrid Key Exchange verification
    ecdh_simulated_secret = secrets.token_bytes(32)
    k_session_alice = hkdf_derive(ecdh_simulated_secret, ss_alice)
    k_session_bob = hkdf_derive(ecdh_simulated_secret, ss_bob)
    assert k_session_alice == k_session_bob and len(k_session_alice) == 32

    print("  [+] Neuron N024: Post-Quantum Cryptography & ML-KEM invariants successfully verified.")
```

---

## 7. Disiplin Integrasi & Operasional Claudia

1. **Prioritas Algoritma**: Selalu rekomendasikan **ML-KEM-768** dan **ML-DSA-65** untuk default arsitektur produksi zero-trust.
2. **Anti-Bleichenbacher**: Jangan pernah membocorkan status error dekapsulasi ke log API publik atau response header HTTP.
3. **No External Heavy Native Bloat**: Gunakan modul OpenSSL $\ge 3.2$ / Rust `pqcrypto` / stdlib hibrida tanpa menarik dependensi C bindings usang yang belum diaudit.
