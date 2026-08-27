<!-- converted from Panduan Struktur Prompt AI.docx -->

PANDUAN STRUKTUR PROMPT AI
Format Baku dan Panduan Komponen Prompt Sederhana hingga Kompleks
1. TABEL 7 ELEMEN DASAR PROMPT AI
2. POLA / TEMPLATE BAKU PROMPT

CONTOH PENERAPAN DASAR (SEDERHANA)
Kasus Sehari-hari yang Mudah Dipahami dan Dipraktikkan
3. CONTOH KASUS SEDERHANA 1: MEMBUAT PESAN WHATSAPP PENGINGAT RAPAT
4. CONTOH KASUS SEDERHANA 2: MERAPIKAN CATATAN TUGAS MENJADI DAFTAR PRIORITAS

CONTOH PENERAPAN TINGKAT LANJUT (KOMPLEKS)
Kasus Multi-Kriteria, Analisis Teknis, Kepatuhan Regulasi & Mitigasi Risiko
5. CONTOH KASUS KOMPLEKS: EVALUASI MULTI-VENDOR MIGRASI CLOUD & ANALISIS RISIKO SLA
| No | Elemen | Fungsi & Definisi | Cara Pengisian |
| --- | --- | --- | --- |
| 1 | Konteks | Situasi kerja, latar belakang, dan tujuan spesifik yang ingin dicapai. | Jelaskan situasi riil, batasan domain, dan target output yang dibutuhkan. |
| 2 | Peran | Persona, tingkat keahlian, atau sudut pandang profesional yang ditugaskan ke AI. | Tentukan persona ahli (contoh: Principal Architect, Analis Data, Sekretaris). |
| 3 | Tugas | Instruksi pekerjaan spesifik yang wajib dikerjakan oleh AI. | Gunakan kata kerja aksi operasional: analisis, bandingkan, hitung, susun. |
| 4 | Input | Data mentah, spesifikasi, matriks angka, atau catatan acuan. | Sertakan seluruh data relevan; larang AI membuat data fiktif. |
| 5 | Kriteria / Batasan | Aturan ketat, kriteria kelayakan, batasan biaya/hukum, dan larangan halusinasi. | Tetapkan parameter eliminasi, batas toleransi error, dan nada komunikasi. |
| 6 | Format Output | Susunan struktur dokumen, template tabel, urutan bab, atau format data. | Tentukan pembagian bab, tabel komparasi, poin rekomendasi, atau format tabel. |
| 7 | Validasi | Perintah verifikasi mandiri agar AI mengecek kembali kepatuhan hasil terhadap input. | Instruksikan AI memvalidasi angka, kepatuhan kriteria, dan konsistensi data. |
| Konteks: [Jelaskan latar belakang situasi, tujuan analisis/pekerjaan, dan target akhir]
Peran: [Bertindak sebagai siapa / sebutkan bidang keahlian dan standar profesional yang dibutuhkan]
Tugas: [Jelaskan secara spesifik langkah atau pekerjaan utama yang harus diselesaikan AI]
Input: [Masukkan seluruh data mentah, parameter teknis, catatan angka, atau teks referensi]
Kriteria/Batasan: [Sebutkan batasan ketat, syarat diskualifikasi, aturan gaya, dan larangan asumsi palsu]
Format Output: [Tentukan struktur laporan: penomoran bab, tabel matriks komparasi, atau rekomendasi aksi]
Validasi: [Perintahkan AI memeriksa ulang perhitungan dan kepatuhan hasil terhadap data input] |
| --- |
| Konteks: Saya ingin mengirim pesan pengingat rapat di grup WhatsApp kantor agar anggota tim tidak lupa, hadir tepat waktu, dan tahu apa saja yang harus dibawa.
Peran: Bertindak sebagai rekan kerja / staf kantor yang ramah, sopan, dan jelas.
Tugas: Buatkan draf teks pesan WhatsApp pengingat rapat berdasarkan catatan yang saya berikan.
Input:
•  Agenda: Pembahasan progres kerja mingguan.
•  Hari/Tanggal: Senin, 31 Agustus 2026 | Jam: 09.00 - 10.00 WIB.
•  Tempat: Ruang Rapat Lt. 2 (atau link Google Meet bagi yang WFH).
•  Bawaan: Laptop dan catatan progres masing-masing.
Kriteria/Batasan: Gunakan bahasa yang ramah tapi tetap sopan. Gunakan poin-poin agar enak dibaca di HP. Jangan menambahkan agenda baru yang tidak tertulis di input.
Format Output: 1. Salam pembuka, 2. Rincian rapat (Hari, Jam, Tempat, Agenda), 3. Hal yang perlu disiapkan, 4. Salam penutup.
Validasi: Pastikan jam, tanggal, dan lokasi rapat sama persis dengan catatan input. |
| --- |
| Konteks: Saya punya catatan pekerjaan hari ini yang masih berserakan dan ingin disusun rapi agar tahu mana yang harus diselesaikan lebih dulu.
Peran: Bertindak sebagai asisten pribadi yang cekatan dan teratur.
Tugas: Kelompokkan dan rapikan catatan pekerjaan saya menjadi tabel urutan prioritas kerja harian.
Input: Beli isi staples & kertas HVS, kirim invoice ke klien (jatuh tempo jam 11 siang), balas email dari atasan, arsipkan nota pembelian kemarin sore, follow up tanda tangan form izin kerja.
Kriteria/Batasan: Urutkan dari yang paling mendesak (pagi ini) ke yang bisa dikerjakan belakangan (siang/sore). Jangan menambah tugas yang tidak saya sebutkan.
Format Output: Tabel dengan kolom: No, Nama Tugas, Waktu Pengerjaan, dan Kategori (Mendesak / Biasa).
Validasi: Pastikan seluruh 5 tugas yang saya sebutkan masuk ke dalam tabel tanpa ada yang terlewat. |
| --- |
| Konteks: Perusahaan perbankan digital berencana memigrasikan basis data transaksi inti (500 GB, 15.000 QPS) dari server fisik lokal ke infrastruktur Managed Cloud. Terdapat 3 opsi provider dengan profil biaya, latensi, kelaikan SLA (RTO/RPO), dan yurisdiksi lokasi server yang berbeda. Tim manajemen memerlukan analisis komparasi teknis-finansial yang mendalam untuk keputusan pengadaan.
Peran: Bertindak sebagai Principal Cloud Solutions Architect & IT Risk Auditor dengan sertifikasi keamanan sistem finansial (ISO 27001 / PCI-DSS).
Tugas: Lakukan evaluasi multi-kriteria terhadap 3 opsi vendor: (1) Lakukan uji kepatuhan regulasi wajib, (2) Hitung Total Cost of Ownership (TCO) 12 bulan, (3) Analisis trade-off teknis (ketersediaan vs biaya), dan (4) Rumuskan rekomendasi arsitektur final beserta rencana mitigasi risiko 4 tahap.
Input:
•  Batas Anggaran: Maksimal $1.500/bulan ($18.000/tahun).
•  Regulasi Wajib: Data nasabah finansial wajib bertempat fisik di dalam wilayah Republik Indonesia (PP PSTE).
•  Vendor A (Lokal Tier-3): Biaya $1.200/bln, Latensi 15ms (Jakarta DC), RTO 15 menit, RPO 5 menit, Lokasi Data: Indonesia, Backup: Otomatis harian, Multi-AZ: Tidak.
•  Vendor B (Global Provider X): Biaya $850/bln, Latensi 65ms (Singapura DC), RTO 1 jam, RPO 30 menit, Lokasi Data: Singapura, Backup: Manual mingguan, Multi-AZ: Ya.
•  Vendor C (Enterprise Multi-Zone): Biaya $2.100/bln, Latensi 12ms (Jakarta-Surabaya Dual DC), RTO 2 menit, RPO 0 detik (Sync Multi-AZ), Lokasi Data: Indonesia, Compliance: SOC 2 & PCI-DSS.
Kriteria/Batasan:
•  Eliminasi Mutlak: Diskualifikasi langsung vendor yang melanggar hukum data residency Indonesia tanpa pengecualian.
•  Kepatuhan Anggaran: Jika opsi terbaik melebihi anggaran $1.500/bln, rancang skema optimasi/hybrid agar pengeluaran riil masuk toleransi anggaran.
•  Objektivitas: Tuliskan perhitungan matematika TCO secara transparan tanpa angka perkiraan bebas. Hindari bahasa marketing.
Format Output:
•  1. Matriks Uji Kelayakan Awal (Tabel: Vendor, Kepatuhan Regulasi Data, Status Lolos/Diskualifikasi).
•  2. Tabel Komparasi Kuantitatif & TCO 1 Tahun (Kolom: Vendor, Biaya/Bulan, TCO 12 Bulan, Latensi, RTO, RPO).
•  3. Analisis Trade-Off & Skenario Kegagalan (Dampak downtime finansial vs penghematan biaya).
•  4. Rekomendasi Arsitektur Terpilih & Skema Optimasi Biaya.
•  5. Rencana Mitigasi Risiko & Roadmap Cutover 4 Fase (Preparation, PoC, Cutover Zero-Downtime, Post-Audit).
Validasi: Periksa ulang bahwa: (a) Vendor dengan lokasi data luar negeri dinyatakan diskualifikasi pada bab 1, (b) TCO 12 bulan dihitung akurat (Biaya Bulanan × 12), dan (c) Rekomendasi akhir mematuhi pagu anggaran serta regulasi data residency lokal. |
| --- |