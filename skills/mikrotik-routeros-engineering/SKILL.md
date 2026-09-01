---
name: mikrotik-routeros-engineering
description: Production-grade engineering guide and empirical configuration reference for MikroTik RouterOS v7. Covers routing engine invariants, L3 hardware offloading, connection tracking, multi-tier firewall hardening, PCC multi-WAN load balancing, recursive routing failover, WireGuard site-to-site & hub-and-spoke topologies, hierarchical Queue Trees with PCQ/CAKE bufferbloat mitigation, and failure-resilient automation scripting with Telegram alerting.
---

# MikroTik RouterOS v7 Enterprise Engineering Reference

Production-grade, zero-hallucination operational architecture for MikroTik RouterOS v7 (v7.10+). Covers core kernel invariants, high-throughput packet processing, deterministic firewall security, multi-WAN load balancing, modern WireGuard VPN infrastructure, advanced QoS queue scheduling, and automated runtime operations.

---

## 1. RouterOS v7 Core Invariants & Packet Architecture

### A. The RouterOS v7 Routing Engine Rewrite
RouterOS v7 replaces the legacy routing daemon of v6 with an asynchronous routing engine:
* **FIB & Routing Tables**: Routing tables are no longer created dynamically via mangle marks. Every custom routing table **must** be explicitly defined with the `fib` flag enabled before reference.
  ```routeros
  /routing table add name=to_WAN1 fib
  /routing table add name=to_WAN2 fib
  ```
* **Routing Rules vs. Mangle Routing Marks**: Routing marks applied in `/ip firewall mangle` select an active FIB table. Alternatively, `/routing rule` allows deterministic table selection without mangle connection-tracking overhead.

### B. FastPath, FastTrack, and L3 Hardware Offloading (L3HW)
```
[ Ingress Packet ]
       |
       v
[ L3 Hardware Offload (Switch ASIC) ] ---> (Bypasses CPU completely: Line-rate inter-VLAN routing)
       | (Miss / Unsupported Feature)
       v
[ FastPath / FastTrack ] -------------> (Bypasses Firewall Mangle & Queues: Max CPU throughput)
       | (Miss / Mangle Required / Queued)
       v
[ Full Slow Path (Conntrack -> Raw -> Mangle -> Filter -> Queues) ]
```

* **FastTrack Invariant**: FastTrack bypasses `/ip firewall mangle` and `/queue tree`. If per-packet bandwidth shaping or QoS packet marking is required, FastTrack **must be selectively bypassed** or disabled.

---

## 2. Multi-Tier Firewall Hardening (Raw, Filter, NAT)

### A. Raw Table Hardware-Level Drop (Zero CPU Conntrack Overhead)
```routeros
/ip firewall raw
add action=drop chain=prerouting comment="defconf: drop invalid in raw" connection-state=invalid
add action=drop chain=prerouting in-interface-list=WAN src-address-list=BOGONS comment="drop bogons from WAN"
add action=drop chain=prerouting protocol=tcp tcp-flags=!fin,!syn,!rst,!ack comment="drop TCP NULL scan"
add action=drop chain=prerouting protocol=tcp tcp-flags=fin,syn comment="drop TCP SYN-FIN scan"
```

### B. SSH & Winbox Brute-Force Blacklisting
```routeros
/ip firewall filter
add action=drop chain=input src-address-list=SSH_BLACKLIST dst-port=22,8291 protocol=tcp comment="drop brute-force attackers"
add action=add-src-to-address-list address-list=SSH_BLACKLIST address-list-timeout=7d chain=input connection-state=new dst-port=22,8291 protocol=tcp src-address-list=SSH_STAGE3
add action=add-src-to-address-list address-list=SSH_STAGE3 address-list-timeout=1m chain=input connection-state=new dst-port=22,8291 protocol=tcp src-address-list=SSH_STAGE2
add action=add-src-to-address-list address-list=SSH_STAGE2 address-list-timeout=1m chain=input connection-state=new dst-port=22,8291 protocol=tcp src-address-list=SSH_STAGE1
add action=add-src-to-address-list address-list=SSH_STAGE1 address-list-timeout=1m chain=input connection-state=new dst-port=22,8291 protocol=tcp
```

### C. TCP MSS Clamping for PPPoE / VPN Tunnels
```routeros
/ip firewall mangle
add action=change-mss chain=forward new-mss=clamp-to-pmtu passthrough=yes protocol=tcp tcp-flags=syn
add action=change-mss chain=forward new-mss=1412 out-interface-list=WAN protocol=tcp tcp-flags=syn tcp-mss=1413-65535 comment="clamp TCP MSS for PPPoE MTU 1492"
```

---

## 3. Multi-WAN: PCC Load Balancing & Recursive Routing Failover

### A. Per-Connection Classifier (PCC)
```routeros
/ip firewall mangle
add action=accept chain=prerouting dst-address=192.168.0.0/16 in-interface-list=LAN
add action=mark-connection chain=prerouting in-interface-list=LAN connection-state=new per-connection-classifier=both-addresses:2/0 new-connection-mark=CONN_WAN1 passthrough=yes
add action=mark-connection chain=prerouting in-interface-list=LAN connection-state=new per-connection-classifier=both-addresses:2/1 new-connection-mark=CONN_WAN2 passthrough=yes
add action=mark-routing chain=prerouting in-interface-list=LAN connection-mark=CONN_WAN1 new-routing-mark=to_WAN1 passthrough=no
add action=mark-routing chain=prerouting in-interface-list=LAN connection-mark=CONN_WAN2 new-routing-mark=to_WAN2 passthrough=no
```

### B. Recursive Routing Failover with Check-Gateway
```routeros
/ip route
add dst-address=1.1.1.1/32 gateway=192.168.1.1 scope=10 comment="Host route to Cloudflare DNS via WAN1"
add dst-address=8.8.8.8/32 gateway=192.168.2.1 scope=10 comment="Host route to Google DNS via WAN2"
add dst-address=0.0.0.0/0 gateway=1.1.1.1 check-gateway=ping distance=1 target-scope=11 comment="Primary WAN1 via 1.1.1.1"
add dst-address=0.0.0.0/0 gateway=8.8.8.8 check-gateway=ping distance=2 target-scope=11 comment="Secondary WAN2 via 8.8.8.8"
```

---

## 4. Modern WireGuard VPN Infrastructure

```routeros
/interface wireguard
add name=wg-cloud listen-port=51820 mtu=1420

/interface wireguard peers
add interface=wg-cloud public-key="SERVER_PUBLIC_KEY=" endpoint-address=vps.zolu.my.id endpoint-port=51820 allowed-address=10.0.0.0/24 persistent-keepalive=25s

/ip address
add address=10.0.0.2/24 interface=wg-cloud
```

---

## 5. Hierarchical Queue Trees & PCQ Bandwidth Management

```routeros
/queue type
add name=PCQ_Download kind=pcq pcq-classifier=dst-address pcq-rate=0 pcq-total-limit=2000KiB
add name=PCQ_Upload kind=pcq pcq-classifier=src-address pcq-rate=0 pcq-total-limit=2000KiB

/queue tree
add name=TOTAL_DOWNLOAD parent=bridge1 max-limit=100M
add name=LAN_PCQ_DOWN parent=TOTAL_DOWNLOAD limit-at=90M max-limit=100M queue=PCQ_Download packet-mark=PM_DOWN
add name=TOTAL_UPLOAD parent=WAN1 max-limit=50M
add name=LAN_PCQ_UP parent=TOTAL_UPLOAD limit-at=45M max-limit=50M queue=PCQ_Upload packet-mark=PM_UP
```
