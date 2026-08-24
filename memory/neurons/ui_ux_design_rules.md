# Neuron Memory: Standar Desain UI/UX & Aturan Kode

1. **Mode Tampilan**:
   - **Default Light Mode (Mode Terang)** di seluruh aplikasi web.
   - Dark mode disediakan via toggle dengan persistensi localStorage.
2. **Komponen Form & Interaktivitas**:
   - Dilarang memakai dropdown `<select>` default browser yang kaku.
   - Wajib gunakan custom React popover dropdown dengan pencarian live, header kategori, dan checkmark.
   - Field password pada login/register WAJIB memiliki toggle **Eye/EyeOff (Show/Hide Password)**.
   - **DILARANG KERAS popup bawaan browser (`alert()`, `confirm()`, `prompt()`)**.
3. **Larangan Mutlak Popup Browser (Zero Native Browser Popups Rule)**:
   - **DILARANG KERAS menggunakan popup bawaan browser (`alert()`, `confirm()`, `prompt()`) pada SELURUH website.**
   - **Wajib 100% menggunakan Custom In-Page UI Popup / Modal / Toast Website** (komponen modal kustom dengan animasi halus, backdrop blur, tombol aksi bergaya modern korporat, dan terintegrasi tema Light/Dark).
   - Seluruh notifikasi sukses, peringatan, error, maupun dialog konfirmasi hapus/tindakan penting WAJIB dirender sebagai elemen DOM website sendiri (misal: custom Toast, Radix UI Dialog, Framer Motion Modal, atau komponen modal React/HTML kustom).
4. **Responsivitas Ponsel**:
   - Mobile-first, padding proporsional (p-4 s.d. p-6), no horizontal overflow.
   - Form input sub-field vertikal wajib 1 kolom pada ponsel (grid-cols-1 sm:grid-cols-2).
   - Tab switcher (role selector) wajib seimbang (grid-cols-2) tanpa text wrapping berantakan.
5. **Anti-AI Design Aesthetic**:
   - Dilarang menambahkan badge dekoratif klise (e.g. "Regulasi Resmi...", sparkles, bintang AI).
   - Tampilan harus korporat, bersih, dan modern seperti Glints/JobStreet.
6. **Aturan Baris Kode (Maintainability Rule)**:
   - **MAKSIMAL 300 BARIS KODE PER FILE**.
   - Wajib memecah file menjadi sub-komponen, helper modul, atau repositori terpisah jika mendekati 300 baris.
7. **Umpan Balik Error & Ketahanan Interaksi (Feedback & Interaction Resilience)**:
   - **Dilarang tombol macet/stuck loading**: Tombol aksi/submit wajib pulih otomatis (`disabled=false`) jika terjadi error di jaringan atau server.
   - **Pesan error eksplisit & kontekstual**: Tampilkan pesan jelas (e.g. `Username sudah dipakai`, `Password terlalu pendek`), dilarang hanya kode error mentah atau diam tanpa respon.
   - **Visual Feedback & Auto-Focus**: Field input yang bermasalah wajib diberi highlight visual (border merah/animasi getar) dan kursor otomatis fokus ke field tersebut.
   - **Auto-Clear saat mengetik**: Banner/highlight error wajib otomatis hilang begitu user mulai mengetik perbaikan.
