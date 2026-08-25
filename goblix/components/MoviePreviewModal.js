'use client';

import React from 'react';
import Link from 'next/link';
import { useGoblix } from '@/lib/store';

export default function MoviePreviewModal() {
  const { selectedMovie, setSelectedMovie, myList, toggleMyList, watchProgress } = useGoblix();

  if (!selectedMovie) return null;

  const inList = myList.includes(selectedMovie.id) || myList.includes(selectedMovie.slug);
  const prog = watchProgress[selectedMovie.id] || watchProgress[selectedMovie.slug];

  return (
    <div 
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) setSelectedMovie(null); }}
    >
      <div className="bg-[#181818] border border-gray-800 rounded-xl sm:rounded-2xl max-w-3xl w-full overflow-hidden shadow-2xl relative my-auto text-white">
        
        {/* Close Button */}
        <button
          onClick={() => setSelectedMovie(null)}
          className="absolute top-4 right-4 z-20 w-9 h-9 rounded-full bg-black/70 hover:bg-red-600 text-white flex items-center justify-center transition border border-white/20"
        >
          <i className="fa-solid fa-xmark text-sm"></i>
        </button>

        {/* Modal Banner */}
        <div 
          className="relative aspect-video sm:aspect-[21/9] w-full bg-cover bg-center"
          style={{ backgroundImage: `url('${selectedMovie.backdrop || selectedMovie.poster}')` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-[#181818] via-transparent to-black/40"></div>
          
          <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 space-y-3 z-10 max-w-lg">
            <h2 className="text-2xl sm:text-4xl font-black text-white leading-tight drop-shadow-lg">
              {selectedMovie.title}
            </h2>
            
            <div className="flex items-center space-x-3">
              <Link
                href={`/watch/${selectedMovie.slug}`}
                onClick={() => setSelectedMovie(null)}
                className="bg-white hover:bg-gray-200 text-black font-extrabold px-6 py-2 rounded-md flex items-center space-x-2 transition text-xs sm:text-sm shadow-lg hover:scale-105"
              >
                <i className="fa-solid fa-play text-xs"></i>
                <span>{prog ? `Lanjutkan (${prog.percent}%)` : 'Putar'}</span>
              </Link>

              <button
                onClick={() => toggleMyList(selectedMovie.id)}
                className={`w-9 h-9 rounded-full border border-gray-400 flex items-center justify-center transition text-xs ${
                  inList ? 'bg-red-600 border-red-600 text-white' : 'bg-black/60 text-white hover:bg-black'
                }`}
                title={inList ? 'Hapus dari Daftar' : 'Tambah ke Daftar'}
              >
                <i className={`fa-solid ${inList ? 'fa-check' : 'fa-plus'}`}></i>
              </button>
            </div>
          </div>
        </div>

        {/* Modal Details Body */}
        <div className="p-4 sm:p-6 space-y-4 text-xs sm:text-sm">
          
          {/* Metadata Row */}
          <div className="flex flex-wrap items-center gap-2 text-gray-300 font-semibold border-b border-gray-800 pb-3">
            <span className="text-green-400 font-bold">{selectedMovie.matchScore || '98% Cocok'}</span>
            <span>•</span>
            <span>{selectedMovie.year}</span>
            <span>•</span>
            <span className="border border-gray-600 px-1.5 py-0.2 rounded text-[10px]">{selectedMovie.ageRating || '13+'}</span>
            <span>•</span>
            <span>{selectedMovie.duration}</span>
            <span>•</span>
            <span className="bg-red-600 text-white text-[10px] px-1.5 py-0.5 rounded font-black">{selectedMovie.quality || '1080p'}</span>
            <span>•</span>
            <span className="text-amber-400 font-mono text-[11px]">{selectedMovie.audio}</span>
          </div>

          {/* Synopsis & Cast Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-2">
              <p className="text-gray-300 leading-relaxed">
                {selectedMovie.synopsis}
              </p>
            </div>

            <div className="space-y-2.5 text-xs border-t md:border-t-0 md:border-l border-gray-800 pt-3 md:pt-0 md:pl-4">
              <div>
                <span className="text-gray-500 block">Sutradara:</span>
                <span className="text-gray-200 font-medium">{selectedMovie.director}</span>
              </div>

              <div>
                <span className="text-gray-500 block">Pemeran:</span>
                <span className="text-gray-200 font-medium">
                  {Array.isArray(selectedMovie.cast) ? selectedMovie.cast.join(', ') : selectedMovie.cast}
                </span>
              </div>

              <div>
                <span className="text-gray-500 block">Genre IMDb:</span>
                <span className="text-gray-200 font-medium">
                  {Array.isArray(selectedMovie.genres) ? selectedMovie.genres.join(', ') : selectedMovie.genres}
                </span>
              </div>

              <div>
                <span className="text-gray-500 block">Subtitle:</span>
                <span className="text-amber-400 font-semibold">{selectedMovie.subtitle}</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
