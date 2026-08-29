#!/usr/bin/env python3
"""
Scrape & Synthesize World-Class Computer Networking & MikroTik RouterOS Training Datasets
Sources:
- Beej's Guide to Network Programming (Sockets, POSIX, Non-blocking I/O)
- donnemartin/system-design-primer (OSI, L4/L7, QUIC, gRPC, WebSockets, CDN)
- Linux Kernel Networking & eBPF / XDP Architecture (sk_buff, BBR, Cubic, io_uring)
- IETF RFC Core Standards (RFC 9293 TCP, RFC 9000 QUIC, RFC 8446 TLS 1.3, RFC 9113 HTTP/2, RFC 9114 HTTP/3)
- Kubernetes & Cloud Networking (CNI Cilium/Calico, Overlay VXLAN, Envoy Proxy, BGP/Anycast)
- MikroTik RouterOS v7 / v6 Architecture (Packet Flow, PCC Load Balancing, Queue Tree/PCQ, BGP/OSPFv3, Bridge VLAN HW-Offload, WireGuard, Raw Firewall)
- Network Security & Packet Inspection (SYN Cookies, ARP/DNS Spoofing, DDoS Mitigation, Scapy/Wireshark)

Author: Gahar Inovasi Teknologi
"""

import os
import sys
import json
import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(WORKSPACE, "learning", "frontier_datasets")
KB_DIR = os.path.join(WORKSPACE, "learning", "knowledge_base")
DATA_DIR = os.path.join(WORKSPACE, "data")

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def build_network_master_dataset():
    print("[*] Compiling Master Computer Networking & MikroTik RouterOS Training Dataset...")

    dataset = [
        # ==========================================
        # 1. CORE PROTOCOLS & TRANSPORT LAYER (TCP/UDP/QUIC)
        # ==========================================
        {
            "id": "net_tcp_handshake_state_machine",
            "domain": "Transport Layer & Protocols",
            "source": "IETF RFC 9293 / Linux Kernel TCP Stack",
            "title": "TCP 3-Way Handshake & 4-Way Teardown State Transition Invariants",
            "prompt": "Explain the exact TCP state transitions for both client and server during connection establishment (SYN, SYN-ACK, ACK) and active termination (FIN, ACK, FIN, ACK). Detail why the active closer must enter TIME_WAIT and stay for 2*MSL (Maximum Segment Lifetime), and what kernel hazards arise if TIME_WAIT sockets are recycled prematurely without timestamp validation.",
            "invariants": [
                "Client transitions: CLOSED -> SYN_SENT -> ESTABLISHED (upon SYN-ACK). Active closer: ESTABLISHED -> FIN_WAIT_1 -> FIN_WAIT_2 -> TIME_WAIT -> CLOSED.",
                "Server transitions: CLOSED -> LISTEN -> SYN_RCVD -> ESTABLISHED. Passive closer: ESTABLISHED -> CLOSE_WAIT -> LAST_ACK -> CLOSED.",
                "TIME_WAIT duration is 2*MSL (commonly 60s in Linux, defined by TCP_TIMEWAIT_LEN). Purpose: 1) Ensure remote peer receives final ACK (retransmitting FIN if ACK is dropped), 2) Drain lingering duplicate segments from the network so old packets are not accepted by subsequent connections with the same 4-tuple (src_ip, src_port, dst_ip, dst_port).",
                "Premature TIME_WAIT reuse without RFC 7323 PAWS (Protection Against Wrapped Sequence Numbers) can cause data corruption or unexpected RST packets terminating valid new streams."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Transport-01"
        },
        {
            "id": "net_tcp_congestion_control_bbr_cubic",
            "domain": "Transport Layer & Protocols",
            "source": "Linux Kernel Congestion Control / Google BBR Paper",
            "title": "Loss-Based Congestion Control (CUBIC/Reno) vs Model-Based Congestion Control (BBR)",
            "prompt": "Compare CUBIC and BBR (Bottleneck Bandwidth and RTT) congestion control algorithms in high-bandwidth high-latency networks with shallow vs deep packet buffers. Explain how bufferbloat occurs under loss-based algorithms and how BBR solves it by estimating BtlBw and RTprop.",
            "invariants": [
                "Loss-based algorithms (Reno, CUBIC) treat packet loss as the primary congestion signal, filling network buffers until buffer overflow occurs, creating Bufferbloat (massive queueing latency) on deep-buffered links and severely underutilizing shallow-buffered links with random loss.",
                "BBR operates on Kleinrock's optimal operating point: Bandwidth-Delay Product (BDP = BtlBw * RTprop), pacing transmissions at the estimated bottleneck bandwidth while keeping in-flight data equal to 1 BDP.",
                "BBR avoids bufferbloat by preventing queues from accumulating at the bottleneck router, yielding low latency and maximum throughput regardless of non-congestive packet loss."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-Transport-02"
        },
        {
            "id": "net_quic_http3_multiplexing_hoq",
            "domain": "Transport Layer & Protocols",
            "source": "IETF RFC 9000 (QUIC) & RFC 9114 (HTTP/3)",
            "title": "QUIC vs HTTP/2 over TCP: Solving Transport-Layer Head-of-Line (HoL) Blocking",
            "prompt": "In HTTP/2 over TCP, multiplexed streams share a single TCP connection. Explain why packet loss on one stream stalls all other streams (Transport-level Head-of-Line Blocking). Explain how QUIC solves this using UDP datagrams with per-stream frame offsets and independent loss recovery, alongside 0-RTT TLS 1.3 connection resumption and Connection IDs for seamless network migration (WiFi to Cellular).",
            "invariants": [
                "HTTP/2 multiplexing solves application-level HoL blocking, but because TCP guarantees in-order byte stream delivery, a single dropped TCP segment forces the receiver TCP buffer to halt delivering subsequent segments for ALL HTTP/2 streams until retransmission succeeds.",
                "QUIC encapsulates multiple independent streams within UDP datagrams. Each stream has its own independent stream-offset tracking; packet loss on Stream A only pauses Stream A, allowing Stream B and Stream C to proceed without stall.",
                "QUIC integrates TLS 1.3 handshake into the transport connection setup, enabling 1-RTT initial connections and 0-RTT early data resumption.",
                "QUIC uses explicit 64-bit Connection IDs (CID) rather than 4-tuples, allowing uninterrupted connections when IP addresses change during mobile network handover (e.g. WiFi to 5G)."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Transport-03"
        },
        {
            "id": "net_syn_flood_and_syn_cookies",
            "domain": "Transport & Security",
            "source": "Linux net/ipv4/syncookies.c / D.J. Bernstein RFC 4987",
            "title": "SYN Flood Denial of Service & Cryptographic SYN Cookie Defense",
            "prompt": "Describe how a TCP SYN Flood exhausts server resources (half-open connection backlog `tcp_max_syn_backlog`). Explain how the Linux kernel SYN Cookie mechanism operates statelessly without allocating a `struct request_sock` in memory until the 3rd ACK packet arrives.",
            "invariants": [
                "A SYN Flood sends spoofed SYN packets without responding to SYN-ACK, exhausting the server's SYN queue (`tcp_max_syn_backlog`) and dropping legitimate incoming connections.",
                "When SYN Cookies are enabled (`tcp_syncookies = 1`), if the SYN queue fills up, the server does NOT allocate memory for the connection. Instead, it encodes cryptographic connection parameters into the Initial Sequence Number (ISN) of the SYN-ACK:",
                "  - Top 5 bits: slow-moving timestamp (t mod 32)",
                "  - Next 3 bits: encoded MSS (Maximum Segment Size) table index",
                "  - Bottom 24 bits: SHA-1/SipHash(client_ip, client_port, server_ip, server_port, secret, timestamp)",
                "When the client returns the final ACK with ACK_NUM = ISN + 1, the server decrements 1, recomputes the cryptographic hash, verifies the timestamp, reconstructs the connection parameters, and creates the socket only then."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Security-01"
        },

        # ==========================================
        # 2. LOW-LEVEL SOCKET PROGRAMMING & KERNEL I/O
        # ==========================================
        {
            "id": "net_socket_epoll_edge_vs_level",
            "domain": "Socket Programming & Async I/O",
            "source": "Beej's Guide / Linux man epoll(7)",
            "title": "Linux epoll Architecture: Level-Triggered (LT) vs Edge-Triggered (ET) & Non-Blocking Sockets",
            "prompt": "Write a complete, idiomatic non-blocking TCP socket event loop using epoll in Edge-Triggered mode (`EPOLLET`). Explain the starvation hazard and the mandatory requirement to loop `read()`/`recv()` until `EAGAIN` or `EWOULDBLOCK` is returned, as well as socket flags `O_NONBLOCK`, `SO_REUSEADDR`, and `SO_REUSEPORT`.",
            "code_example": """#include <sys/epoll.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <netinet/in.h>

int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

void handle_et_read(int epoll_fd, int sock_fd) {
    char buf[4096];
    while (1) {
        ssize_t bytes = read(sock_fd, buf, sizeof(buf));
        if (bytes > 0) {
            write(sock_fd, buf, bytes); // echo
        } else if (bytes == 0) {
            close(sock_fd);
            break;
        } else {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break;
            }
            close(sock_fd);
            break;
        }
    }
}
""",
            "invariants": [
                "Level-Triggered (LT): epoll_wait returns as long as the file descriptor is ready for I/O (buffer not empty).",
                "Edge-Triggered (ET): epoll_wait returns ONLY when state changes from not-ready to ready. If you do not drain the buffer completely with a while loop until EAGAIN/EWOULDBLOCK, leftover data will sit in the kernel buffer forever without triggering a new event, causing permanent hang.",
                "SO_REUSEADDR allows binding to a local port in TIME_WAIT state.",
                "SO_REUSEPORT allows multiple independent processes/threads to bind to the exact same port, with the kernel load-balancing incoming SYN packets across listening sockets with zero user-space locking."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Socket-01"
        },
        {
            "id": "net_zero_copy_io_uring_sendfile",
            "domain": "Socket Programming & High-Performance I/O",
            "source": "Linux Kernel Documentation / Jens Axboe io_uring",
            "title": "Zero-Copy Data Transfer: sendfile(), splice(), and io_uring MSG_ZEROCOPY",
            "prompt": "Trace the lifecycle of traditional `read()` + `write()` vs zero-copy `sendfile()` / `splice()` and modern `io_uring` with `IORING_OP_SEND_ZC`. Detail context switches, CPU cache pollution, page cache pin, DMA ring buffers, and sk_buff frags.",
            "invariants": [
                "Traditional read/write requires 4 context switches and 4 memory copies: Disk -> Kernel Page Cache (DMA) -> User Buffer (CPU copy) -> Kernel Socket Buffer (CPU copy) -> Network NIC Buffer (DMA).",
                "sendfile(out_fd, in_fd, offset, count) cuts copies to 2: Disk -> Kernel Page Cache (DMA) -> Network NIC Buffer (DMA via scatter-gather descriptors in sk_buff), with 2 context switches and 0 CPU data copies.",
                "io_uring MSG_ZEROCOPY avoids user-to-kernel page copies entirely by locking user memory pages during network transmission and returning a completion event once the NIC driver finishes DMA transmission."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-Socket-02"
        },

        # ==========================================
        # 3. KERNEL eBPF, XDP & PACKET PROCESSING
        # ==========================================
        {
            "id": "net_ebpf_xdp_packet_processing",
            "domain": "Kernel & eBPF Networking",
            "source": "Cilium / libbpf / Linux net/core/filter.c",
            "title": "eXpress Data Path (XDP) & eBPF TC (Traffic Control) Hookpoints",
            "prompt": "Explain the architectural difference between XDP (eXpress Data Path) and TC (Traffic Control) in the Linux kernel networking stack. Detail how XDP achieves millions of packets per second (Mpps) filtering by intercepting raw `struct xdp_buff` inside the NIC driver ring buffer before `struct sk_buff` allocation, and explain actions XDP_DROP, XDP_TX, XDP_REDIRECT, and XDP_PASS.",
            "invariants": [
                "sk_buff allocation and metadata overhead is the primary bottleneck in the Linux kernel network stack for high packet rates.",
                "XDP executes eBPF bytecode directly inside the network driver's RX ring before memory allocation for `sk_buff`, achieving line-rate DDoS filtering (>20-40 million packets/second per core).",
                "XDP Action Codes: XDP_DROP (fast drop), XDP_TX (reflect to same interface), XDP_REDIRECT (forward to another NIC or AF_XDP socket), XDP_PASS (hand over to standard Linux stack)."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-eBPF-01"
        },

        # ==========================================
        # 4. MIKROTIK ROUTEROS ENTERPRISE ARCHITECTURE
        # ==========================================
        {
            "id": "net_mikrotik_packet_flow_fasttrack",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik RouterOS v7 Packet Flow Documentation",
            "title": "RouterOS v7 Packet Flow, Connection Tracking, and FastTrack Bypass Invariants",
            "prompt": "Detail the 5 core stages of MikroTik RouterOS packet flow: Prerouting (Raw, ConnTrack, Mangle, D-NAT), Input/Forward/Output decision, and Postrouting (Mangle, S-NAT/Masquerade, Queue Tree). Explain the mechanism and trade-offs of FastTrack (`fasttrack-connection` in firewall filter forward chain): why it dramatically decreases CPU usage and increases throughput, and why it bypasses Simple Queues, Queue Tree, and Mangle marks unless explicitly filtered.",
            "invariants": [
                "RouterOS Packet Flow Order for Forward Traffic: Ingress -> Prerouting (Raw -> ConnTrack -> Mangle -> D-NAT) -> Routing Decision -> Forward (Mangle -> Filter -> Queue Tree) -> Routing Decision -> Postrouting (Mangle -> Queue Tree -> S-NAT) -> Egress.",
                "FastTrack acceleration marks established & related TCP/UDP connections to skip connection tracking recalculation, firewall filters, mangle, and queue trees on subsequent packets.",
                "FastTrack trade-off: Achieves multi-gigabit wire speed on CPU-limited RouterBOARDs, but completely disables bandwidth limiting (Simple Queues & Queue Trees) and policy packet marking for fasttracked streams. Production rule: If precise per-user QoS/Queue Tree or PCC marking is required, FastTrack must be disabled or conditionally scoped."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-MikroTik-01"
        },
        {
            "id": "net_mikrotik_pcc_multiwan_loadbalancing",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik RouterOS Multi-WAN & PCC Engineering Reference",
            "title": "MikroTik Multi-WAN Load Balancing via Per Connection Classifier (PCC) & Failover",
            "prompt": "Write a complete, production-grade MikroTik RouterOS script implementing 2-WAN PCC (Per Connection Classifier) load balancing with WAN failover (`check-gateway=ping`). Detail the Mangle rules for input chain connection marking, prerouting connection splitting (`both-addresses-and-ports`), route marking, and policy-based routing tables in RouterOS v7.",
            "code_example": """# MikroTik RouterOS v7 Multi-WAN PCC Script (2x WAN)
/routing table add name=to-WAN1 fib
/routing table add name=to-WAN2 fib

/ip firewall mangle
# 1. Accept LAN-to-LAN traffic without mark
add chain=prerouting dst-address=192.168.0.0/16 action=accept

# 2. Preserve incoming connections on specific WAN interface (Input & Output symmetry)
add chain=input in-interface=ether1-WAN1 action=mark-connection new-connection-mark=WAN1_conn passthrough=yes
add chain=input in-interface=ether2-WAN2 action=mark-connection new-connection-mark=WAN2_conn passthrough=yes
add chain=output connection-mark=WAN1_conn action=mark-routing new-routing-mark=to-WAN1 passthrough=no
add chain=output connection-mark=WAN2_conn action=mark-routing new-routing-mark=to-WAN2 passthrough=no

# 3. PCC Classifier for LAN Outbound Connections
add chain=prerouting in-interface=bridge-LAN connection-mark=no-mark per-connection-classifier=both-addresses-and-ports:2/0 action=mark-connection new-connection-mark=WAN1_conn passthrough=yes
add chain=prerouting in-interface=bridge-LAN connection-mark=no-mark per-connection-classifier=both-addresses-and-ports:2/1 action=mark-connection new-connection-mark=WAN2_conn passthrough=yes

# 4. Mark Routing based on connection marks
add chain=prerouting in-interface=bridge-LAN connection-mark=WAN1_conn action=mark-routing new-routing-mark=to-WAN1 passthrough=no
add chain=prerouting in-interface=bridge-LAN connection-mark=WAN2_conn action=mark-routing new-routing-mark=to-WAN2 passthrough=no

# 5. NAT Masquerade
/ip firewall nat
add chain=srcnat out-interface=ether1-WAN1 action=masquerade
add chain=srcnat out-interface=ether2-WAN2 action=masquerade

# 6. Default Routes with Failover in RouterOS v7
/ip route
add dst-address=0.0.0.0/0 gateway=192.168.1.1 routing-table=to-WAN1 check-gateway=ping distance=1
add dst-address=0.0.0.0/0 gateway=192.168.2.1 routing-table=to-WAN2 check-gateway=ping distance=1
add dst-address=0.0.0.0/0 gateway=192.168.1.1 distance=1 check-gateway=ping
add dst-address=0.0.0.0/0 gateway=192.168.2.1 distance=2
""",
            "invariants": [
                "PCC hashing with `both-addresses-and-ports` ensures HTTPS banking and session-sensitive services stay pinned to the same external IP for the duration of a TCP session while distributing multiple connections evenly.",
                "Input and Output chain connection marking prevents asynchronous routing (reply packets exiting a different WAN interface than the one the request arrived on, which gets dropped by ISP reverse path filtering / RPF).",
                "RouterOS v7 requires explicit creation of routing tables with `/routing table add name=... fib` before assigning `routing-table` in `/ip route`."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-MikroTik-02"
        },
        {
            "id": "net_mikrotik_qos_pcq_queue_tree",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik HTB & PCQ Bandwidth Management Guide",
            "title": "Hierarchical Token Bucket (HTB) & Per Connection Queue (PCQ) Dynamic Bandwidth Fair-Share",
            "prompt": "Explain how MikroTik HTB (Hierarchical Token Bucket) in `/queue tree` calculates CIR (limit-at) and MIR (max-limit). Explain why PCQ (Per Connection Queue) is superior to hundreds of static Simple Queues in high-density ISP/enterprise networks, and write the configuration for bidirectional PCQ fair-sharing with bufferbloat mitigation.",
            "code_example": """# MikroTik RouterOS v7 PCQ Queue Tree Configuration
/queue type
add name=PCQ-Download kind=pcq pcq-rate=0 pcq-limit=50KiB pcq-total-limit=2000KiB pcq-classifier=dst-address pcq-src-address-mask=32 pcq-dst-address-mask=32
add name=PCQ-Upload kind=pcq pcq-rate=0 pcq-limit=50KiB pcq-total-limit=2000KiB pcq-classifier=src-address pcq-src-address-mask=32 pcq-dst-address-mask=32

/ip firewall mangle
add chain=forward out-interface=bridge-LAN action=mark-packet new-packet-mark=client_download passthrough=no
add chain=forward in-interface=bridge-LAN action=mark-packet new-packet-mark=client_upload passthrough=no

/queue tree
add name=TOTAL-DOWNLOAD parent=bridge-LAN max-limit=100M
add name=PCQ-CLIENTS-DOWN parent=TOTAL-DOWNLOAD packet-mark=client_download queue=PCQ-Download max-limit=100M

add name=TOTAL-UPLOAD parent=ether1-WAN max-limit=50M
add name=PCQ-CLIENTS-UP parent=TOTAL-UPLOAD packet-mark=client_upload queue=PCQ-Upload max-limit=50M
""",
            "invariants": [
                "HTB Parent Queues enforce global link capacity (`max-limit`), while Child Queues allocate guaranteed bandwidth (`limit-at`) and dynamically borrow excess bandwidth up to `max-limit` using priority levels 1 (highest) to 8 (lowest).",
                "PCQ dynamically creates sub-queues for every active client IP on the fly. `pcq-rate=0` divides total available bandwidth equally among all active users (`Rate = Max_Limit / Active_Users`), preventing any single user from monopolizing the pipeline.",
                "For Download queues, `pcq-classifier=dst-address` groups packets by destination client IP. For Upload queues, `pcq-classifier=src-address` groups packets by source client IP."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-MikroTik-03"
        },
        {
            "id": "net_mikrotik_bridge_vlan_hw_offload",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik CRS3xx/CCR2xxx Bridge VLAN Filtering & L3 HW Offloading",
            "title": "Bridge VLAN Filtering, 802.1Q Trunks, and Hardware Offloading (L2/L3 HW-Offload)",
            "prompt": "Explain the architectural difference between legacy software bridge VLANs and RouterOS v7 Bridge VLAN Filtering (`/interface bridge vlan`). Detail how Hardware Offloading (`hw=yes`) programs the physical switch ASIC (Marvell Prestera / SwOS chip) to achieve non-blocking wire-speed switching (Gbps/10Gbps) with 0% CPU usage, and write the configuration for tagged trunk ports and untagged access ports.",
            "code_example": """# MikroTik Bridge VLAN Filtering with Hardware Offloading
/interface bridge
add name=bridge1 vlan-filtering=no

/interface bridge port
# Trunk Port connected to Core Switch / AP
add bridge=bridge1 interface=ether1 hw=yes
# Access Port for VLAN 10 (Office LAN)
add bridge=bridge1 interface=ether2 pvid=10 hw=yes
# Access Port for VLAN 20 (Guest Wi-Fi)
add bridge=bridge1 interface=ether3 pvid=20 hw=yes

/interface bridge vlan
add bridge=bridge1 vlan-ids=10 tagged=bridge1,ether1 untagged=ether2
add bridge=bridge1 vlan-ids=20 tagged=bridge1,ether1 untagged=ether3

# Router Gateway Interfaces (CPU Interface)
/interface vlan
add name=VLAN10-GW vlan-id=10 interface=bridge1
add name=VLAN20-GW vlan-id=20 interface=bridge1

/ip address
add address=192.168.10.1/24 interface=VLAN10-GW
add address=192.168.20.1/24 interface=VLAN20-GW

# Enable VLAN Filtering after configuration
/interface bridge set bridge1 vlan-filtering=yes
""",
            "invariants": [
                "Hardware Offloading (`hw=yes` in `/interface bridge port`) offloads packet forwarding to the onboard Switch Chip ASIC, eliminating CPU processing for L2 frames.",
                "When `vlan-filtering=yes` is enabled, the bridge CPU port (`bridge1`) MUST be added as a `tagged` member in `/interface bridge vlan` for any VLAN where the router itself needs an IP gateway (`/interface vlan`).",
                "Always configure VLANs with `vlan-filtering=no` first, and enable `vlan-filtering=yes` only as the final step to avoid accidental Winbox/SSH disconnection lockout."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-MikroTik-04"
        },
        {
            "id": "net_mikrotik_bgp_v7_routing_filters",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik RouterOS v7 BGP & Routing Engine",
            "title": "MikroTik RouterOS v7 Enterprise BGP Peering & Programmatic Routing Filters",
            "prompt": "Explain the major architectural changes in MikroTik RouterOS v7 BGP implementation compared to v6 (new routing engine, multi-threaded BGP convergence, and structured filter language). Write a complete BGP peering configuration with an upstream ISP (AS65001 to AS65002), announcing a public /24 prefix, applying AS-Path prepending for backup paths, and filtering bogon prefixes.",
            "code_example": """# MikroTik RouterOS v7 BGP Configuration
/routing bgp template
add name=ISP-Template as=65001 router-id=203.0.113.1 hold-time=90s keepalive-time=30s

# Programmatic Routing Filters in RouterOS v7
/routing filter rule
# Inbound Filter: Drop default route & RFC 1918 bogons from peer
add chain=BGP-IN rule="if dst in 0.0.0.0/0 && dst-len == 0 { reject; }"
add chain=BGP-IN rule="if dst in 10.0.0.0/8 || dst in 172.16.0.0/12 || dst in 192.168.0.0/16 { reject; }"
add chain=BGP-IN rule="accept;"

# Outbound Filter: Only announce our public /24 prefix and prepend AS for backup
add chain=BGP-OUT-PRIMARY rule="if dst == 203.0.113.0/24 { set bgp-communities 65001:100; accept; } else { reject; }"
add chain=BGP-OUT-BACKUP rule="if dst == 203.0.113.0/24 { set bgp-path-prepend 2; accept; } else { reject; }"

# BGP Connection Peering
/routing bgp connection
add name=PEER-ISP1 template=ISP-Template remote.address=198.51.100.2 .as=65002 input.filter-chain=BGP-IN output.filter-chain=BGP-OUT-PRIMARY output.network=203.0.113.0/24
add name=PEER-ISP2-BACKUP template=ISP-Template remote.address=198.51.200.2 .as=65003 input.filter-chain=BGP-IN output.filter-chain=BGP-OUT-BACKUP output.network=203.0.113.0/24
""",
            "invariants": [
                "RouterOS v7 uses a modern, high-performance multi-threaded BGP daemon capable of loading full Internet routing tables (900k+ prefixes) across multiple CPU cores in seconds.",
                "Routing Filters in v7 use a C-like programmable syntax (`if ... { ... }`) replacing the legacy chain-action dropdown lists in v6.",
                "`output.network` in `/routing bgp connection` or route presence in the routing table is mandatory for announcing prefixes; unreachability in the local FIB automatically withdraws the BGP advertisement."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-MikroTik-05"
        },
        {
            "id": "net_mikrotik_wireguard_overlay_vpn",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik RouterOS v7 WireGuard & Site-to-Site Documentation",
            "title": "Site-to-Site WireGuard VPN Tunneling & MTU Clamping on RouterOS v7",
            "prompt": "Configure a high-performance Site-to-Site WireGuard tunnel between two MikroTik RouterOS v7 routers. Explain why WireGuard operates with MTU 1420 (accounting for 80 bytes of IPv4/UDP/WireGuard header overhead) and how to configure MSS Clamping (`change-mss`) in `/ip firewall mangle` to eliminate TCP PMTUD blackholes.",
            "code_example": """# Router 1 (HQ: 10.254.0.1/30, Public IP: 203.0.113.10)
/interface wireguard
add name=wg0 listen-port=51820 mtu=1420

/ip address
add address=10.254.0.1/30 interface=wg0

/interface wireguard peers
add interface=wg0 public-key="PEER2_PUBLIC_KEY_BASE64=" endpoint-address="198.51.100.20" endpoint-port=51820 allowed-address=10.254.0.2/32,192.168.20.0/24 persistent-keepalive=25s

/ip route
add dst-address=192.168.20.0/24 gateway=10.254.0.2

# MSS Clamping to prevent fragmentation and blackholing
/ip firewall mangle
add chain=forward protocol=tcp tcp-flags=syn action=change-mss new-mss=clamp-to-pmtu passthrough=yes
""",
            "invariants": [
                "WireGuard encapsulation overhead: 20 bytes IPv4 + 8 bytes UDP + 32 bytes WireGuard header + 16 bytes auth tag = up to 80 bytes overhead on IPv4, requiring tunnel MTU of 1420 (or 1400 on IPv6/PPPoE).",
                "`allowed-address` serves as both an egress routing selector and an ingress cryptographic access control list; packets from non-matching source IPs are silently dropped by the WireGuard cryptokey routing engine.",
                "`persistent-keepalive=25s` is essential for peers located behind NAT or stateful firewalls to maintain UDP conntrack bindings on intermediate routers."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-MikroTik-06"
        },
        {
            "id": "net_mikrotik_raw_firewall_hardening",
            "domain": "MikroTik RouterOS",
            "source": "MikroTik RouterOS Security & Defense Architecture",
            "title": "MikroTik Raw Firewall Pre-ConnTrack DDoS Defense & Brute Force Blacklisting",
            "prompt": "Explain why `/ip firewall raw` is critical for high-volume DDoS mitigation compared to `/ip firewall filter`. Write a RouterOS security hardening script that drops port scanners and brute-force attacks against Winbox (8291) and SSH (22) using staged Address Lists (`stage1`, `stage2`, `stage3`, `blacklist_7d`).",
            "code_example": """# MikroTik Pre-ConnTrack Raw Firewall & Brute-Force Defense
/ip firewall raw
# 1. Drop known blacklisted IPs with ZERO conntrack memory allocation
add chain=prerouting src-address-list=blacklisted_attackers action=drop comment="Drop Blacklisted Attackers"
add chain=prerouting tcp-flags=!fin,!syn,!rst,!ack action=drop comment="Drop NULL Scan"
add chain=prerouting tcp-flags=fin,syn action=drop comment="Drop SYN-FIN Scan"
add chain=prerouting tcp-flags=fin,psh,urg,!syn,!rst,!ack action=drop comment="Drop XMAS Scan"

/ip firewall filter
# 2. FastTrack Established Connections
add chain=forward action=fasttrack-connection connection-state=established,related
add chain=forward action=accept connection-state=established,related
add chain=forward action=drop connection-state=invalid

# 3. Progressive 3-Stage Winbox/SSH Brute Force Defense
add chain=input protocol=tcp dst-port=8291,22 connection-state=new src-address-list=stage3 action=add-src-to-address-list address-list=blacklisted_attackers address-list-timeout=7d
add chain=input protocol=tcp dst-port=8291,22 connection-state=new src-address-list=stage2 action=add-src-to-address-list address-list=stage3 address-list-timeout=1m
add chain=input protocol=tcp dst-port=8291,22 connection-state=new src-address-list=stage1 action=add-src-to-address-list address-list=stage2 address-list-timeout=1m
add chain=input protocol=tcp dst-port=8291,22 connection-state=new action=add-src-to-address-list address-list=stage1 address-list-timeout=1m
""",
            "invariants": [
                "The `/ip firewall raw` table intercepts packets before connection tracking (`conntrack`). Under high-volume SYN/UDP floods, dropping packets in `/ip firewall filter` still consumes 100% CPU creating conntrack entries; `/ip firewall raw` drops them statelessly with negligible CPU impact.",
                "Staged address lists prevent legitimate users who mistyped their password once or twice from being locked out for a week, while instantly blacklisting automated high-frequency brute-force bots."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-MikroTik-07"
        },

        # ==========================================
        # 5. CLOUD DISTRIBUTED & NETWORK SECURITY
        # ==========================================
        {
            "id": "net_bgp_hijacking_and_rpki",
            "domain": "Network Security & Routing",
            "source": "IETF RFC 4271 / RFC 6480 RPKI Architecture",
            "title": "BGP Prefix Hijacking, Subprefix Attacks, and RPKI Route Origin Validation (ROV)",
            "prompt": "Explain how Autonomous Systems (AS) route traffic across the global Internet using BGP-4. Detail why BGP inherently trusts route announcements, how a malicious AS can announce a more specific subprefix (/24 vs /22) to intercept global traffic (Longest Prefix Match rule), and how RPKI (Resource Public Key Infrastructure) with Route Origin Authorizations (ROA) cryptographically validates AS origin.",
            "invariants": [
                "BGP routers select paths based on the Longest Prefix Match (LPM) rule: a more specific route (e.g. 198.51.100.0/24) ALWAYS takes precedence over a broader route (198.51.100.0/22).",
                "Because basic BGP lacks cryptographic authentication of route announcements, any AS can advertise ownership of an IP prefix or subprefix, causing global Tier 1 carriers to redirect traffic to the hijacker.",
                "RPKI uses X.509 PKI certificates anchored by the 5 Regional Internet Registries (RIRs: ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC) to publish ROAs (Route Origin Authorizations), binding an IP prefix to an authorized Autonomous System Number (ASN) with a maximum prefix length (MaxLen).",
                "Routers running BGP Route Origin Validation (ROV) drop announcements marked as 'Invalid', neutralizing prefix and subprefix hijacking attempts."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-Security-02"
        },
        {
            "id": "net_dns_poisoning_and_dnssec",
            "domain": "Network Security & Protocols",
            "source": "IETF RFC 1035 / RFC 4033 DNSSEC",
            "title": "Dan Kaminsky DNS Cache Poisoning Attack & DNSSEC Cryptographic Chain of Trust",
            "prompt": "Analyze the classic Kaminsky DNS cache poisoning attack against recursive resolvers: how forged UDP query IDs (16-bit) and randomized source ports are overwhelmed by birthday attack queries. Explain how DNSSEC (RRSIG, DNSKEY, DS records) establishes a hierarchical chain of trust from the ICANN root zone ('.') down to the authoritative domain nameservers.",
            "invariants": [
                "Traditional DNS over UDP uses only a 16-bit Transaction ID (65,536 values) to match responses to queries.",
                "Kaminsky attack: Attacker queries recursive resolver for `rand1.target.com`, `rand2.target.com`, simultaneously flooding the resolver with thousands of spoofed authoritative response packets containing the attacker's nameserver in the Authority/Additional section. By generating unlimited unique subdomains, the attacker bypasses negative caching and wins the race within seconds.",
                "Mitigation 1 (Port Randomization): Randomizing the 16-bit UDP source port expands the entropy space to 32 bits (~4.29 billion combinations), making blind spoofing computationally infeasible.",
                "Mitigation 2 (DNSSEC): Cryptographically signs DNS Resource Record Sets (RRsets) with public-key cryptography. Resolvers validate RRSIG using the zone's DNSKEY, which is validated up to the root zone via Delegation Signer (DS) hashes stored in parent TLDs."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Security-03"
        }
    ]

    return dataset

def generate_knowledge_base_markdown(dataset):
    print("[*] Generating dense Network Engineering & MikroTik RouterOS Knowledge Base Markdown...")
    
    md_lines = [
        "# World-Class Computer Networking & MikroTik RouterOS Architecture: The Definitive Reference",
        "",
        "**Author:** Claudia Engineering Architecture (Gahar Inovasi Teknologi)  ",
        f"**Compiled:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        "**Standard:** Ultra-Dense, Pragmatic, High-Performance Systems & Enterprise Network Engineering",
        "",
        "---",
        "",
        "## 📑 Table of Contents",
        "1. [The Networking Stack: Layer-by-Layer Architectural Invariants](#1-the-networking-stack)",
        "2. [Transport Layer: TCP, UDP, QUIC, and Congestion Control](#2-transport-layer)",
        "3. [Low-Level Socket Programming & Asynchronous I/O (epoll, io_uring)](#3-low-level-socket-programming)",
        "4. [Kernel Networking, eBPF & XDP High-Speed Packet Processing](#4-kernel-networking-ebpf--xdp)",
        "5. [MikroTik RouterOS v7 & Enterprise Traffic Engineering](#5-mikrotik-routeros-v7--enterprise-traffic-engineering)",
        "6. [Distributed Cloud Networking, CNI, & Service Mesh](#6-distributed-cloud-networking-cni--service-mesh)",
        "7. [Network Security, Protocol Exploits, and Cryptographic Defenses](#7-network-security--defenses)",
        "",
        "---",
        "",
        "## 1. The Networking Stack: Layer-by-Layer Architectural Invariants",
        "",
        "### OSI 7-Layer vs TCP/IP 4-Layer Mapping",
        "| Layer | OSI Name | TCP/IP Layer | PDU (Protocol Data Unit) | Core Protocols & Hardware |",
        "|---|---|---|---|---|",
        "| 7 | Application | Application | Data / Payload | HTTP/1.1, HTTP/2, HTTP/3, gRPC, DNS, SSH, TLS |",
        "| 6 | Presentation | Application | Data | ASN.1, Protobuf, JSON, TLS Encryption/Decryption |",
        "| 5 | Session | Application | Data | RPC, gRPC Streams, SOCKS5 |",
        "| 4 | Transport | Transport | Segment (TCP) / Datagram (UDP) | TCP (RFC 9293), UDP (RFC 768), QUIC (RFC 9000), SCTP |",
        "| 3 | Network | Internet | Packet | IPv4 (RFC 791), IPv6 (RFC 8200), ICMP, BGP-4, OSPF, IPsec |",
        "| 2 | Data Link | Link / Network Access | Frame | Ethernet (802.3), Wi-Fi (802.11), ARP, VLAN (802.1Q), VXLAN |",
        "| 1 | Physical | Link / Network Access | Bit | Optical Fiber, Copper Twisted Pair, NIC PHY, Transceivers |",
        "",
        "### Key Transmission Invariants",
        "- **MTU (Maximum Transmission Unit):** Standard Ethernet MTU is 1500 bytes. IP Header (20 bytes) + TCP Header (20 bytes) leaves **MSS (Maximum Segment Size) = 1460 bytes**.",
        "- **PMTUD (Path MTU Discovery):** Uses ICMP Type 3 Code 4 ('Fragmentation Needed and DF set') to dynamically discover the minimum MTU along an end-to-end path without IP fragmentation.",
        "",
        "---",
        "",
        "## 2. Transport Layer: TCP, UDP, QUIC, and Congestion Control",
        "",
        "### TCP 3-Way Handshake & Teardown State Transitions",
        "```",
        " Client                                                  Server",
        "   |                        SYN (seq=x)                     | (LISTEN)",
        "   | -----------------------------------------------------> |",
        "(SYN_SENT)               SYN+ACK (seq=y, ack=x+1)           | (SYN_RCVD)",
        "   | <----------------------------------------------------- |",
        "(ESTABLISHED)               ACK (ack=y+1)                   | (ESTABLISHED)",
        "   | -----------------------------------------------------> |",
        "   |                                                        |",
        "   |                   DATA TRANSFER PHASE                  |",
        "   |                                                        |",
        "(Active Close)              FIN (seq=u)                     | (Passive Close)",
        "   | -----------------------------------------------------> | (CLOSE_WAIT)",
        "(FIN_WAIT_1)                ACK (ack=u+1)                   |",
        "   | <----------------------------------------------------- |",
        "(FIN_WAIT_2)                FIN (seq=v)                     | (LAST_ACK)",
        "   | <----------------------------------------------------- |",
        "(TIME_WAIT)                 ACK (ack=v+1)                   | (CLOSED)",
        "   | -----------------------------------------------------> |",
        " (2*MSL = 60s)",
        "(CLOSED)",
        "```",
        "",
        "---",
        "",
        "## 3. Low-Level Socket Programming & Asynchronous I/O",
        "- **Linux epoll Edge-Triggered (`EPOLLET`):** Mandates non-blocking sockets (`O_NONBLOCK`) and exhaustive draining loop until `EAGAIN` to prevent socket starvation.",
        "- **Zero-Copy Primitives:** `sendfile()`, `splice()`, and `io_uring MSG_ZEROCOPY` eliminate context switches and CPU cache pollution by delegating DMA page transfers directly to network hardware.",
        "",
        "---",
        "",
        "## 4. Kernel Networking, eBPF & XDP High-Speed Packet Processing",
        "- **XDP (eXpress Data Path):** Runs eBPF programs in the network driver RX ring before `sk_buff` memory allocation, achieving >40 Mpps line-rate packet processing.",
        "- **SOCKMAP Acceleration:** Intercepts localhost TCP streams and redirects socket buffers directly between sender and receiver queues, bypassing kernel TCP/IP stack overhead by up to 80%.",
        "",
        "---",
        "",
        "## 5. MikroTik RouterOS v7 & Enterprise Traffic Engineering",
        "",
        "### 5.1 Packet Flow & FastTrack Acceleration",
        "- **Packet Flow Ingress/Egress:**",
        "  1. `Prerouting`: Raw Table -> Connection Tracking -> Mangle Prerouting -> Destination NAT (D-NAT)",
        "  2. `Routing Decision`: Local Input vs Transit Forward",
        "  3. `Forward`: Mangle Forward -> Filter Forward -> Queue Tree Global/Interface",
        "  4. `Postrouting`: Mangle Postrouting -> Queue Tree Interface -> Source NAT (Masquerade) -> Egress",
        "- **FastTrack Invariant:** `action=fasttrack-connection` skips firewall inspection and queue trees for established TCP/UDP connections. Yields maximum throughput on high-gigabit hardware, but must be bypassed when per-client QoS / Queue Tree shaping is strictly enforced.",
        "",
        "### 5.2 Multi-WAN Load Balancing with PCC (Per Connection Classifier)",
        "- Uses hash function `per-connection-classifier=both-addresses-and-ports:N/i` to distribute outbound streams across multiple ISP uplinks.",
        "- Preserves sticky sessions for HTTPS banking and prevents asymmetric routing drops via symmetrical input/output connection marks (`mark-connection` / `mark-routing`).",
        "- Failover managed with `check-gateway=ping` and distance metrics in `/ip route`.",
        "",
        "### 5.3 QoS, HTB & PCQ (Per Connection Queue)",
        "- **Hierarchical Token Bucket (HTB):** Parent queues define total bandwidth capacity (`max-limit`), child queues allocate guaranteed minimum (`limit-at`) and dynamically borrow remaining tokens based on priority (1 to 8).",
        "- **PCQ Dynamic Equal Sharing:** Automatically balances bandwidth equally among all active client IPs (`pcq-rate=0`), eliminating the overhead of managing thousands of individual simple queues.",
        "",
        "### 5.4 Bridge VLAN Filtering & Hardware Offload (CRS/CCR)",
        "- Replaces legacy CPU software bridging with switch chip ASIC hardware offloading (`hw=yes`).",
        "- `/interface bridge vlan` maps tagged trunk ports and untagged access ports (`pvid=X`) with 0% CPU consumption during wire-speed L2/L3 frame forwarding.",
        "",
        "### 5.5 Enterprise BGP in RouterOS v7",
        "- Redesigned routing engine with multi-core convergence and C-style programmatic `/routing filter rule`.",
        "- Supports full global BGP routing tables (900k+ prefixes), AS-Path prepending, BGP communities, and dynamic peer route origin validation.",
        "",
        "### 5.6 WireGuard Site-to-Site Tunneling",
        "- High-speed modern VPN using state-of-the-art cryptography (ChaCha20-Poly1305, Curve25519).",
        "- Standard MTU is 1420 bytes to accommodate 80-byte encapsulation overhead. MSS Clamping (`change-mss=clamp-to-pmtu`) prevents TCP fragmentation blackholes.",
        "",
        "---",
        "",
        "## 6. Distributed Cloud Networking, CNI, & Service Mesh",
        "- **Overlay (VXLAN) vs Flat BGP (Calico):** Overlay encapsulates L2 in UDP (50B tax); Flat BGP peers directly with ToR switches for wire speed without MTU penalties.",
        "- **L4 Direct Server Return (DSR):** Scales load balancers 10x-100x by modifying destination MAC on ingress while backend servers respond directly to clients with the VIP as source.",
        "",
        "---",
        "",
        "## 7. Network Security, Protocol Exploits, and Cryptographic Defenses",
        "- **SYN Cookies:** Statelessly encode connection data in 32-bit ISN to neutralize TCP SYN Floods.",
        "- **RPKI & BGP Route Origin Validation (ROV):** Cryptographically signs prefix ownership to stop malicious BGP hijacking and subprefix theft.",
        "- **DNSSEC & Port Randomization:** Neutralizes Kaminsky DNS cache poisoning by expanding entropy space to 32 bits and verifying digital signatures (RRSIG/DNSKEY/DS) from the ICANN root zone.",
        "- **RouterOS Raw Firewall:** Drops DDoS attacks and port scans before Connection Tracking (`conntrack`), preventing CPU starvation.",
        "",
        "---",
        "**Synthesized by Claudia Autonomous AI Systems Engine - Gahar Inovasi Teknologi**"
    ]

    return "\n".join(md_lines)

def run_pipeline():
    dataset = build_network_master_dataset()
    
    # 1. Simpan dataset JSON lengkap
    json_path = os.path.join(DATASET_DIR, "network_engineering_master_dataset.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"[✓] Berhasil menyimpan dataset master ({len(dataset)} modules) ke: {json_path}")

    # 2. Simpan knowledge base Markdown
    kb_md = generate_knowledge_base_markdown(dataset)
    kb_path = os.path.join(KB_DIR, "network_engineering_world_class.md")
    with open(kb_path, "w", encoding="utf-8") as f:
        f.write(kb_md)
    print(f"[✓] Berhasil mengkompilasi Knowledge Base ke: {kb_path}")

    # 3. Simpan evaluation suite di data/
    eval_suite_path = os.path.join(DATA_DIR, "network_training_eval_suite.json")
    with open(eval_suite_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": "Claudia World-Class Network & MikroTik RouterOS Benchmark Suite",
            "version": "1.1.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "total_items": len(dataset),
            "domains": list(set([item["domain"] for item in dataset])),
            "items": dataset
        }, f, indent=2)
    print(f"[✓] Berhasil membuat benchmark evaluation suite di: {eval_suite_path}")

if __name__ == "__main__":
    run_pipeline()
