'use client';

import React from 'react';

export default function Footer() {
  return (
    <footer className="border-t border-gray-900 py-10 px-6 md:px-16 text-gray-500 text-xs bg-black">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-[12px] text-gray-400">
          <span className="hover:underline hover:text-gray-200 transition cursor-pointer">Syarat & Ketentuan Penggunaan</span>
          <span className="hover:underline hover:text-gray-200 transition cursor-pointer">Kebijakan Privasi</span>
          <span className="hover:underline hover:text-gray-200 transition cursor-pointer">Preferensi Cookie</span>
          <span className="hover:underline hover:text-gray-200 transition cursor-pointer">Pusat Bantuan & FAQ</span>
        </div>

        <div className="pt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between text-gray-500 text-[11px] border-t border-gray-900/80 gap-2">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold tracking-widest text-red-600 font-bebas">GOBLIX</span>
            <span>Indonesia</span>
          </div>
          <p>© 2026 GOBLIX Cinema. Hak Cipta Dilindungi.</p>
        </div>
      </div>
    </footer>
  );
}
