'use client';

import React from 'react';
import { useGoblix } from '@/lib/store';
import MovieCard from './MovieCard';

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
    : (activeCategory === 'all' ? 'Koleksi Film Box Office & Blockbuster Terpopuler' : `Kategori: ${activeCategory}`);

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg sm:text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <span>{sectionTitle}</span>
          <span className="text-xs font-normal text-gray-400">({filteredMovies.length})</span>
        </h2>
        <span className="text-[11px] font-bold text-red-500 uppercase tracking-wider hidden sm:inline">
          <i className="fa-solid fa-fire mr-1"></i>
          Trending di Indonesia
        </span>
      </div>

      {filteredMovies.length === 0 ? (
        <div className="text-center py-16 bg-gray-900/40 rounded-xl border border-gray-800/80 space-y-3">
          <i className="fa-solid fa-film text-4xl text-gray-600"></i>
          <p className="text-sm text-gray-400">Tidak ada film yang cocok dengan kriteria pencarian.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 gap-3 sm:gap-5">
          {filteredMovies.map(movie => (
            <MovieCard key={movie.id || movie.slug} movie={movie} />
          ))}
        </div>
      )}
    </section>
  );
}
