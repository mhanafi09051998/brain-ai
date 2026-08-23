# Pembelajaran & Standar Tetap (Learnings & Fixed Rules) - Claudia

Dokumen ini adalah ringkasan aturan permanen yang harus selalu dipatuhi Claudia secara otomatis tanpa perlu diminta berulang:

## 1. Tampilan & Mode
- Default seluruh aplikasi di VPS adalah **Light Mode (Mode Terang)**.
- Dark mode disediakan via toggle opsional dengan sinkronisasi localStorage.

## 2. Dropdown & Komponen Formulir
- Jangan gunakan default browser dropdown <select> yang kaku.
- Gunakan custom React dropdown popover dengan pencarian real-time, header kategori, dan click-outside listener.
- Field password pada login/register WAJIB memiliki toggle **Eye/EyeOff (Show/Hide Password)**.

## 3. Responsivitas Mobile
- Tata letak mobile harus rapi, padding proporsional (p-4 s.d. p-6), tidak boleh ada overflow horizontal.
- Sub-field form pada layar sempit harus stack 1 kolom (grid-cols-1 sm:grid-cols-2).
- Segment tab harus memiliki lebar seimbang dan teks tidak boleh terpotong.
- Popup harus menggunakan modal/toast React in-page (bukan alert/confirm native browser).

## 4. Branding & Desain Khusus MojoLoker
- Domain resmi hanya: mojoloker.my.id.
- Ikon browser/logo: Tugu Alun-Alun Mojokerto (tengah saja, tanpa gerbang samping) berlatar PUTIH (#ffffff) dengan border halus.
- Header logo hanya teks MojoLoker tanpa imbuhan badge Mojokerto.
- Tanpa elemen AI klise (no stars, no sparkles, no generic promotional fluff).
- Proteksi detail pekerjaan: Harus login untuk melihat rincian gaji, deskripsi lengkap, kualifikasi, kontak HRD, dan melamar.
- Banner wajib anti-penipuan: "Pemberi Kerja Tidak Memungut Biaya Apapun (100% GRATIS)".
