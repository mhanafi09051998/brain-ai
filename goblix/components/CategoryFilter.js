'use client';

import React from 'react';
import { useGoblix } from '@/lib/store';

const CATEGORIES = [
  { id: 'all', label: 'Semua Genre' },
  { id: 'Action', label: 'Action' },
  { id: 'Adventure', label: 'Adventure' },
  { id: 'Comedy', label: 'Comedy' },
  { id: 'Crime', label: 'Crime' },
  { id: 'Drama', label: 'Drama' },
  { id: 'Mystery', label: 'Mystery' },
  { id: 'Sci-Fi', label: 'Sci-Fi' },
  { id: 'Thriller', label: 'Thriller' },
  { id: 'Animation', label: 'Animation' },
  { id: 'Horror', label: 'Horror' },
  { id: 'Romance', label: 'Romance' }
];

export default function CategoryFilter() {
  const { activeCategory, setActiveCategory, setSearchQuery } = useGoblix();

  return (
    <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider mr-2 flex-shrink-0">
        Genre:
      </span>
      {CATEGORIES.map(cat => {
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
