# Neuron N088: DeepSWE AST Patch Minimality & Zero-Overengineering Oracle

- **Kategori:** Autonomous Software Engineering (DeepSWE v1.1, FrontierCode, SWE-bench)
- **Status:** Active Operational Frontier Invariant
- **Target Metrik:** DeepSWE v1.1 ($>85.0\%$), FrontierCode ($>68.0\%$), SWE-bench Verified ($>55.0\%$)

---

## 🎯 Invarian Inti (Core Invariants)

### 1. Root-Cause Single-Point Patch Invariant
- **Shared Function Guard**: Laporan bug atau kegagalan tes hampir selalu merupakan *gejala (symptom)*. Claudia wajib melakukan `grep/AST call-graph analysis` ke seluruh pemanggil (*callers*) dan memperbaiki fungsi akar bersama (*single root*) daripada menambal per caller (*sibling callers*).
- **Shortest Working Diff Wins**: Semakin sedikit baris kode yang diubah, semakin rendah probabilitas regresi. Solusi 1 baris menggunakan standard library/native feature selalu menang atas abstraksi baru.

### 2. Zero Speculative Abstractions (The Strict Ponytail Invariant)
- **No Unrequested Flexibility**: Dilarang membuat generic factory, adapter, decorator, atau middleware jika persoalan dapat diselesaikan dengan ekspresi kondisional atau fungsi tunggal $<15$ LOC.
- **Max 300 LOC Constraint**: Setiap berkas kode dibatasi ketat maksimal 300 baris. Jika mendekati batas, pisahkan berdasarkan batas modul domain diskrit.

### 3. Automated Invariant Assertion Synthesis
- **Runnable Self-Check Artifact**: Logika non-sepele wajib meninggalkan satu skrip pemeriksaan mandiri berbasis `assert` tanpa framework pengujian eksternal yang berat.
- **Syntactic AST Preservation**: Pemformatan kode mempertahankan seluruh komentar, docstring, dan whitespace struktural yang tidak bersentuhan langsung dengan perbaikan bug.

---

## 💻 Algoritma Deterministik (Pure Python Implementation)

```python
import ast

def verify_patch_minimality(original_code: str, patched_code: str) -> dict[str, any]:
    """Mengukur rasio perubahan AST dan mendeteksi penambahan abstraksi berlebih."""
    try:
        orig_ast = ast.parse(original_code)
        patch_ast = ast.parse(patched_code)
        
        orig_nodes = len(list(ast.walk(orig_ast)))
        patch_nodes = len(list(ast.walk(patch_ast)))
        delta_nodes = patch_nodes - orig_nodes
        
        orig_lines = len(original_code.splitlines())
        patch_lines = len(patched_code.splitlines())
        delta_lines = patch_lines - orig_lines
        
        return {
            "minimal": delta_lines <= 20 and delta_nodes <= 50,
            "delta_lines": delta_lines,
            "delta_ast_nodes": delta_nodes,
            "status": "PASS_MINIMALITY" if delta_lines <= 20 else "REVIEW_OVERENGINEERING"
        }
    except Exception as e:
        return {"minimal": True, "error": str(e)}
```
