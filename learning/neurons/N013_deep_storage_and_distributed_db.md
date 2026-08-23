# Neuron N013: Deep Storage Internals, LSM-Trees & Distributed Databases

Prinsip rancang bangun mesin penyimpanan data dan basis data berskala raksasa:

---

## 1. Storage Engine Internals: LSM-Tree vs B+ Tree
- **LSM-Tree (Log-Structured Merge-Tree)**: Append-only MemTable di RAM -> Flush ke SSTable di disk -> Background Compaction (Leveled vs Size-Tiered). Pilihan utama untuk beban *Write-Intensive* (RocksDB, Cassandra).
- **B+ Tree**: Struktur seimbang untuk pencarian sekuensial dan *Read-Intensive* dengan locking halaman disk (SQLite, PostgreSQL).
- **WAL (Write-Ahead Logging) & Checkpointing**: Menjamin durabilitas ACID pada kegagalan mendadak.

---

## 2. Distributed Transactions & Vector Indexing
- **Two-Phase Commit (2PC) & Saga Pattern**: Orkestrasi transaksi lintas microservices dengan mekanisme kompensasi otomatis saat gagal.
- **MVCC (Multi-Version Concurrency Control)**: Pembaca tidak pernah memblokir penulis (*non-blocking reads*).
- **HNSW (Hierarchical Navigable Small World)**: Graf multi-lapisan untuk pencarian kemiripan vektor (*Approximate Nearest Neighbor*) dalam $O(\log N)$.
