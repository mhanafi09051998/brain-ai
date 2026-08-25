'use client';

import React from 'react';
import { useGoblix } from '@/lib/store';
import MovieCard from './MovieCard';
import CategoryFilter from './CategoryFilter';

export default function MovieGrid() {
  const { movies, activeCategory, searchQuery } = useGoblix();

  const filteredMovies = movies.filter(m => {
    // 1. Category filter
    if (activeCategory !== 'all') {
      const genres = Array.isArray(m.genres) ? m.genres : [];
      if (!genres.some(g => g.toLowerCase() === activeCategory.toLowerCase())) {
        return false;
      }
    }

    // 2. Search query
    if (searchQuery) {
      const q = searchQuery.toLowerCase().trim();
      const titleMatch = (m.title || '').toLowerCase().includes(q);
      const genreMatch = Array.isArray(m.genres) && m.genres.some(g => (g || '').toLowerCase().includes(q));
      const castMatch = Array.isArray(m.cast) && m.cast.some(c => (c || '').toLowerCase().includes(q));
      const directorMatch = (m.director || '').toLowerCase().includes(q);
      const synopsisMatch = (m.synopsis || '').toLowerCase().includes(q);
      return titleMatch || genreMatch || castMatch || directorMatch || synopsisMatch;
    }

    return true;
  });

  const sectionTitle = searchQuery
    ? `Hasil Pencarian: "${searchQuery}"`
    : (activeCategory === 'all' ? 'Koleksi Film Box Office & Blockbuster Terpopuler' : `Kategori IMDb: ${activeCategory}`);

  return (
    <section className="space-y-6 pt-4">
      
      {/* Section Header: Title & Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-900 pb-4">
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <span>{sectionTitle}</span>
          <span className="text-xs font-normal text-gray-400">({filteredMovies.length} film)</span>
        </h2>
        
        <span className="text-[11px] font-bold text-red-500 uppercase tracking-wider flex items-center">
          <i className="fa-solid fa-fire mr-1.5 animate-pulse"></i>
          Trending di Indonesia
        </span>
      </div>

      {/* Inline Genre Filter Bar */}
      <div className="bg-gray-950/70 p-3 rounded-xl border border-gray-800/80 shadow-inner">
        <CategoryFilter />
      </div>

      {/* Movie Cards Grid */}
      {filteredMovies.length === 0 ? (
        <div className="text-center py-16 bg-gray-900/30 rounded-2xl border border-gray-800/60 space-y-3">
          <i className="fa-solid fa-film text-4xl text-gray-600"></i>
          <p className="text-sm text-gray-400">Tidak ada film dalam kategori ini.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 gap-4 sm:gap-6">
          {filteredMovies.map(movie => (
            <MovieCard key={movie.id || movie.slug} movie={movie} />
          ))}
        </div>
      )}

    </section>
  );
}
