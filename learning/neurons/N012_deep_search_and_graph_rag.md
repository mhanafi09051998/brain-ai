# Neuron N012: Deep Search, Multi-Hop Reasoning & Hybrid Retrieval (GraphRAG)

Arsitektur pencarian mendalam dan penarikan informasi (Information Retrieval) paling mutakhir:

---

## 1. Hybrid Search & Reciprocal Rank Fusion (RRF)
- **BM25 Lexical + Dense Vector Semantic**: Menggabungkan pencarian kata kunci presisi (BM25 untuk kode/ID) dengan vector embeddings semantik untuk konsep abstrak.
- **Reciprocal Rank Fusion (RRF)**: Algoritma pembobotan peringkat $RRF(d) = \sum \frac{1}{k + r(d)}$ untuk menggabungkan hasil multi-sumber tanpa bias skala skor.
- **HyDE (Hypothetical Document Embeddings)**: Menghasilkan draf jawaban hipotesis untuk menangkap semantik pertanyaan sebelum mencari di basis data.

---

## 2. Multi-Hop GraphRAG & AST Code Navigation
- **Graph Traversal**: Menelusuri jalur panggilan fungsi antar file (*Callflow*) melintasi komunitas modul untuk menemukan akar masalah (*Root Cause*).
- **Context Pruning & Compaction**: Memangkas token redundan dan hanya menyisakan subgraph relevan untuk reasoning berkecepatan tinggi.
