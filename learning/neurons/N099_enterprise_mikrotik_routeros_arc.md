# N099: Enterprise MikroTik RouterOS Architecture and Traffic Engineering

- **Kategori:** MikroTik Routing
- **Tanggal Sintesis:** 2026-08-29 13:10:32
- **Status:** Active Operational Invariant

---

## 🎯 Inti Pembelajaran (Engineering Invariant)
Invarian rekayasa MikroTik RouterOS v7/v6: 1) Packet Flow & FastTrack acceleration (fasttrack-connection memotong firewall & queue trees untuk line-rate TCP/UDP); 2) Multi-WAN Load Balancing PCC (per-connection-classifier both-addresses-and-ports dengan routing-mark & check-gateway=ping failover); 3) Traffic shaping HTB & PCQ dynamic fair-sharing (pcq-rate=0 equal sharing); 4) Bridge VLAN Filtering dengan Hardware Offload ASIC (hw=yes pada CRS/CCR); 5) Enterprise BGP v7 dengan multi-threaded engine dan programmatic filter rules; 6) Site-to-Site WireGuard VPN (MTU 1420 & MSS clamping); 7) Raw Firewall pre-conntrack DDoS mitigation & staged brute-force address lists.

## 🔒 Disiplin Eksekusi
- Hindari pembuatan abstraksi berlebih (YAGNI).
- Terapkan perbaikan langsung pada fungsi akar bersama (*single root fix*).
- Kode tetap berada di bawah batas maksimal 300 baris per file.
