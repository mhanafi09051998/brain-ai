# Playbook: Graphify Workflow

## Ekstraksi & Refresh Graf

1. **Full Scan**:
   ```bash
   python -m graphify extract .
   ```
2. **Incremental Update** (hanya file yang berubah):
   ```bash
   python -m graphify extract . --update
   ```
3. **Query Relasi**:
   ```bash
   python -m graphify query "pertanyaan arsitektur"
   ```
4. **Agregasi Refleksi**:
   ```bash
   python -m graphify reflect
   ```
