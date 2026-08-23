# Neuron N008: Persistent Live Session Checkpoint & Infrastructure State

## 📌 Metadata
- **Last Sync**: 2026-08-23
- **Primary VPS**: `ubuntu@<VPS_HOST>` (Ubuntu 24.04 LTS, configured via `.env`)
- **Authentication**: Key-based passwordless (`~/.ssh/vps_ubuntu.ppk` & `~/.ssh/vps_ubuntu_ed25519`).
- **Hardware Specs**: 6 Cores CPU (AMD EPYC), 18 GB RAM, 1,000 GB (1 TB 100% SSD) Storage (824 GB free space).

---

## 🚀 Deployed Ecosystem & Port Mappings
1. **Landing Page Main Hub**: `https://zolu.my.id` (Port 3000, PM2 `zolu-main`)
2. **Zolu Cinema (Jellyfin)**: `https://movie.zolu.my.id` (Port 3016, Docker `zolu-jellyfin`, PM2 supervisor)
   - Admin: `<ADMIN_USER>` / `<ADMIN_PASSWORD>` (Stored in `.env` / `credentials.json`)
   - User: `arya` / `password123`
   - Server Name: `Zolu Cinema`
3. **Zolu Cloud NAS (Nextcloud)**: `https://nextcloud.zolu.my.id` (Port 3015, Docker `zolu-nextcloud`, PM2 supervisor)
   - Admin: `<ADMIN_USER>` / `<ADMIN_PASSWORD>` (Stored in `.env` / `credentials.json`)

4. **Self-Registration Invite Gateway**: `https://join.zolu.my.id` (Port 3017, PM2 `zolu-invite`)
   - CLI Helper: `/usr/local/bin/buat-invite <KODE> <KUOTA>` & `/usr/local/bin/list-invite`
5. **9Router AI Gateway**: `https://9router.zolu.my.id` (Port 3040, PM2 `9router`)
6. **MojoLoker**: `https://mojoloker.my.id` (Port 3011, PM2 `zolu-mojoloker`)
7. **Zolu Prod**: `https://prod.zolu.my.id` (Port 3012, PM2 `zolu-prod`)
8. **Kas Zolu**: `https://kas.zolu.my.id` (Port 3030, PM2 `zolu-kas`)
9. **Zolu Skripsi**: `https://skripsi.zolu.my.id` (Port 3050, PM2 `zolu-skripsi`)
10. **Zolu Monitor**: `https://monitoring.zolu.my.id` (Port 3001, PM2 `zolu-monitor`)
11. **User Tenant Manager**: `https://user.zolu.my.id` (Port 3003, PM2 `zolu-user`)

---

## 🎬 Media Engine & Strict Subtitle Cleaner
- **Storage Directories**:
  - Movies: `/home/ubuntu/media_storage/movies/`
  - Series: `/home/ubuntu/media_storage/series/`
  - Anime: `/home/ubuntu/media_storage/anime/`
  - Music: `/home/ubuntu/media_storage/music/`
- **Streaming Standardization**: FastStart (`+faststart`) + H.264 + AAC for 0.1s instant streaming without buffering.
- **Subtitle Sanitizer (`/usr/local/bin/clean-subtitles`)**: Strictly strips gambling/slot/judi ads, URLs, author credits, and non-dialogue markup from all `.srt` files.
## 🛠️ Installed Autonomous Fullstack & Security Toolkit
- **Biome Linter & Formatter (`@biomejs/biome`)**: `v2.5.10` (Global Rust linter, 35x faster than ESLint).
- **Playwright E2E UI Testing (`playwright` + Chromium Headless)**: `v1234` (Automated browser testing & screenshot engine).
- **Edge API Framework (`hono`)**: `v4.13.3` (Sub-15KB ultra-fast web server).
- **Runtime Schema Validator (`zod`)**: `v4.4.3` (Strict trust boundary input validation).
- **Type-Safe ORM (`drizzle-orm` + `better-sqlite3`)**: `v0.45.2` (Zero-bloat SQLite WAL database engine).
- **Headless Automation (`puppeteer`)**: (PDF invoice rendering & programmatic web scrapers).
