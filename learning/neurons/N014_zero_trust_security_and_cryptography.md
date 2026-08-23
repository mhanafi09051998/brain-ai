# Neuron N014: Zero-Trust Security, Cryptography & Threat Modeling

Standar pertahanan keamanan tingkat militer untuk infrastruktur dan aplikasi:

---

## 1. Modern Cryptography & Token Architecture
- **PASETO (Platform-Agnostic Security Tokens) vs JWT**: Mencegah celah manipulasi algoritma token (*"none" algorithm attack*).
- **Constant-Time Comparison**: Mencegah serangan kebocoran waktu (*Timing Attacks*) saat memvalidasi hash password/kunci API.
- **mTLS (Mutual TLS)**: Enkripsi dan autentikasi dua arah antar microservices dan node internal.

---

## 2. Threat Modeling & Runtime Protection
- **STRIDE & DREAD Matrix**: Analisis ancaman komprehensif pada setiap trust boundary dan endpoint API.
- **eBPF Security Probing**: Pengawasan aktivitas syscall kernel Linux secara langsung tanpa overhead untuk mendeteksi anomali/intrusi secara realtime.
