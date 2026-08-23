# Self-Learning Framework

Direktori ini berfungsi sebagai sistem penyimpanan dan evolusi pengetahuan mandiri (self-learning) untuk Claudia.

## Struktur Folder

```text
learning/
├── knowledge_base/   # Dokumentasi konsep, arsitektur, dan insight domain
├── feedback_log/      # Log evaluasi, perbaikan bug, dan preferensi yang dipelajari
├── playbooks/         # SOP, runbook, dan resep kerja yang terbukti efektif
└── reflections/       # Refleksi periodik & agregasi memori (sinkron dengan Graphify)
```

## Alur Pembelajaran
1. **Observe & Execute**: Menjalankan task dengan prinsip Ponytail (minimalis) dan Graphify (pemetaan relasi).
2. **Capture**: Menyimpan feedback atau pola baru di `feedback_log/`.
3. **Synthesize**: Mengekstrak pola berulang ke `playbooks/` atau `knowledge_base/`.
4. **Reflect**: Menggunakan `python -m graphify reflect` untuk mengagregasi sinyal keberhasilan/kegagalan.
