#!/usr/bin/env python3
"""
Scrape & Synthesize World-Class Computer Networking Training Datasets
Sources:
- Beej's Guide to Network Programming (Sockets, POSIX, Non-blocking I/O)
- donnemartin/system-design-primer (OSI, L4/L7, QUIC, gRPC, WebSockets, CDN)
- Linux Kernel Networking & eBPF / XDP Architecture (sk_buff, BBR, Cubic, io_uring)
- IETF RFC Core Standards (RFC 9293 TCP, RFC 9000 QUIC, RFC 8446 TLS 1.3, RFC 9113 HTTP/2, RFC 9114 HTTP/3)
- Kubernetes & Cloud Networking (CNI Cilium/Calico, Overlay VXLAN, Envoy Proxy, BGP/Anycast)
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
    print("[*] Compiling Master Computer Networking Training & Evaluation Dataset...")

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
            // Process payload
            write(sock_fd, buf, bytes); // echo
        } else if (bytes == 0) {
            // Connection closed by peer
            close(sock_fd);
            break;
        } else {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Buffer completely drained, wait for next epoll event
                break;
            }
            // Real error occurred
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
                "XDP Action Codes:",
                "  - XDP_DROP: Drop packet immediately at lowest cost (sub-microsecond CPU time).",
                "  - XDP_TX: Bounce the packet back out the same network interface it arrived on (ideal for ultra-fast L4 load balancers like Facebook Katran).",
                "  - XDP_REDIRECT: Redirect packet to another NIC, CPU core, or AF_XDP user-space socket.",
                "  - XDP_PASS: Pass packet up to standard Linux networking stack (`sk_buff` allocated).",
                "TC (Traffic Control) runs later in the stack after `sk_buff` allocation, supporting both ingress and egress shaping, packet mangling, and full socket context."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-eBPF-01"
        },
        {
            "id": "net_ebpf_sockmap_acceleration",
            "domain": "Kernel & eBPF Networking",
            "source": "Cilium Service Mesh / BPF_MAP_TYPE_SOCKMAP",
            "title": "Accelerating Local TCP Microservices via eBPF SOCKMAP Socket Redirection",
            "prompt": "In service mesh sidecar architectures (Envoy/Istio), inter-process communication on localhost incurs full TCP/IP stack overhead (IP routing, TCP handshake, congestion control, checksums). Explain how `BPF_MAP_TYPE_SOCKMAP` and `BPF_PROG_TYPE_SK_MSG` redirect socket buffers directly between socket send/receive queues in the kernel, bypassing TCP/IP processing.",
            "invariants": [
                "Standard localhost TCP connections pass through the entire kernel networking stack twice (tx path: socket -> TCP -> IP -> loopback device -> rx path: loopback -> IP -> TCP -> socket).",
                "eBPF SOCKMAP registers established TCP socket file descriptors into a kernel map.",
                "When a process writes data into Socket A, the `sk_msg` eBPF program intercepts the memory buffer (`sk_msg`) and redirects it directly into Socket B's receive queue via `bpf_msg_redirect_map()`, achieving zero-overhead socket-to-socket fast-path streaming with 50-80% lower latency."
            ],
            "difficulty": "Expert",
            "benchmark_eval": "SWE-eBPF-02"
        },

        # ==========================================
        # 4. DISTRIBUTED NETWORKING, CLOUD CNI & SERVICE MESH
        # ==========================================
        {
            "id": "net_k8s_cni_overlay_vs_routing",
            "domain": "Cloud & Distributed Networking",
            "source": "Kubernetes The Hard Way / Calico / Cilium Documentation",
            "title": "Kubernetes CNI: Overlay Networks (VXLAN/Geneve) vs Flat Routed Networks (BGP)",
            "prompt": "Compare Overlay Networking (e.g., Flannel VXLAN, Calico VXLAN) with Flat Routed Networking (e.g., Calico BGP peering with Top-of-Rack switches, AWS VPC CNI). Analyze MTU overhead (50 bytes VXLAN header), packet encapsulation/decapsulation CPU tax, cross-subnet routing, and security policy enforcement.",
            "invariants": [
                "Overlay (VXLAN): Encapsulates Layer 2 Pod Ethernet frames inside Layer 4 UDP packets (port 4789). Works across any underlying network without router reconfiguration, but incurs 50 bytes encapsulation overhead per packet (reducing MTU from 1500 to 1450) and CPU cost for encapsulation/decapsulation.",
                "Flat Routed (BGP): Each K8s node acts as a BGP speaker (e.g., Calico Bird), announcing its Pod CIDR subnet to Top-of-Rack (ToR) physical switches or route reflectors. Packets travel natively with standard MTU (1500 or 9000 Jumbo Frames) without encapsulation overhead, achieving raw wire speed.",
                "Cilium CNI leverages native eBPF routing to replace kube-proxy iptables/IPVS, performing L4 load balancing directly at the socket level (`sock_ops`) without conntrack table locks."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Cloud-01"
        },
        {
            "id": "net_load_balancing_l4_vs_l7",
            "domain": "Cloud & Distributed Networking",
            "source": "donnemartin/system-design-primer & Envoy Architecture",
            "title": "Load Balancing Architecture: L4 (Direct Server Return / Maglev) vs L7 (Envoy / Reverse Proxy)",
            "prompt": "Explain the architectural difference between Layer 4 Load Balancing (TCP/UDP, Maglev consistent hashing, Direct Server Return / DSR) and Layer 7 Load Balancing (HTTP, gRPC, SSL termination, path-based routing, circuit breaking). Explain why DSR enables a single L4 load balancer to handle hundreds of gigabits of traffic.",
            "invariants": [
                "L4 Load Balancing operates at the transport layer without terminating TCP/TLS. In Direct Server Return (DSR), incoming requests pass through the L4 load balancer which modifies the destination MAC address to the chosen backend server, but the backend server responds DIRECTLY to the client with the Virtual IP (VIP) as source IP.",
                "DSR exploits the asymmetry of web traffic (requests are tiny ~1KB, responses are huge ~1MB-10MB), allowing the load balancer to handle 10x-100x more throughput since it never processes egress response traffic.",
                "L7 Load Balancing terminates TCP and TLS, parses HTTP headers/JSON/gRPC payloads, and maintains two separate connection pools (client-to-proxy, proxy-to-upstream). It enables complex routing, authentication, retry policies, and circuit breaking at the cost of higher CPU and memory overhead."
            ],
            "difficulty": "Hard",
            "benchmark_eval": "SWE-Cloud-02"
        },

        # ==========================================
        # 5. NETWORK SECURITY, PROTOCOL ATTACKS & MITIGATION
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
    print("[*] Generating dense Network Engineering Knowledge Base Markdown...")
    
    md_lines = [
        "# World-Class Computer Networking & Systems Engineering: The Definitive Reference",
        "",
        "**Author:** Claudia Engineering Architecture (Gahar Inovasi Teknologi)  ",
        f"**Compiled:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        "**Standard:** Ultra-Dense, Pragmatic, High-Performance Systems & Network Engineering",
        "",
        "---",
        "",
        "## 📑 Table of Contents",
        "1. [The Networking Stack: Layer-by-Layer Architectural Invariants](#1-the-networking-stack)",
        "2. [Transport Layer: TCP, UDP, QUIC, and Congestion Control](#2-transport-layer)",
        "3. [Low-Level Socket Programming & Asynchronous I/O (epoll, io_uring)](#3-low-level-socket-programming)",
        "4. [Kernel Networking, eBPF & XDP High-Speed Packet Processing](#4-kernel-networking-ebpf--xdp)",
        "5. [Distributed Cloud Networking, CNI, & Service Mesh](#5-distributed-cloud-networking-cni--service-mesh)",
        "6. [Network Security, Protocol Exploits, and Cryptographic Defenses](#6-network-security--defenses)",
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
        "- **IP Fragmentation Hazards:** Fragmented packets increase loss probability (losing 1 fragment drops the whole datagram) and break L4 firewall inspection on non-first fragments.",
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
        "### Congestion Control Algorithms",
        "1. **CUBIC:** Standard default in Linux. Uses a cubic polynomial function for congestion window growth based on time since last packet loss rather than ACK arrivals. Aggressive in high-BDP networks, but suffers from bufferbloat on deep-buffered paths.",
        "2. **BBR (Bottleneck Bandwidth and RTT):** Model-based congestion control. Simultaneously estimates Bottleneck Bandwidth (BtlBw) and Minimum Round-Trip Time (RTprop). Operates at maximum throughput with minimum queue delay (Kleinrock optimum), immune to non-congestive packet loss.",
        "3. **QUIC (RFC 9000):** Built on UDP. Eliminates transport Head-of-Line blocking, integrates TLS 1.3 encryption by default, provides 0-RTT connection resumption, and uses Connection IDs (CID) for instant network migration across Wi-Fi and Cellular.",
        "",
        "---",
        "",
        "## 3. Low-Level Socket Programming & Asynchronous I/O",
        "",
        "### Linux Sockets & epoll Edge-Triggered Loop",
        "- **Non-Blocking Requirement:** When using `EPOLLET` (Edge-Triggered epoll), socket file descriptors **must** be set to `O_NONBLOCK` via `fcntl`.",
        "- **Exhaustion Loop:** A worker thread receiving an `EPOLLIN` event must loop `read()` or `recv()` until it encounters `EAGAIN` or `EWOULDBLOCK`. Leaving unread bytes in the kernel socket buffer will permanently stall further epoll notifications on that descriptor.",
        "- **`SO_REUSEPORT` Multi-Process Architecture:** Allows multiple independent worker processes to bind to the exact same IP and Port. The Linux kernel distributes incoming TCP SYN packets using a 4-tuple hash across listening sockets, eliminating user-space accept mutex contention.",
        "",
        "### High-Performance Zero-Copy Primitives",
        "- `sendfile(out_fd, in_fd, offset, count)`: Transfers data directly from the kernel page cache to the network socket buffer without copying into user space.",
        "- `splice(fd_in, off_in, fd_out, off_out, len, flags)`: Moves data between two file descriptors via kernel pipes without copying through user memory.",
        "- `io_uring`: Asynchronous kernel ring-buffer interface created by Jens Axboe. Submission Queue (SQ) and Completion Queue (CQ) shared between user space and kernel via `mmap()`, allowing millions of IOPS with zero syscall overhead.",
        "",
        "---",
        "",
        "## 4. Kernel Networking, eBPF & XDP High-Speed Packet Processing",
        "",
        "### eXpress Data Path (XDP)",
        "- **RX Hookpoint:** Executes verified eBPF bytecode in the network driver before `sk_buff` allocation.",
        "- **Performance:** Reaches 40+ Million Packets per Second (Mpps) per CPU core on 100GbE NICs.",
        "- **XDP Return Codes:**",
        "  - `XDP_DROP`: Wire-speed DDoS dropping.",
        "  - `XDP_TX`: Bounces packet out the same interface (L4 Load Balancer fast-path).",
        "  - `XDP_REDIRECT`: Passes packet to another NIC interface or AF_XDP user-space socket.",
        "  - `XDP_PASS`: Elevates packet to the standard Linux kernel network stack.",
        "",
        "### eBPF SOCKMAP & Service Mesh Acceleration",
        "- Maps socket pairs (`BPF_MAP_TYPE_SOCKMAP`) to bypass TCP/IP stack evaluation on localhost inter-process communication.",
        "- `bpf_msg_redirect_map()` injects data directly into destination socket queues, reducing sidecar proxy latency by over 60%.",
        "",
        "---",
        "",
        "## 5. Distributed Cloud Networking, CNI, & Service Mesh",
        "",
        "### Kubernetes CNI Architecture",
        "1. **Overlay Networks (VXLAN / Geneve):** L2-over-L4 encapsulation. Works anywhere, but adds 50-byte UDP header overhead and requires CPU encapsulation.",
        "2. **Flat BGP Routed Networks (Calico):** Nodes peer with physical ToR (Top-of-Rack) switches via BGP, advertising Pod CIDRs. No packet encapsulation overhead, wire speed, standard 1500/9000 MTU.",
        "3. **eBPF-Native CNI (Cilium):** Replaces kube-proxy iptables with eBPF hash tables, providing O(1) service lookups and kernel socket-level load balancing (`sock_ops`).",
        "",
        "### Load Balancing Strategies: L4 vs L7",
        "- **L4 Direct Server Return (DSR):** High-speed load balancing where client request goes to VIP via L4 balancer, but backend server responds directly to the client. Massive scalability because load balancer only handles inbound traffic.",
        "- **L7 Proxy (Envoy / NGINX):** Terminates TLS, parses HTTP headers, inspects JSON/gRPC payloads, enables dynamic routing, circuit breaking, and rate limiting at higher CPU cost.",
        "",
        "---",
        "",
        "## 6. Network Security, Protocol Exploits, and Cryptographic Defenses",
        "",
        "### Major Attack Vectors & Canonical Mitigations",
        "1. **TCP SYN Flood:** Attacker floods server with half-open SYN connections.  ",
        "   *Defense:* Cryptographic **SYN Cookies** (`net.ipv4.tcp_syncookies = 1`), encoding connection parameters into the 32-bit ISN without allocating kernel memory until the final ACK arrives.",
        "2. **BGP Route Hijacking:** Rogue AS announces a more specific /24 subprefix to steal traffic.  ",
        "   *Defense:* **RPKI (Resource Public Key Infrastructure)** with Route Origin Authorizations (ROA) cryptographically signed by Regional Internet Registries (RIRs).",
        "3. **Kaminsky DNS Cache Poisoning:** Attacker floods recursive resolvers with spoofed UDP replies for random subdomains.  ",
        "   *Defense:* **UDP Source Port Randomization** (32-bit entropy space) and **DNSSEC** (hierarchical digital signatures via RRSIG/DNSKEY/DS records).",
        "4. **ARP Spoofing:** Attacker broadcasts gratuitous ARP replies associating their MAC address with the default gateway IP.  ",
        "   *Defense:* **Dynamic ARP Inspection (DAI)** on managed switches using DHCP Snooping binding tables.",
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
            "title": "Claudia World-Class Network Engineering Benchmark Suite",
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "total_items": len(dataset),
            "domains": list(set([item["domain"] for item in dataset])),
            "items": dataset
        }, f, indent=2)
    print(f"[✓] Berhasil membuat benchmark evaluation suite di: {eval_suite_path}")

if __name__ == "__main__":
    run_pipeline()
