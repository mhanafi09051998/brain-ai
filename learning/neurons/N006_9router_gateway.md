# Neuron N006: 9Router Gateway Engine

## Core Concept
Arsitektur gateway LLM & Model Router (`9router`):
- Runtime: Next.js standalone server di port 20128 (lokal) / 3040 (VPS).
- Auth & Password: Hash tersimpan di SQLite `data.sqlite` (`settings.data.password` via bcrypt).
- Remote Access: Butuh password non-default atau `INITIAL_PASSWORD` env var sebelum login remote diizinkan.

## Synaptic Links
- **N002 (VPS Remote Ops)**: Terintegrasi dengan proxy dan monitoring PM2.
