'use client';

import React from 'react';
import { useGoblix } from '@/lib/store';
import { IMDB_GENRES } from '@/config/global.config';

export default function CategoryFilter() {
  const { activeCategory, setActiveCategory, setSearchQuery } = useGoblix();

  const categories = [
    { id: 'all', label: 'Semua Genre' },
    ...IMDB_GENRES.map(g => ({ id: g, label: g }))
  ];

  return (
    <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider mr-2 flex-shrink-0">
        Genre:
      </span>
      {categories.map(cat => {
        const isActive = activeCategory === cat.id;
        return (
          <button
            key={cat.id}
            onClick={() => { setActiveCategory(cat.id); setSearchQuery(''); }}
            className={`px-3.5 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition border ${
              isActive
                ? 'bg-red-600 border-red-600 text-white shadow-md shadow-red-600/30'
                : 'bg-gray-900/80 border-gray-800 text-gray-300 hover:border-gray-600 hover:text-white'
            }`}
          >
            {cat.label}
          </button>
        );
      })}
    </div>
  );
}
