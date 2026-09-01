---
name: api-gateway-reverse-proxy
description: High-precision engineering reference for API Gateway and Reverse Proxy architectures, multi-tenant path/subdomain routing, WebSocket/SSE streaming pipelines, circuit breakers, jittered retries, request deduplication, distributed timeouts, and header security invariants.
---

# API Gateway & High-Performance Reverse Proxy Engineering

An API Gateway / Reverse Proxy is the single ingress control plane for distributed systems. It enforces zero-trust security boundaries, decouples clients from upstream microservice topologies, manages traffic shaping, guarantees real-time stream passthrough, and prevents cascading system failures.

---

## 1. Gateway Routing Architectures & Proxy Pipeline

### A. Reverse Proxy Pipeline Lifecycle
Every incoming byte traversing a gateway must follow an explicit, deterministic pipeline:

```
[ Downstream Client ]
         |
         v
+-------------------------------------------------------------------------+
| INGRESS & TRANSPORT LAYER                                               |
| - TLS Termination (SNI routing, ALPN negotiation HTTP/1.1 vs HTTP/2)    |
| - Connection Limiting & TCP Backlog Management                          |
+-------------------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------------------+
| SECURITY & NORMALIZATION LAYER                                          |
| - Request Smuggling Prevention (RFC 7230 / RFC 9112 TE/CL validation)   |
| - Hop-by-Hop Header Stripping (`Connection`, `Keep-Alive`, etc.)         |
| - Client IP Extraction (`X-Forwarded-For` from Trusted CIDRs only)      |
| - Ingress Header Sanitization (Purge untrusted `X-Internal-*`, `X-User`)|
+-------------------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------------------+
| TRAFFIC SHAPING & IDENTITY LAYER                                        |
| - Global / IP / Tenant Rate Limiting (Token Bucket / Sliding Window)    |
| - Authentication Token Verification (JWT verify, OAuth2 Introspection)  |
| - Identity Context Enrichment (`X-User-ID`, `X-Tenant-ID`, `X-Roles`)   |
+-------------------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------------------+
| ROUTING & DISPATCH ENGINE                                               |
| - Subdomain / Host Match -> Path Prefix Match -> Route Rewrite          |
| - Upstream Cluster Selection & Load Balancing (Least-Conn / IP Hash)   |
+-------------------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------------------+
| RESILIENCY & FORWARDING LAYER                                           |
| - Circuit Breaker Inspection (Closed / Open / Half-Open)                |
| - Request Deduplication (Singleflight in-flight collapsing)             |
| - Distributed Deadline / Timeout Propagation (`X-Request-Deadline`)     |
| - Full Jitter Exponential Retry Policy (Idempotent requests only)       |
+-------------------------------------------------------------------------+
         |
         v
[ Upstream Microservice / Cluster ]
```

---

### B. Multi-Tenant Path-Based Routing & Path Rewriting

Path-based routing maps URI namespaces to distinct backend clusters while stripping or transforming tenant-specific prefixes before forwarding.

#### 1. Prefix Stripping Invariant
When routing `/api/v1/tenant-alpha/payments/charge` to the payment service, the gateway must strip `/api/v1/tenant-alpha` so the upstream service receives `/payments/charge`, while forwarding tenant metadata via normalized headers.

#### 2. Regex vs Trie-Based Prefix Matching
- **Static & Prefix Matching**: Use Radix Tree / Trie structures for $O(K)$ lookup time (where $K$ is path length), independent of total route count $N$.
- **Trailing Slash Normalization**: Ensure strict canonicalization: `/api/v1/users/` and `/api/v1/users` must map to the same upstream route without triggering open-redirect vulnerabilities.

#### NGINX Path Rewrite Pattern:
```nginx
# Explicit prefix match with regex boundary protection
location ~ ^/api/v1/(?<tenant>[a-zA-Z0-9_-]+)/orders(?<rest>/.*)?$ {
    # Block path traversal attempts
    if ($rest ~ "\.\.") {
        return 400 '{"error":"Malformed path traversal"}';
    }

    # Inject tenant context into request header
    proxy_set_header X-Tenant-ID $tenant;
    
    # Forward sanitized remaining path
    proxy_pass http://order_service_upstream$rest$is_args$args;
}
```

---

### C. Dynamic Subdomain & Wildcard Host Routing

Subdomain routing isolates tenants or services at the DNS / Host level (e.g., `alpha.platform.io`, `api.platform.io`).

#### 1. SNI (Server Name Indication) & TLS Handshake Invariants
- Clients send the target hostname in the TLS ClientHello `server_name` extension.
- Gateway performs TLS termination using dynamic certificate loading (SNI dispatch via automated ACME cert storage or Wildcard SAN certificate `*.platform.io`).

#### 2. Host Header Extraction & Security
- The raw `Host` header must be validated against an allowed host whitelist or regex pattern to prevent HTTP Host Header Injection and cache poisoning.
- The downstream host must be preserved for upstream virtual hosting via `X-Forwarded-Host: $host`.

#### NGINX Subdomain Dynamic Resolution Pattern:
```nginx
# Wildcard Subdomain Mapping to Dynamic Upstream Resolver
server {
    listen 443 ssl http2;
    server_name ~^(?<subdomain>[a-zA-Z0-9-]+)\.platform\.io$;

    ssl_certificate /etc/letsencrypt/live/platform.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/platform.io/privkey.pem;

    # Internal DNS resolver with aggressive caching
    resolver 10.0.0.2 valid=10s ipv6=off;
    set $target_backend "backend-${subdomain}.internal.local:8080";

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Tenant-Subdomain $subdomain;

        proxy_pass http://$target_backend;
    }
}
```

---

### D. Upstream Load Balancing Strategies & Health Checks

| Strategy | Algorithm Mechanics | Failure Mode / Trade-off | Ideal Use Case |
| :--- | :--- | :--- | :--- |
| **Round-Robin** | Sequential circular distribution across active nodes. | Ignores backend request execution duration; can overload slow instances. | Homogeneous stateless services with uniform execution time. |
| **Weighted Least Connections** | Routes to node with minimum active TCP connections ($C_i / W_i$). | Slight memory overhead tracking connection counters; rapid connection churn can cause oscillation. | Long-running queries, heavy computation, dynamic payload sizes. |
| **Consistent Hashing / IP Hash** | Hashes client IP or session key to a ring (e.g., Ketama, MurmurHash3). | Node addition/removal causes $K/N$ key remapping; hot tenant causes node saturation. | In-memory session affinity, local LRU cache locality, WebSockets. |
| **Random with Two Choices (Power of 2)** | Picks two nodes randomly and selects the one with fewer active connections. | Marginally suboptimal compared to absolute global minimum. | Massive scale distributed gateways where global state synchronization is impossible. |

#### Health Check Invariants:
1. **Passive Health Checks**: Monitor live traffic responses. If a node returns $E$ consecutive 5xx errors within window $W$, mark `DOWN` for duration $D$.
2. **Active Health Checks**: Out-of-band synthetic HTTP probes to `/healthz` or `/livez` every $T$ seconds. Node marked healthy only after $S$ consecutive successes.
3. **Flapping Dampening**: Exponentially increase cooldown time for instances that frequently oscillate between healthy and unhealthy.

---

## 2. Real-Time Streaming, Server-Sent Events (SSE) & WebSockets

### A. WebSocket Upgrade Invariants & State Transition

WebSockets initiate as standard HTTP/1.1 requests and transition into full-duplex raw TCP byte streams.

#### 1. Upgrade Handshake Protocol (RFC 6455)
- **Client Request**:
  ```http
  GET /ws/v1/feed HTTP/1.1
  Host: api.platform.io
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
  Sec-WebSocket-Version: 13
  ```
- **Gateway Validation & Upstream Forwarding**:
  Gateway must preserve and forward `Upgrade` and `Connection` headers to upstream.
- **Upstream Response**:
  ```http
  HTTP/1.1 101 Switching Protocols
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
  ```
- **Socket Piping**: Upon receiving `101 Switching Protocols`, the proxy transforms the connection into an opaque bidirectional TCP tunnel.

#### 2. Timeout & Heartbeat Invariants
- Default HTTP read/write timeouts (e.g. 60 seconds) will sever idle WebSockets.
- Set proxy timeouts to 24 hours (`86400s`) or disable idle timeouts, while enforcing application-level Ping/Pong frames every 30s.

```nginx
# WebSocket Upstream Map Invariant
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

upstream ws_backend {
    server 127.0.0.1:4001;
    server 127.0.0.1:4002;
    keepalive 64;
}

server {
    listen 443 ssl;
    server_name ws.platform.io;

    location /socket.io/ {
        proxy_pass http://ws_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;

        # Disable buffering and extend timeouts for long-lived TCP tunnel
        proxy_buffering off;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

### B. Hot Module Replacement (HMR) & Dev Passthrough

Next.js Turbopack and Vite utilize dedicated WebSocket channels for Hot Module Replacement (HMR) and Fast Refresh (e.g., `/_next/webpack-hmr` or Vite WS at port `24678` / `/@vite/client`).

#### Invariants for HMR Reverse Proxying:
1. **HTTP/1.1 Requirement**: HTTP/2 does not support the HTTP/1.1 `Upgrade` mechanism natively. Proxies must speak HTTP/1.1 to the dev server.
2. **Buffer Bypass**: Buffer accumulation completely blocks streaming diff chunks.
3. **Dedicated Location Block**: Separate standard static assets from websocket HMR endpoints to avoid applying aggressive production caching to dev streams.

```nginx
# Next.js / Vite HMR Passthrough Configuration
location /_next/webpack-hmr {
    proxy_pass http://127.0.0.1:3000/_next/webpack-hmr;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400s;
    proxy_buffering off;
}
```

---

### C. Server-Sent Events (SSE) & Chunked Transfer Invariants

Server-Sent Events (SSE) provide a unidirectional, continuous HTTP response stream (`text/event-stream`). Improper proxy buffering breaks real-time delivery, causing events to buffer until the connection terminates or buffer reaches 4KB–64KB.

#### Critical Invariants for SSE Delivery:
1. **`X-Accel-Buffering: no`**: Sent by upstream or set by NGINX to immediately disable proxy response caching and buffer queues.
2. **`Cache-Control: no-cache, no-transform`**: Prevents intermediate proxies from compressing (gzip/brotli buffering) or caching chunks.
3. **`Content-Type: text/event-stream`**: Mandatory MIME type.
4. **`Connection: keep-alive`**: Keeps the persistent HTTP channel open.
5. **Immediate TCP Flush**: Proxies must transmit TCP packets immediately (`tcp_nodelay on`).

```nginx
# SSE Zero-Buffering Proxy Location
location /api/v1/stream/ {
    proxy_pass http://ai_inference_cluster;
    proxy_http_version 1.1;
    proxy_set_header Connection "";

    # Critical SSE Invariants
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header X-Accel-Buffering "no";
    chunked_transfer_encoding on;
    tcp_nodelay on;

    # Keep stream open during token generation gaps
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

---

## 3. Resiliency, Fault Tolerance & Traffic Control

### A. Circuit Breaker State Machine

The Circuit Breaker pattern isolates degraded upstream services to prevent cascading latency exhaustion and thread pool starvation across the gateway.

```
       +-------------------------+
       |                         |
       |         CLOSED          |  <-- Normal operations (requests pass through)
       |   (Tracking Failures)   |
       |                         |
       +-------------------------+
         |                     ^
         | Failure Rate >= T   | Success Rate >= S
         v                     |
       +-------------------------+
       |                         |
       |          OPEN           |  <-- Fast fail (Instant 503 Return)
       |     (Zero Traffic)      |
       |                         |
       +-------------------------+
         |
         | Sleep Window (Timeout elapsed)
         v
       +-------------------------+
       |                         |
       |        HALF-OPEN        |  <-- Canary Probe (Allows 1 trial request)
       |     (Canary Probe)      |
       |                         |
       +-------------------------+
         |
         +--> Failed Probe -> Return to OPEN
```

#### Circuit Breaker Invariants:
1. **Sliding Window Error Rate**:
   $$\text{Error Rate} = \frac{\sum \text{Failures in Window } W}{\text{Total Requests in Window } W}$$
   Trigger state transition to `OPEN` if $\text{Error Rate} \ge 50\%$ with minimum volume $N \ge 20$.
2. **Fast Failure**: When `OPEN`, the gateway returns HTTP `503 Service Unavailable` with `Retry-After: <cooldown_seconds>` header immediately ($< 1\text{ms}$) without touching the network.
3. **Canary Probing (HALF-OPEN)**: After cooldown period (e.g. 10 seconds), permit exactly 1 request (or $M$ requests). If successful, transition to `CLOSED`; if it fails, reset to `OPEN` with exponential cooldown.

---

### B. Exponential Backoff with Full Jitter & Idempotency Rules

#### 1. Mathematical Formulation (AWS Full Jitter Algorithm)
Simple exponential backoff leads to synchronized retry spikes (Thundering Herd). Full Jitter randomizes the sleep interval across the entire backoff spectrum:

$$t_{\text{sleep}} = \text{random}(0, \; \min(M, \; B \cdot 2^i))$$

- $B$: Base interval (e.g., $100\text{ms}$)
- $i$: Consecutive retry attempt index ($0, 1, 2, \dots$)
- $M$: Maximum backoff ceiling (e.g., $5000\text{ms}$)
- $\text{random}(0, x)$: Uniform random floating-point value in $[0, x]$

#### 2. Retry Safety & HTTP Invariants
- **NEVER retry non-idempotent HTTP methods (`POST`, `PATCH`, `CONNECT`)** unless accompanied by an `Idempotency-Key` verified by the gateway or explicitly configured.
- **Permissible Retry Methods**: `GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`.
- **Permissible Status Codes for Retry**: `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`, `429 Too Many Requests` (respecting `Retry-After`).
- **Forbidden Status Codes for Retry**: `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error` (application state bugs cannot be solved by instant network retries).

---

### C. Request Deduplication & Singleflight Invariant

When multiple concurrent downstream clients request the same expensive, un-cached resource (Cache Stampede / Thundering Herd), the gateway must coalesce in-flight requests.

#### Singleflight Mechanics:
1. Client A requests `GET /api/v1/catalog/trending`.
2. Gateway calculates Request Signature: $\text{Hash}(\text{Method} + \text{URI} + \text{AuthTenant})$.
3. Gateway registers in-flight promise for this key.
4. Clients B, C, D request identical signature within $50\text{ms}$.
5. Gateway blocks B, C, D and binds them to Client A's in-flight execution promise.
6. When Upstream responds, Gateway broadcasts identical response body and headers to A, B, C, and D simultaneously.
7. Total Upstream load: **1 request instead of 4**.

---

### D. Distributed Timeouts & End-to-End Deadline Propagation

A static timeout at the gateway does not prevent wasted upstream processing if the client disconnects or if an upstream call chain consumes the entire latency budget.

```
[ Client ] 
    | (Deadline: 1000ms)
    v
[ Gateway ] ------------------------> [ Auth Service ] (Consumed: 200ms)
    | (Remaining Budget: 750ms)
    v
[ Order Service ] ------------------> [ Payment Service ] (Consumed: 600ms)
    | (Remaining Budget: 100ms)
    v
[ Inventory Service ] (Requires 300ms -> Abort immediately with 504)
```

#### Deadline Propagation Invariants:
1. **Ingress Deadline Stamp**: Gateway injects `X-Request-Deadline: <epoch_ms>` or `X-Request-Timeout: <remaining_ms>`.
2. **Context Budget Consumption**: Each upstream service deducts its processing time before dispatching sub-requests.
3. **Eager Termination**: If remaining budget $\le 0\text{ms}$ or client severs TCP connection (`Client Disconnect`), immediately terminate upstream HTTP requests using HTTP/2 `RST_STREAM` or closing the connection to save CPU/DB cycles.

---

## 4. Header Propagation, Trust Boundaries & Security Invariants

### A. Client IP Resolution & `X-Forwarded-*` Spoofing Defense

Clients can forge arbitrary headers (`X-Forwarded-For: 1.1.1.1`, `X-Real-IP: 8.8.8.8`). Allowing unvalidated ingress headers destroys rate limiting and IP-based access controls.

#### Trust Invariant Rules:
1. **Direct Socket Connection**: The only cryptographically and network-verified IP address is the direct TCP socket remote address ($IP_{\text{socket}}$).
2. **Trusted Proxy Chain Evaluation**:
   - If the gateway sits behind a CDN/Load Balancer (e.g., Cloudflare, AWS ALB), verify that $IP_{\text{socket}} \in \text{Trusted\_CIDR\_List}$.
   - Only if $IP_{\text{socket}}$ matches a trusted CIDR, parse `X-Forwarded-For` from **Right to Left**, selecting the first untrusted IP address.
3. **Untrusted Client Ingress**: If the gateway is directly exposed to public traffic, **COMPLETELY OVERWRITE** `X-Forwarded-For` with `$remote_addr`. Do not append to client-supplied values.

#### NGINX Trusted Proxy Resolution:
```nginx
# Real IP Resolution from Cloudflare / Trusted Load Balancers
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 10.0.0.0/8;        # Internal VPC ALB CIDR

# Use header provided by trusted upstream
real_ip_header CF-Connecting-IP;    # Or X-Forwarded-For
real_ip_recursive on;

# Standardized propagation to downstream microservices
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Port $server_port;
```

---

### B. Header Sanitization & Internal Identity Injection

Attackers frequently attempt privilege escalation by passing internal headers directly from external clients (e.g., `X-User-ID: admin`, `X-Is-Superadmin: true`).

#### Ingress Sanitization Standard:
1. **Strip Internal Headers**: Gateway must strip **ALL** internal identity and routing headers on ingress before executing auth middleware:
   - `X-User-ID`, `X-User-Email`, `X-User-Roles`
   - `X-Tenant-ID`, `X-Organization-ID`
   - `X-Internal-Token`, `X-Caller-Service`
2. **Cryptographic Validation**: Verify JWT or API key at the gateway layer.
3. **Re-Inject Validated Context**: Gateway mints and injects verified values into request headers before forwarding upstream:
   ```
   Client Headers: { Authorization: "Bearer <token>", X-User-ID: "999" }
                           |
                           v  (Gateway purges X-User-ID, verifies JWT claims)
   Upstream Headers: { X-User-ID: "42", X-Tenant-ID: "corp-1", X-Roles: "user" }
   ```

---

### C. Hop-by-Hop Header Stripping (RFC 7230 / RFC 9112)

Hop-by-hop headers are meaningful only for a single transport-level connection and must **never** be forwarded by a proxy across upstream connections.

#### Standard Hop-by-Hop Headers (Must be removed):
- `Connection`
- `Keep-Alive`
- `Proxy-Authenticate`
- `Proxy-Authorization`
- `TE` (Trailers Encoding)
- `Trailer`
- `Transfer-Encoding`
- `Upgrade` (Unless performing explicit WebSocket upgrade handshake)

#### Dynamic Connection Header Stripping Rule:
Any header name listed inside the value of the incoming `Connection` header is also deemed hop-by-hop and must be stripped:
```
Incoming: Connection: close, X-Custom-Token
Action:   Strip both 'Connection' AND 'X-Custom-Token' before upstream forwarding.
```

---

### D. HTTP Request Smuggling Mitigation (TE.CL / CL.TE Desync)

Request smuggling occurs when frontend gateways and backend servers disagree on request boundaries due to conflicting `Transfer-Encoding` (TE) and `Content-Length` (CL) headers.

#### Gateway Defense Invariants:
1. **Strict Rejection of Ambiguous Requests**: If a request contains both `Transfer-Encoding` and `Content-Length`, the gateway must reject it immediately with `400 Bad Request` (RFC 7230 §3.3.3 / RFC 9112 §6.1).
2. **Normalize to Chunked or Fixed Length**: When proxying to HTTP/1.1 upstreams, rewrite all request bodies into a single canonical framing format.
3. **Enforce HTTP/2 or HTTP/3 on Ingress**: HTTP/2 uses binary framing with explicit length fields (`DATA` frame payload length), making boundary ambiguity impossible at the transport layer.
4. **Strip Malformed Chunk Extensions**: Drop requests containing illegal whitespace or control characters (`\r\n\t`) in chunk length fields.

---

## 5. Production Reference Implementations

### A. Production Hardened NGINX API Gateway (`nginx.conf`)

```nginx
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;
pid /var/run/nginx.pid;

events {
    worker_connections 16384;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Performance & Socket Invariants
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    server_tokens off;
    keepalive_timeout 65;
    keepalive_requests 1000;

    # Buffer Limits (Anti-DDoS / Memory exhaustion)
    client_body_buffer_size 128k;
    client_max_body_size 20M;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;

    # Rate Limiting Zones (Token Bucket / Leaky Bucket)
    limit_req_zone $binary_remote_addr zone=ip_limit:20m rate=50r/s;
    limit_req_zone $http_authorization zone=auth_limit:20m rate=100r/s;
    limit_conn_zone $binary_remote_addr zone=addr_conn_limit:20m;

    # Real IP Resolution from Cloudflare
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    real_ip_header CF-Connecting-IP;
    real_ip_recursive on;

    # WebSocket Connection Upgrade Mapping
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    # Upstream Pools with Connection Keepalive
    upstream core_api_cluster {
        least_conn;
        server 10.0.1.10:8080 max_fails=3 fail_timeout=10s;
        server 10.0.1.11:8080 max_fails=3 fail_timeout=10s;
        server 10.0.1.12:8080 backup;
        keepalive 128;
    }

    upstream sse_stream_cluster {
        ip_hash;
        server 10.0.2.10:9000;
        server 10.0.2.11:9000;
        keepalive 64;
    }

    # Ingress Gateway Server
    server {
        listen 443 ssl http2;
        server_name api.platform.io;

        ssl_certificate /etc/ssl/certs/api.platform.io.crt;
        ssl_certificate_key /etc/ssl/private/api.platform.io.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_session_cache shared:SSL:50m;
        ssl_session_timeout 1d;

        # Security Headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

        # Strict Request Smuggling Invariant Check
        if ($http_transfer_encoding ~* "chunked") {
            set $te_present "1";
        }
        if ($http_content_length != "") {
            set $cl_present "1";
        }
        set $smuggle_check "${te_present}${cl_present}";
        if ($smuggle_check = "11") {
            return 400 '{"error":"Ambiguous framing (TE + CL rejected)"}';
        }

        # 1. Standard REST API Route
        location /api/v1/ {
            limit_req zone=ip_limit burst=20 nodelay;
            limit_conn addr_conn_limit 50;

            # Strip Client Untrusted Ingress Headers
            proxy_set_header X-User-ID "";
            proxy_set_header X-Tenant-ID "";
            proxy_set_header X-Internal-Roles "";

            # Standardized Forwarding Headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Request-ID $request_id;

            # Upstream HTTP/1.1 Keepalive Connection
            proxy_http_version 1.1;
            proxy_set_header Connection "";

            # Timeouts
            proxy_connect_timeout 3s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;

            # Upstream Retry Invariant (Safe methods only)
            proxy_next_upstream error timeout http_502 http_503 http_504 non_idempotent;
            proxy_next_upstream_tries 2;

            proxy_pass http://core_api_cluster;
        }

        # 2. SSE Streaming Route (Zero Buffering)
        location /api/v1/events/ {
            proxy_pass http://sse_stream_cluster;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # Disable all proxy buffering & caching
            proxy_buffering off;
            proxy_cache off;
            proxy_set_header X-Accel-Buffering "no";
            chunked_transfer_encoding on;
            tcp_nodelay on;

            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
        }

        # 3. WebSocket Upgrade Route
        location /ws/ {
            proxy_pass http://core_api_cluster;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            proxy_buffering off;
            proxy_read_timeout 86400s;
            proxy_send_timeout 86400s;
        }
    }
}
```

---

### B. High-Precision Node.js / TypeScript Gateway Resiliency Pipeline

Complete, zero-dependency production pattern implementing **Singleflight Request Deduplication**, **Circuit Breaker State Machine**, and **Full Jitter Retries**:

```typescript
import http, { IncomingMessage, ServerResponse, RequestOptions } from 'node:http';
import { randomUUID } from 'node:crypto';

// --- 1. TYPES & INVARIANTS ---
interface CircuitBreakerConfig {
  failureThreshold: number;   // Failure rate percentage (e.g. 50)
  minRequests: number;        // Minimum requests to evaluate
  slidingWindowMs: number;    // Window duration
  cooldownPeriodMs: number;   // Sleep time before Half-Open probe
}

enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

// --- 2. CIRCUIT BREAKER IMPLEMENTATION ---
export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failures: number[] = [];
  private successes: number[] = [];
  private nextAttempt: number = Date.now();

  constructor(private readonly config: CircuitBreakerConfig) {}

  public allowRequest(): boolean {
    const now = Date.now();
    this.pruneOldMetrics(now);

    if (this.state === CircuitState.OPEN) {
      if (now >= this.nextAttempt) {
        this.state = CircuitState.HALF_OPEN;
        return true; // Canary probe permitted
      }
      return false; // Fast fail
    }
    return true;
  }

  public recordSuccess(): void {
    const now = Date.now();
    this.successes.push(now);
    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.CLOSED;
      this.failures = [];
    }
  }

  public recordFailure(): void {
    const now = Date.now();
    this.failures.push(now);

    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
      this.nextAttempt = now + this.config.cooldownPeriodMs;
      return;
    }

    const total = this.failures.length + this.successes.length;
    if (total >= this.config.minRequests) {
      const errorRate = (this.failures.length / total) * 100;
      if (errorRate >= this.config.failureThreshold) {
        this.state = CircuitState.OPEN;
        this.nextAttempt = now + this.config.cooldownPeriodMs;
      }
    }
  }

  public getState(): CircuitState {
    return this.state;
  }

  private pruneOldMetrics(now: number): void {
    const cutoff = now - this.config.slidingWindowMs;
    this.failures = this.failures.filter((t) => t > cutoff);
    this.successes = this.successes.filter((t) => t > cutoff);
  }
}

// --- 3. SINGLEFLIGHT IN-FLIGHT DEDUPLICATION ---
export class Singleflight {
  private inFlight = new Map<string, Promise<{ statusCode: number; headers: http.IncomingHttpHeaders; body: Buffer }>>();

  public async do(
    key: string,
    fn: () => Promise<{ statusCode: number; headers: http.IncomingHttpHeaders; body: Buffer }>
  ): Promise<{ statusCode: number; headers: http.IncomingHttpHeaders; body: Buffer }> {
    const existing = this.inFlight.get(key);
    if (existing) {
      return existing; // Share in-flight upstream execution
    }

    const promise = fn().finally(() => {
      this.inFlight.delete(key);
    });

    this.inFlight.set(key, promise);
    return promise;
  }
}

// --- 4. EXPONENTIAL BACKOFF WITH FULL JITTER ---
export async function sleepFullJitter(attempt: number, baseMs = 100, maxMs = 3000): Promise<void> {
  const exponential = Math.min(maxMs, baseMs * Math.pow(2, attempt));
  const jitteredSleep = Math.random() * exponential;
  return new Promise((resolve) => setTimeout(resolve, jitteredSleep));
}

// --- 5. REVERSE PROXY PIPELINE DISPATCHER ---
export class ResilientProxyDispatcher {
  private breaker = new CircuitBreaker({
    failureThreshold: 50,
    minRequests: 10,
    slidingWindowMs: 30000,
    cooldownPeriodMs: 10000
  });
  private singleflight = new Singleflight();

  public async forwardRequest(req: IncomingMessage, res: ServerResponse, upstreamPort: number): Promise<void> {
    const requestId = (req.headers['x-request-id'] as string) || randomUUID();
    const isIdempotent = ['GET', 'HEAD', 'OPTIONS'].includes(req.method || '');

    // 1. Check Circuit Breaker
    if (!this.breaker.allowRequest()) {
      res.writeHead(503, {
        'Content-Type': 'application/json',
        'Retry-After': '10',
        'X-Circuit-State': 'OPEN'
      });
      res.end(JSON.stringify({ error: 'Upstream cluster circuit open (Fast fail)' }));
      return;
    }

    // 2. Build Ingress Deduplication Key (Idempotent GETs only)
    const dedupKey = isIdempotent ? `${req.method}:${req.url}:${req.headers.authorization || ''}` : null;

    const executeForward = async () => {
      let lastError: Error | null = null;
      const maxRetries = isIdempotent ? 2 : 0;

      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        if (attempt > 0) {
          await sleepFullJitter(attempt);
        }

        try {
          const response = await this.dispatchUpstream(req, upstreamPort, requestId);
          if (response.statusCode >= 502 && response.statusCode <= 504) {
            throw new Error(`Upstream transient failure: ${response.statusCode}`);
          }
          this.breaker.recordSuccess();
          return response;
        } catch (err: any) {
          lastError = err;
          this.breaker.recordFailure();
        }
      }
      throw lastError;
    };

    try {
      const upstreamResult = dedupKey
        ? await this.singleflight.do(dedupKey, executeForward)
        : await executeForward();

      // Forward response to client
      res.writeHead(upstreamResult.statusCode, {
        ...upstreamResult.headers,
        'X-Request-ID': requestId
      });
      res.end(upstreamResult.body);
    } catch (err: any) {
      res.writeHead(504, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Gateway timeout / Upstream unavailable', details: err.message }));
    }
  }

  private dispatchUpstream(
    req: IncomingMessage,
    port: number,
    requestId: string
  ): Promise<{ statusCode: number; headers: http.IncomingHttpHeaders; body: Buffer }> {
    return new Promise((resolve, reject) => {
      // Strip dangerous hop-by-hop & client identity spoofing headers
      const sanitizedHeaders: http.OutgoingHttpHeaders = {
        ...req.headers,
        'x-forwarded-for': req.socket.remoteAddress,
        'x-forwarded-proto': 'http',
        'x-request-id': requestId
      };
      delete sanitizedHeaders['x-user-id'];
      delete sanitizedHeaders['x-tenant-id'];
      delete sanitizedHeaders['connection'];
      delete sanitizedHeaders['keep-alive'];

      const options: RequestOptions = {
        hostname: '127.0.0.1',
        port: port,
        path: req.url,
        method: req.method,
        headers: sanitizedHeaders,
        timeout: 5000 // 5-second strict upstream deadline
      };

      const proxyReq = http.request(options, (proxyRes) => {
        const chunks: Buffer[] = [];
        proxyRes.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
        proxyRes.on('end', () => {
          resolve({
            statusCode: proxyRes.statusCode || 500,
            headers: proxyRes.headers,
            body: Buffer.concat(chunks)
          });
        });
      });

      proxyReq.on('timeout', () => {
        proxyReq.destroy(new Error('Upstream socket timeout'));
      });

      proxyReq.on('error', (err) => {
        reject(err);
      });

      // Stream incoming body for POST/PUT
      req.pipe(proxyReq);
    });
  }
}
```

---

## 6. Operational Diagnostics & Anti-Patterns Checklist

### Critical Ingress Anti-Patterns (NEVER DO):
- ❌ **Trusting Unfiltered Ingress `X-Forwarded-For`**: Allows remote attackers to spoof their IP, bypassing rate limits, geo-blocks, and IP allowlists.
- ❌ **Retrying Non-Idempotent POST Requests on Gateway Timeout**: Causes duplicate credit card charges, duplicate order creation, and unrecoverable database state divergence.
- ❌ **Enabling Proxy Buffering or Response Compression on SSE/LLM Token Streams**: Stalls Server-Sent Events until the entire completion finishes, breaking streaming user experiences.
- ❌ **Using HTTP/2 Cleartext (H2C) to Upstreams Without Strict Boundary Checks**: Invites request smuggling and protocol confusion attacks.
- ❌ **Permitting Both `Content-Length` and `Transfer-Encoding`**: Leaves gateway vulnerable to TE.CL / CL.TE Request Smuggling.
- ❌ **Infinite Upstream Socket Timeouts on Standard REST**: Stalls gateway worker processes indefinitely during upstream resource deadlocks.

### Verification Runbook & Commands:
```bash
# 1. Verify SSE Zero-Buffering & Immediate Chunk Delivery (No Delay)
curl -N -i -H "Accept: text/event-stream" https://api.platform.io/api/v1/events/stream

# 2. Test WebSocket Handshake Upgrade via cURL
curl -i -N \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Host: api.platform.io" \
     -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     -H "Sec-WebSocket-Version: 13" \
     https://api.platform.io/ws/

# 3. Verify Ambiguous TE/CL Smuggling Rejection (Must return 400 Bad Request)
printf "POST /api/v1/test HTTP/1.1\r\nHost: api.platform.io\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\n" | nc api.platform.io 80

# 4. Inspect Upstream Response Headers for Buffer Disablement
curl -I https://api.platform.io/api/v1/events/
# Expect: X-Accel-Buffering: no
# Expect: Content-Type: text/event-stream
```
