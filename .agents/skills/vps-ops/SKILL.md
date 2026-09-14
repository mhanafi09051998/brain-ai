---
name: vps-ops
description: >-
  Standar operasional VPS Linux (Ubuntu) untuk administrasi server: SSH aman,
  PM2 process manager, Nginx reverse proxy, Cloudflare Tunnel, systemd,
  firewall UFW, monitoring, dan deployment aplikasi Node.js/Next.js.
  Aktifkan skill ini ketika pengguna meminta konfigurasi, deployment,
  debugging, atau pemeliharaan VPS (termasuk VPS sol.zolu.my.id).
---

# VPS Operations Skill (Ubuntu + PM2 + Cloudflare)

Skill ini adalah pedoman eksekusi tugas administrasi VPS berbasis Linux
(khususnya Ubuntu) untuk deployment dan pemeliharaan aplikasi produksi,
dengan penekanan pada keamanan, idempotensi, dan verifikasi empiris.

## 1. Prinsip Operasional
- **SSH Non-Interaktif**: Selalu gunakan `ssh -n user@host "command"` di Windows untuk menghindari hang (lihat anti-pola #7 di `memory.md`).
- **Grounding**: Jalankan `pm2 list`, `systemctl status`, atau `df -h` sebelum mengubah apa pun.
- **Backup Sebelum Mutasi**: Salin file konfigurasi (`cp file file.bak-YYYYMMDD`) sebelum edit.
- **Verifikasi Empiris**: Setiap deployment wajib diuji (`curl`, `pm2 logs`, `systemctl status`) sebelum dinyatakan selesai.
- **Minimal Intervention**: Ubah hanya bagian yang diperlukan; hindari restart seluruh server kecuali diperlukan.

## 2. SSH & Akses Aman
```bash
# Nonaktifkan root login & password auth
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl reload sshd

# Verifikasi status
ssh -n ubuntu@sol.zolu.my.id "sudo grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config"
```

## 3. PM2 (Node.js Process Manager)
```bash
# Lihat status semua aplikasi
pm2 list

# Restart spesifik
pm2 restart meridian

# Auto-restart on boot
pm2 startup && pm2 save

# Monitoring log real-time
pm2 logs meridian --lines 50

# Hapus proses
pm2 delete kasir
```

## 4. Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/app
server {
    listen 80;
    server_name app.zolu.my.id;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 5. Cloudflare Tunnel (Zero Trust)
```bash
# Cek status tunnel
systemctl status cloudflared

# Lihat route aktif
cloudflared tunnel ingress validate

# Restart tunnel
systemctl restart cloudflared
```
Aturan penting: jangan pernah hapus ingress route tanpa konfirmasi pengguna — terutama untuk domain produksi aktif.

## 6. Firewall UFW
```bash
sudo ufw status numbered
sudo ufw allow OpenSSH
sudo ufw deny 22/tcp comment "SSH public"  # atau sesuaikan
sudo ufw allow from 103.21.244.0/22 to any port 443 comment "Cloudflare IP range"
```

## 7. Monitoring & Disk Health
```bash
df -h                    # cek ruang disk
free -h                  # cek memori
htop                     # real-time CPU/proc
journalctl -u meridian -n 50 --no-pager
pm2 monit                # dashboard PM2 interaktif
```

## 8. Deployment Standar (Next.js / Node.js)
```bash
cd /home/ubuntu/apps/app
git pull origin main
npm ci --omit=dev
npm run build 2>&1 | tee deploy-$(date +%Y%m%d).log
pm2 restart app
curl -sS -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/
```

## 9. Anti-Pola yang Dilarang
- Dilarang `ssh` tanpa `-n` di Windows (akan hang) — wajib `ssh -n`.
- Dilarang `rm -rf` pada path yang belum diverifikasi.
- Dilarang restart PM2 semua proses (`pm2 restart all`) tanpa alasan eksplisit.
- Dilarang mengekspos port aplikasi langsung ke publik tanpa reverse proxy + TLS.
- Dilarang menyimpan kredensial dalam file yang di-track git (gunakan environment variable).

## 10. Checklist Selesai
- [ ] Backup file yang diubah tersimpan (`.bak-YYYYMMDD`).
- [ ] `pm2 list` menunjukkan status `online` untuk aplikasi target.
- [ ] `curl` ke endpoint lokal mengembalikan 200/redirect yang benar.
- [ ] Tidak ada error baru di `pm2 logs` atau `journalctl`.
- [ ] Perubahan konfigurasi tercatat di `memory.md` bila bersifat arsitektural.
