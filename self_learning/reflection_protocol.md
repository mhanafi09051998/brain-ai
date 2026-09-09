# Protokol Mode Refleksi (Autonomous Reflexion Protocol)

Dokumen ini mendefinisikan aturan kerja operasional **Mode Refleksi** (Reflexion Mode) untuk asisten Claudia dan framework multi-agent. Protokol ini mengatur bagaimana sistem mengeksekusi refleksi diri verbal secara terstruktur saat menghadapi kegagalan eksekusi, regresi, atau ketidakefisienan logika.

---

## 1. Fondasi Teoretis: Reflexion Loop

Mode Refleksi mengadopsi arsitektur *Verbal Reinforcement Learning* (Shinn et al.):

```
   ┌────────────────────────────────────────────────────────┐
   │                                                        │
   ▼                                                        │
┌──────────────┐     ┌──────────────┐     ┌─────────────┴──────┐
│  PERFORM     │ ──▶ │  EVALUATE    │ ──▶ │  VERBAL REFLECT    │
│  (Eksekusi   │     │  (Deteksi    │     │  (Diagnosis Kausal │
│   Aksi/Kode) │     │   Kegagalan) │     │   & Heuristik Baru)│
└──────────────┘     └──────────────┘     └────────────────────┘
                                                     │
                                                     ▼
                                          ┌────────────────────┐
                                          │  EPISODIC MEMORY   │
                                          │ (In-Context Prompt)│
                                          └────────────────────┘
```

Alih-alih mengulangi aksi yang sama secara membabi buta (*trial-and-error tanpa memori*), sistem **wajib berhenti sejenak** untuk merumuskan refleksi verbal sebelum melakukan percobaan berikutnya.

---

## 2. Rubrik 4 Kuadran Refleksi Diri (4-Quadrant Reflection Rubric)

Setiap catatan refleksi wajib memuat 4 elemen analisis kausal:

1. **Target Nyata (*Intended Goal*)**: Apa perilaku atau output yang sebenarnya ingin dicapai?
2. **Kondisi Aktual (*Actual Outcome & Trace*)**: Apa output aktual yang didapat atau pesan error spesifik apa yang muncul?
3. **Akar Permasalahan (*Root Cause Diagnosis*)**: Mengapa logika saat ini gagal? Asumsi keliru apa yang dibuat pada percobaan sebelumnya?
4. **Kebijakan Korektif (*Actionable Corrective Heuristic*)**: Aturan atau modifikasi spesifik apa yang WAJIB diterapkan pada percobaan selanjutnya untuk menjamin keberhasilan?

---

## 3. Pemicu Aktivasi Mode Refleksi (Trigger Conditions)

Mode Refleksi otomatis aktif ketika salah satu kondisi berikut terpenuhi:
1. **Kegagalan Pengujian**: Terjadi Assertion Error, Exception, atau penurunan *pass rate* pada kode baru.
2. **Pelanggaran Toleransi Target**: Latensi eksekusi melebihi batas yang ditentukan (misal > 2x lipat baseline).
3. **Ambiguasi / Kesalahan Kompilasi**: Terjadi syntax error, type mismatch, atau respon tidak valid dari external API.
4. **Deteksi Regresi**: Fitur yang sebelumnya berjalan normal menjadi rusak setelah refactoring.

---

## 4. Persistensi & Injeksi Konteks Refleksi (In-Context Prompt Injection)

1. Hasil refleksi disimpan ke basis data memori episodik persisten di [`self_learning/knowledge_base/reflections.json`](file:///C:/Users/Win10/Music/train/self_learning/knowledge_base/reflections.json).
2. Pada percobaan berikutnya, refleksi dari kegagalan sebelumnya **disuntikkan ke dalam konteks eksekutor** sebagai peringatan (*negative constraint & corrective guide*).
