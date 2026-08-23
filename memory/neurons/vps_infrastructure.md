# Neuron Memory: VPS Infrastructure & Services

- **Host Node**: Primary Cloud VPS (`<VPS_HOST>`, Ubuntu 24.04 LTS).
- **User**: ubuntu.
- **Database Standard**: SQLite3 (etter-sqlite3) + WAL mode (PRAGMA journal_mode = WAL;).
- **Active PM2 Services**:
  - zolu-main: Port 3000 (zolu.my.id - Ecosystem Portal Hub)
  - zolu-monitor: Port 3001 (monitoring.zolu.my.id - System Telemetry)
  - zolu-user: Port 3003 (user.zolu.my.id - Telegram Tenant & Hermes Isolation Manager)
  - zolu-mojoloker: Port 3011 (mojoloker.my.id - Portal Loker Mojokerto)
  - zolu-prod: Port 3012 (prod.zolu.my.id - AI Fullstack Web Production Generator)
  - zolu-kas: Port 3030 (kas.zolu.my.id - Kasir & Financial OS)
  - zolu-skripsi: Port 3050 (skripsi.zolu.my.id - Academic Skripsi Generator)
  - 9router: Port 3040 / 20128 (AI Multi-Model Gateway)
  - antigravity-bridge: Port 8000 (OpenAI-compatible AI Bridge)
- **Hermes Agent (Telegram & Multi-tenant)**:
  - Global Persona: "Claudia" developed by Gahar Inovasi Teknologi.
  - Model: `ag/gemini-3.7-flash-high` via 9Router Gateway (`https://9router.zolu.my.id/v1`).
  - Telegram Tenant Isolation: Dynamic SQLite WAL auth in adapter with 3-day auto-trial for new users, isolated per-user sessions, and sync with `zolu-user`.
  - UI & Date Format: DD/MM/YYYY formatting, eye show/hide for Telegram IDs, 10-item pagination, and extension modals active across all 7 ecosystem web apps.

