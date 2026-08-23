# Neuron N002: VPS Remote Operations & Pipeline

## Core Concept
Pola eksekusi remote VPS berbasis headless & automated tunneling:
- Remote Host: `ubuntu@<VPS_HOST>` (Ubuntu 24.04 LTS, configured via `.env` / SSH config).
- Transport Tool: `plink.exe` (PuTTY CLI dengan key `~/.ssh/vps_ubuntu.ppk`) & OpenSSH `ssh vps-ubuntu`.
- Otomasi non-interaktif: Key-based authentication tanpa password (`-i ~/.ssh/vps_ubuntu.ppk`).
- Services: PM2 apps (`zolu-main`, `zolu-kas`, `zolu-mojoloker`, `zolu-prod`, `9router`, `zolu-nextcloud` [Port 3015], `zolu-jellyfin` [Port 3016 -> movie.zolu.my.id], `zolu-invite` [Port 3017 -> Invite Self-Register System]).
- Media Storage: `/home/ubuntu/media_storage/{movies,series,anime,music}` (Jellyfin dedicated).
- Media Downloader: `yt-dlp` & `aria2c` installed for automated downloading with Indonesian subtitles.
- Subtitle Sanitizer: `/usr/local/bin/clean-subtitles` strictly purges gambling/slot ads, URLs, author credits, and non-dialogue lines.



- **N006 (9Router Gateway)**: Manajemen routing AI di VPS port 3040 / lokal 20128.
- **N004 (Ponytail Minimality)**: Edit langsung file target via PSCP tanpa instalasi tooling berat di server.
