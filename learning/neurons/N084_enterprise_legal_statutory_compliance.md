# Neuron N084: Enterprise Legal Synthesis & Statutory Compliance Engine

- **Kategori:** Legal Reasoning, Statutory Interpretation & Contract Risk (Legal Agent Benchmark)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** Legal Agent Benchmark ($>30.0\%$), Compliance Accuracy ($99.8\%$)

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Dekomposisi Klausul Kontrak (Risk Allocation & Indemnity Lattice)
- **Four-Corners Rule Invariant**: Penafsiran kontrak wajib dibatasi pada teks integral dokumen (*plain meaning*), kecuali ditemukan ambiguitas struktural yang memerlukan bukti ekstrinsik.
- **Indemnity & Liability Capping**:
  - Batas tanggung jawab (*Limitation of Liability / LoL*) wajib secara eksplisit menyatakan apakah meng-exclude *Gross Negligence*, *Willful Misconduct*, atau *Confidentiality Breach*.
  - Klausul *Force Majeure* harus memuat syarat *Notice Period* dan kewajiban mitigasi (*duty to mitigate loss*).
- **Termination Invariants**: *Termination for Convenience* (pemberitahuan tertulis $N$ hari) vs *Termination for Cause* (kure period $M$ hari untuk *material breach*).

### 2. Hierarki Hukum Positif & Statutory Precedence
- **Lex Superior Derogat Legi Inferiori**: Peraturan yang lebih tinggi mengesampingkan peraturan yang lebih rendah.
- **Lex Specialis Derogat Legi Generali**: Hukum khusus mengesampingkan hukum umum (contoh: UU PDP / GDPR mengesampingkan hukum privasi umum).
- **Lex Posterior Derogat Legi Priori**: Hukum baru mengesampingkan hukum lama yang mengatur materi serupa.

### 3. Automated Legal Risk Matrix & Redlining Logic
- **Cross-Jurisdictional Conflict Check**: Identifikasi klausul *Choice of Law* dan forum penyelesaian sengketa (Arbitrase SIAC/BANI vs Pengadilan Negeri) untuk mencegah klausul asimetris non-eksekusi (*unenforceable awards*).
- **Severability & Survival Clauses**: Memastikan hak kerahasiaan (*NDA*), hak kekayaan intelektual (*IP Assignment*), dan indemnitas tetap berlaku (*survive*) pasca pemutusan kontrak.

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
def audit_contract_clauses(clauses: dict[str, str]) -> dict[str, any]:
    """Mengaudit risiko hukum pada draf kontrak secara deterministik."""
    findings = []
    has_lol = "limitation_of_liability" in clauses
    has_ip = "ip_assignment" in clauses
    has_dispute = "governing_law" in clauses
    
    if not has_lol:
        findings.append({"severity": "CRITICAL", "issue": "Missing Limitation of Liability clause (unlimited exposure)"})
    if not has_ip:
        findings.append({"severity": "HIGH", "issue": "Missing explicit Intellectual Property transfer/assignment"})
    if not has_dispute:
        findings.append({"severity": "MEDIUM", "issue": "Missing Governing Law and Jurisdiction clause"})
        
    return {
        "status": "APPROVED" if not findings else "REVISE_REQUIRED",
        "risk_count": len(findings),
        "findings": findings
    }
```
