# World-Class Computer Networking & MikroTik RouterOS Architecture: The Definitive Reference

**Author:** Claudia Engineering Architecture (Gahar Inovasi Teknologi)  
**Compiled:** 2026-08-29 13:10:30  
**Standard:** Ultra-Dense, Pragmatic, High-Performance Systems & Enterprise Network Engineering

---

## 📑 Table of Contents
1. [The Networking Stack: Layer-by-Layer Architectural Invariants](#1-the-networking-stack)
2. [Transport Layer: TCP, UDP, QUIC, and Congestion Control](#2-transport-layer)
3. [Low-Level Socket Programming & Asynchronous I/O (epoll, io_uring)](#3-low-level-socket-programming)
4. [Kernel Networking, eBPF & XDP High-Speed Packet Processing](#4-kernel-networking-ebpf--xdp)
5. [MikroTik RouterOS v7 & Enterprise Traffic Engineering](#5-mikrotik-routeros-v7--enterprise-traffic-engineering)
6. [Distributed Cloud Networking, CNI, & Service Mesh](#6-distributed-cloud-networking-cni--service-mesh)
7. [Network Security, Protocol Exploits, and Cryptographic Defenses](#7-network-security--defenses)

---

## 1. The Networking Stack: Layer-by-Layer Architectural Invariants

### OSI 7-Layer vs TCP/IP 4-Layer Mapping
| Layer | OSI Name | TCP/IP Layer | PDU (Protocol Data Unit) | Core Protocols & Hardware |
|---|---|---|---|---|
| 7 | Application | Application | Data / Payload | HTTP/1.1, HTTP/2, HTTP/3, gRPC, DNS, SSH, TLS |
| 6 | Presentation | Application | Data | ASN.1, Protobuf, JSON, TLS Encryption/Decryption |
| 5 | Session | Application | Data | RPC, gRPC Streams, SOCKS5 |
| 4 | Transport | Transport | Segment (TCP) / Datagram (UDP) | TCP (RFC 9293), UDP (RFC 768), QUIC (RFC 9000), SCTP |
| 3 | Network | Internet | Packet | IPv4 (RFC 791), IPv6 (RFC 8200), ICMP, BGP-4, OSPF, IPsec |
| 2 | Data Link | Link / Network Access | Frame | Ethernet (802.3), Wi-Fi (802.11), ARP, VLAN (802.1Q), VXLAN |
| 1 | Physical | Link / Network Access | Bit | Optical Fiber, Copper Twisted Pair, NIC PHY, Transceivers |

### Key Transmission Invariants
- **MTU (Maximum Transmission Unit):** Standard Ethernet MTU is 1500 bytes. IP Header (20 bytes) + TCP Header (20 bytes) leaves **MSS (Maximum Segment Size) = 1460 bytes**.
- **PMTUD (Path MTU Discovery):** Uses ICMP Type 3 Code 4 ('Fragmentation Needed and DF set') to dynamically discover the minimum MTU along an end-to-end path without IP fragmentation.

---

## 2. Transport Layer: TCP, UDP, QUIC, and Congestion Control

### TCP 3-Way Handshake & Teardown State Transitions
```
 Client                                                  Server
   |                        SYN (seq=x)                     | (LISTEN)
   | -----------------------------------------------------> |
(SYN_SENT)               SYN+ACK (seq=y, ack=x+1)           | (SYN_RCVD)
   | <----------------------------------------------------- |
(ESTABLISHED)               ACK (ack=y+1)                   | (ESTABLISHED)
   | -----------------------------------------------------> |
   |                                                        |
   |                   DATA TRANSFER PHASE                  |
   |                                                        |
(Active Close)              FIN (seq=u)                     | (Passive Close)
   | -----------------------------------------------------> | (CLOSE_WAIT)
(FIN_WAIT_1)                ACK (ack=u+1)                   |
   | <----------------------------------------------------- |
(FIN_WAIT_2)                FIN (seq=v)                     | (LAST_ACK)
   | <----------------------------------------------------- |
(TIME_WAIT)                 ACK (ack=v+1)                   | (CLOSED)
   | -----------------------------------------------------> |
 (2*MSL = 60s)
(CLOSED)
```

---

## 3. Low-Level Socket Programming & Asynchronous I/O
- **Linux epoll Edge-Triggered (`EPOLLET`):** Mandates non-blocking sockets (`O_NONBLOCK`) and exhaustive draining loop until `EAGAIN` to prevent socket starvation.
- **Zero-Copy Primitives:** `sendfile()`, `splice()`, and `io_uring MSG_ZEROCOPY` eliminate context switches and CPU cache pollution by delegating DMA page transfers directly to network hardware.

---

## 4. Kernel Networking, eBPF & XDP High-Speed Packet Processing
- **XDP (eXpress Data Path):** Runs eBPF programs in the network driver RX ring before `sk_buff` memory allocation, achieving >40 Mpps line-rate packet processing.
- **SOCKMAP Acceleration:** Intercepts localhost TCP streams and redirects socket buffers directly between sender and receiver queues, bypassing kernel TCP/IP stack overhead by up to 80%.

---

## 5. MikroTik RouterOS v7 & Enterprise Traffic Engineering

### 5.1 Packet Flow & FastTrack Acceleration
- **Packet Flow Ingress/Egress:**
  1. `Prerouting`: Raw Table -> Connection Tracking -> Mangle Prerouting -> Destination NAT (D-NAT)
  2. `Routing Decision`: Local Input vs Transit Forward
  3. `Forward`: Mangle Forward -> Filter Forward -> Queue Tree Global/Interface
  4. `Postrouting`: Mangle Postrouting -> Queue Tree Interface -> Source NAT (Masquerade) -> Egress
- **FastTrack Invariant:** `action=fasttrack-connection` skips firewall inspection and queue trees for established TCP/UDP connections. Yields maximum throughput on high-gigabit hardware, but must be bypassed when per-client QoS / Queue Tree shaping is strictly enforced.

### 5.2 Multi-WAN Load Balancing with PCC (Per Connection Classifier)
- Uses hash function `per-connection-classifier=both-addresses-and-ports:N/i` to distribute outbound streams across multiple ISP uplinks.
- Preserves sticky sessions for HTTPS banking and prevents asymmetric routing drops via symmetrical input/output connection marks (`mark-connection` / `mark-routing`).
- Failover managed with `check-gateway=ping` and distance metrics in `/ip route`.

### 5.3 QoS, HTB & PCQ (Per Connection Queue)
- **Hierarchical Token Bucket (HTB):** Parent queues define total bandwidth capacity (`max-limit`), child queues allocate guaranteed minimum (`limit-at`) and dynamically borrow remaining tokens based on priority (1 to 8).
- **PCQ Dynamic Equal Sharing:** Automatically balances bandwidth equally among all active client IPs (`pcq-rate=0`), eliminating the overhead of managing thousands of individual simple queues.

### 5.4 Bridge VLAN Filtering & Hardware Offload (CRS/CCR)
- Replaces legacy CPU software bridging with switch chip ASIC hardware offloading (`hw=yes`).
- `/interface bridge vlan` maps tagged trunk ports and untagged access ports (`pvid=X`) with 0% CPU consumption during wire-speed L2/L3 frame forwarding.

### 5.5 Enterprise BGP in RouterOS v7
- Redesigned routing engine with multi-core convergence and C-style programmatic `/routing filter rule`.
- Supports full global BGP routing tables (900k+ prefixes), AS-Path prepending, BGP communities, and dynamic peer route origin validation.

### 5.6 WireGuard Site-to-Site Tunneling
- High-speed modern VPN using state-of-the-art cryptography (ChaCha20-Poly1305, Curve25519).
- Standard MTU is 1420 bytes to accommodate 80-byte encapsulation overhead. MSS Clamping (`change-mss=clamp-to-pmtu`) prevents TCP fragmentation blackholes.

---

## 6. Distributed Cloud Networking, CNI, & Service Mesh
- **Overlay (VXLAN) vs Flat BGP (Calico):** Overlay encapsulates L2 in UDP (50B tax); Flat BGP peers directly with ToR switches for wire speed without MTU penalties.
- **L4 Direct Server Return (DSR):** Scales load balancers 10x-100x by modifying destination MAC on ingress while backend servers respond directly to clients with the VIP as source.

---

## 7. Network Security, Protocol Exploits, and Cryptographic Defenses
- **SYN Cookies:** Statelessly encode connection data in 32-bit ISN to neutralize TCP SYN Floods.
- **RPKI & BGP Route Origin Validation (ROV):** Cryptographically signs prefix ownership to stop malicious BGP hijacking and subprefix theft.
- **DNSSEC & Port Randomization:** Neutralizes Kaminsky DNS cache poisoning by expanding entropy space to 32 bits and verifying digital signatures (RRSIG/DNSKEY/DS) from the ICANN root zone.
- **RouterOS Raw Firewall:** Drops DDoS attacks and port scans before Connection Tracking (`conntrack`), preventing CPU starvation.

---
**Synthesized by Claudia Autonomous AI Systems Engine - Gahar Inovasi Teknologi**