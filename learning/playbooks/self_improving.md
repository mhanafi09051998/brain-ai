# Playbook: Self-Improving Mechanism

Alur evaluasi dan peningkatan performa otomatis Claudia di setiap siklus kerja.

```text
[Task Execution] ──► [Feedback / Error Detection] ──► [Log in feedback_log/]
                                                             │
[Next Task Optimization] ◄── [Update Rules / Memory] ◄───────┘
```

---

## 4 Langkah Siklus Self-Improving

1. **Capture (Deteksi & Pencatatan)**
   - Setiap ada koreksi dari user, kegagalan build/test, atau pola kerja baru: catat langsung ringkasannya ke [`learning/feedback_log/`](file:///D:/Agent_Claudia_Autonomus/learning/feedback_log/).

2. **Distill (Ekstraksi Pola)**
   - Jika kesalahan atau pola berulang ≥ 2 kali: jadikan aturan baku di [`learning/knowledge_base/`](file:///D:/Agent_Claudia_Autonomus/learning/knowledge_base/) atau playbook di [`learning/playbooks/`](file:///D:/Agent_Claudia_Autonomus/learning/playbooks/).
   - Update rule workspace (`AGENTS.md` / `GEMINI.md`) jika berdampak pada seluruh sesi.

3. **Reflect & Sync (Agregasi & Pembersihan)**
   - Jalankan refleksi berkala dengan `python -m graphify reflect` untuk mengagregasi sinyal memori.
   - Update [`memory.md`](file:///D:/Agent_Claudia_Autonomus/memory.md) dengan state terbaru dan bersihkan konteks yang sudah tidak relevan (pruning).

4. **Apply (Eksekusi Minim)**
   - Terapkan hasil pembelajaran langsung pada prompt/tugas berikutnya tanpa perlu diingatkan ulang.
