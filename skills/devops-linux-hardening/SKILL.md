---
name: devops-linux-hardening
description: Production-grade reference and actionable patterns for Linux server hardening, process management (PM2), Nginx reverse proxy optimization, Cloudflare zero-trust tunneling, UFW firewall configuration, and empirical system diagnostics.
---

# Linux DevOps, Hardening & Runtime Infrastructure

Empirical, battle-tested operational guide for Linux server administration, production web service deployment, runtime process reliability, network security boundaries, and high-load performance tuning.

---

## 1. Process Management with PM2 & Systemd

### A. Execution Modes: Fork vs. Cluster
- **Fork Mode (`exec_mode: 'fork'`)**:
  - **Use for**: Single-threaded workloads, scripts, background workers/queues, stateful applications (in-memory caching, socket rooms without Redis adapter), or Next.js standalone servers.
  - **Execution**: `pm2 start ecosystem.config.js --only app-fork`
- **Cluster Mode (`exec_mode: 'cluster'`, `instances: 'max'` or integer)**:
  - **Use for**: Stateless HTTP services and REST APIs scaling across all available CPU cores.
  - **Invariant**: Zero shared memory between instances; sessions and caches must be externalized (Redis, DB).
  - **Next.js Standalone Caveat**: `exec_mode: 'cluster'` requires distinct port handling or Node.js internal cluster load balancing (`PORT` managed by PM2 master).

### B. Production `ecosystem.config.js` Standard
```javascript
module.exports = {
  apps: [
    {
      name: 'prod-api',
      script: 'dist/index.js',
      instances: 2,
      exec_mode: 'cluster',
      max_memory_restart: '1G',
      autorestart: true,
      watch: false,
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: '/var/log/pm2/prod-api-error.log',
      out_file: '/var/log/pm2/prod-api-out.log',
      merge_logs: true,
      time: true,
      kill_timeout: 5000,
      listen_timeout: 8000
    }
  ]
};
```

### C. Log Rotation & Disk Protection
Unbounded logs will exhaust inodes and disk space. Enforce `pm2-logrotate`:
```bash
# Install PM2 logrotate module
pm2 install pm2-logrotate

# Enforce strict rotation policies (Empirical standards)
pm2 set pm2-logrotate:max_size 50M        # Rotate when file reaches 50MB
pm2 set pm2-logrotate:retain 10          # Keep at most 10 rotated logs
pm2 set pm2-logrotate:compress true      # Compress rotated logs with gzip (.gz)
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss
pm2 set pm2-logrotate:rotateInterval '0 0 * * *' # Force daily rotation at midnight
```

### D. Systemd Boot Persistence
Ensure processes recover cleanly across OS restarts:
```bash
# Generate and register systemd unit for current active user
pm2 startup systemd -u $(whoami) --hp $HOME
# (Execute the command string output by PM2 with sudo if prompted)

# Freeze active process list to ~/.pm2/dump.pm2
pm2 save

# Verify systemd service status
sudo systemctl status pm2-$(whoami)
```

---

## 2. Nginx Reverse Proxy Hardening & Performance

### A. SSL/TLS 1.2/1.3 Hardening & Security Headers
Disable insecure legacy protocols (SSLv3, TLS 1.0, TLS 1.1) and weak ciphers.

```nginx
# /etc/nginx/conf.d/ssl-params.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_ecdh_curve X25519:prime256v1:secp384r1;

# Session Cache & Tickets
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# OCSP Stapling (Direct origin verification with DNS resolver)
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 8.8.8.8 valid=300s;
resolver_timeout 5s;

# Security Headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

### B. Upstream Load Balancing & Keepalive
Prevent ephemeral port exhaustion by recycling TCP connections to upstream Node.js/Go/Python apps:

```nginx
upstream node_backend {
    server 127.0.0.1:3000 max_fails=3 fail_timeout=10s;
    keepalive 64; # Maintain persistent connection pool to upstream
}
```

### C. Proxy Buffering & WebSocket HMR Passthrough
Production virtual host configuration supporting HTTP/2, buffer isolation, and full WebSocket/SSE streaming:

```nginx
# /etc/nginx/sites-available/app.conf
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    include /etc/nginx/conf.d/ssl-params.conf;

    # Client body and buffer limits
    client_max_body_size 25M;
    client_body_buffer_size 128k;

    location / {
        proxy_pass http://node_backend;
        proxy_http_version 1.1;

        # WebSocket and Next.js / Vite HMR Passthrough
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        # Real Client IP and Host preservation
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upstream Keepalive Header Reset
        proxy_set_header Connection "";

        # Buffering Tuning for High-Throughput APIs
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 16 8k;
        proxy_busy_buffers_size 16k;

        # Timeouts for Long-Polling / WebSockets
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## 3. Networking, Firewalls & Zero-Trust Tunneling

### A. UFW (Uncomplicated Firewall) Hardening
Enforce default-deny architecture. Only permit explicitly audited ingress vectors.

```bash
# 1. Reset and set default baseline policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. Allow loopback interface traffic
sudo ufw allow in on lo to any

# 3. Secure SSH with rate-limiting (Anti-Bruteforce)
sudo ufw limit proto tcp from any to any port 22 comment 'SSH Rate Limited'

# 4. Allow Standard Web Ingress (When hosting public IP directly)
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# 5. Enable and verify firewall
sudo ufw enable
sudo ufw status verbose
```

### B. Cloudflare Tunnel (Zero-Trust Origin Isolation)
Using Cloudflare Tunnels (`cloudflared`), public ports 80/443 can be completely closed on UFW, eliminating port scanning and direct DDoS vectors.

#### 1. Tunnel Ingress Configuration (`/etc/cloudflared/config.yml`)
```yaml
tunnel: <TUNNEL_UUID>
credentials-file: /etc/cloudflared/<TUNNEL_UUID>.json

ingress:
  # Next.js App
  - hostname: app.example.com
    service: http://127.0.0.1:3000
    originRequest:
      connectTimeout: 30s
      noTLSVerify: false
      keepAliveConnections: 100

  # API Backend via local Nginx
  - hostname: api.example.com
    service: http://127.0.0.1:80
    originRequest:
      httpHostHeader: api.example.com

  # Default Catch-all rule (Mandatory)
  - service: http_status:404
```

#### 2. Service Daemon Installation & Invariant
```bash
# Install and register cloudflared as a systemd service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Hardening Invariant: If using Cloudflare Tunnel exclusively, close external ports 80/443 in UFW:
sudo ufw delete allow 80/tcp
sudo ufw delete allow 443/tcp
```

---

## 4. Linux System Diagnostics & Resource Tuning

### A. Memory & Swap Optimization
Prevent random kernel OOM (Out Of Memory) killer strikes on database or Node.js processes.

#### 1. Swap Space Provisioning (Empirical Standard)
```bash
# Create dedicated 4GB swapfile with root-only permissions
sudo fallocate -l 4G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Persist across reboot in /etc/fstab
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 2. Kernel Memory Sysctl Tuning (`/etc/sysctl.d/99-sysctl.conf`)
```ini
# Avoid aggressive swapping; only swap when physical RAM is nearly exhausted
vm.swappiness = 10

# Balance filesystem inode/dentry cache reclaim rate
vm.vfs_cache_pressure = 50

# Increase max open file descriptors for high-concurrency sockets
fs.file-max = 2097152

# Network connection backlog and TIME_WAIT socket recycling
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
```
Apply immediately:
```bash
sudo sysctl --system
```

### B. High-Precision Diagnostic Commands

| Diagnostic Vector | Command | Practical Purpose & Flags |
| :--- | :--- | :--- |
| **System Resources** | `htop` / `top -b -n 1 \| head -n 20` | Real-time CPU, RAM, load average per core. |
| **Process Inspection** | `ps aux --sort=-%mem \| head -n 10` | Top 10 memory-consuming processes. |
| | `ps aux --sort=-%cpu \| head -n 10` | Top 10 CPU-consuming processes. |
| **Socket & Port Conflicts** | `sudo ss -tulpn` | Active listening TCP/UDP sockets with process PIDs. |
| | `sudo lsof -i :3000` | Identify exact process holding port 3000. |
| | `sudo lsof -p <PID>` | Inspect all open file descriptors / sockets for a process. |
| **Journalctl Logs** | `journalctl -u nginx --since "1 hour ago" --no-pager` | Filter logs by unit and timestamp. |
| | `journalctl -p err -b --no-pager` | Errors only since current boot. |
| | `sudo journalctl --vacuum-size=200M` | Clean up oversized systemd journal logs. |
| **Disk Space & Inodes** | `df -h` / `df -i` | Human-readable disk capacity and inode exhaustion checks. |
| | `du -sh /* 2>/dev/null \| sort -hr \| head -n 10` | Identify largest directory footprints. |
| **Disk I/O Latency** | `iostat -xz 1 5` | Per-device `%util`, `await` (queue wait latency ms). |
| | `sudo iotop -oPa` | Pinpoint specific processes generating high disk write/read throughput. |

---

## 5. Security & Operational Checklist

1. **Root Login & Password Authentication**: Always disable `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
2. **Time Synchronization**: Ensure `chrony` or `systemd-timesyncd` is active (`timedatectl status`) to prevent JWT clock-skew issues.
3. **Automated Security Updates**: Enable `unattended-upgrades` on Debian/Ubuntu systems.
4. **Log Inspection Invariant**: Always inspect raw error logs before issuing process restarts (`tail -n 100 /var/log/nginx/error.log`).
