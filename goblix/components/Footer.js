'use client';

import React from 'react';
import { APP_CONFIG, LEGAL_LINKS } from '@/config/global.config';

export default function Footer() {
  return (
    <footer className="border-t border-gray-900 py-10 px-6 md:px-16 text-gray-500 text-xs bg-black">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Centralized Policy / Legal Links */}
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-[12px] text-gray-400">
          {LEGAL_LINKS.map(item => (
            <span key={item.id} className="hover:underline hover:text-gray-200 transition cursor-pointer">
              {item.label}
            </span>
          ))}
        </div>

        {/* Branding & Copyright */}
        <div className="pt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between text-gray-500 text-[11px] border-t border-gray-900/80 gap-2">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold tracking-widest text-red-600 font-bebas">{APP_CONFIG.name}</span>
            <span>{APP_CONFIG.region}</span>
          </div>
          <p>{APP_CONFIG.copyright}</p>
        </div>
      </div>
    </footer>
  );
}
