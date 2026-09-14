---
name: mikrotik
description: >-
  Standar operasional jaringan MikroTik RouterOS untuk konfigurasi firewall,
  NAT, VLAN, VPN, QoS, dan monitoring. Aktifkan skill ini ketika pengguna
  meminta konfigurasi, diagnostik, atau optimasi perangkat MikroTik
  (RouterOS v6/v7), termasuk VPN tunnel, hotspot, port forwarding,
  bandwidth shaping, dan pemecahan masalah konektivitas.
---

# MikroTik RouterOS Operations Skill

Skill ini adalah pedoman eksekusi tugas administrasi jaringan MikroTik:
firewall, NAT, VPN, QoS, VLAN, dan monitoring, dengan penekanan pada keamanan
dan verifikasi empiris. Seluruh perintah mengikuti sintaks RouterOS v7.

## 1. Prinsip Operasional
- **Grounding Faktual**: Baca konfigurasi aktual perangkat (`/export`) sebelum mengubah apa pun.
- **Non-Destructive First**: Selalu gunakan `print` atau `export` sebelum `set`.
- **Verifikasi Empiris**: Setiap perubahan wajib diuji (`ping`, `torch`, `log`) sebelum dinyatakan selesai.
- **Backup Sebelum Mutasi**: `/system backup save name=pre-change-YYYYMMDD` wajib dijalankan sebelum perubahan besar.

## 2. Konfigurasi Dasar (RouterOS v7)
```routeros
# Identitas & zona waktu
/system identity set name="ROUTER-CORE"
/system clock set time-zone-name=Asia/Jakarta

# Bridge + VLAN
/interface bridge add name=bridge-lan vlan-filtering=yes
/interface bridge vlan add bridge=bridge-lan tagged=bridge-lan vlan-ids=10,20,30

# IP addressing
/ip address add address=192.168.10.1/24 interface=bridge-lan
/ip dhcp-server add interface=bridge-lan address-pool=dhcp-pool disabled=no name=dhcp-lan
```

## 3. Firewall (Keamanan Berlapis)
```routeros
# Blokir akses Winbox dari WAN
/ip firewall filter add chain=input action=drop connection-state=new in-interface=ether1 dst-port=8291 protocol=tcp comment="Block Winbox from WAN"

# Drop invalid & port scan
/ip firewall filter add chain=input action=drop connection-state=invalid
/ip firewall filter add chain=input action=drop protocol=tcp psd=21,3s,3,1

# NAT masquerade
/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1 comment="Default MASQ"
```

## 4. VPN (WireGuard — v7 native)
```routeros
/interface wireguard add listen-port=13231 name=wireguard-vpn
/ip address add address=10.0.0.1/24 interface=wireguard-vpn
/interface wireguard peers add interface=wireguard-vpn public-key="<CLIENT_PUB>" allowed-address=10.0.0.2/32
/ip firewall filter add chain=input action=accept protocol=udp dst-port=13231 in-interface=ether1 comment="WireGuard"
```

## 5. QoS / Bandwidth Shaping (Simple Queue)
```routeros
/queue simple add name=limit-guest target=192.168.20.0/24 max-limit=5M/5M
/queue simple add name=voip-priority target=192.168.30.0/24 priority=1/1
```

## 6. Monitoring & Diagnostik
```routeros
/interface monitor-traffic ether1 once
/ip firewall connection print where dst-address~"zolu"
/log print where topics~"error"
/tool netwatch add host=8.8.8.8 interval=10s up-script=":log info WAN-UP" down-script=":log warning WAN-DOWN"
```

## 7. Anti-Pola yang Dilarang
- Tidak boleh menonaktifkan firewall filter tanpa backup dan alasan eksplisit.
- Dilarang meng-ekspos Winbox/SSH ke WAN publik (gunakan VPN atau address list allowlist).
- Dilarang memakai default admin/password tanpa diganti.
- Dilarang menjalankan `/import` skrip dari sumber tidak terverifikasi.

## 8. Checklist Selesai
- [ ] `/export` sebelum dan sesudah dibandingkan.
- [ ] Akses Winbox/SSH masih bisa dari jaringan internal.
- [ ] Log tidak menampilkan error baru.
- [ ] Backup post-change tersimpan (`/system backup save`).
