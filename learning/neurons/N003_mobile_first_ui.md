# Neuron N003: Mobile-First UI & Compact Data Viz

## Core Concept
Prinsip adaptasi UI densitas tinggi (seperti kalender arus kas, grafik metrik, tabel data) pada layar sempit:
- **Kalender Grid (7 Kolom)**: Layar mobile (~360px–400px) hanya memiliki ~40px per kolom. Teks mata uang panjang (`+Rp 1.500.000`) pasti overflow jika dipaksakan.
- **Solusi**: Gunakan indikator dot visual (`w-1.5 h-1.5 rounded-full bg-emerald-500`) pada mode mobile (`flex sm:hidden`), dan teks angka penuh pada desktop (`hidden sm:block`).
- **Tinggi Cell**: Turunkan dari `min-h-[85px]` menjadi `min-h-[44px] sm:min-h-[85px]` agar tidak memakan seluruh viewport ponsel.
- **Aksi Tabel**: Jangan gunakan `opacity-0 group-hover:opacity-100` di mobile karena touch screen tidak memiliki event hover. Gunakan `opacity-100 sm:opacity-0 sm:group-hover:opacity-100`.

## Synaptic Links
- **N004 (Ponytail Minimality)**: Gunakan utility classes Tailwind bawaan tanpa menambah library UI eksternal.
- **N001 (Executive Decisions)**: Deteksi langsung komponen padat data dan terapkan pola compact dot secara otomatis.
