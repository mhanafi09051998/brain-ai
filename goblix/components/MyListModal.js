'use client';

import React from 'react';
import { useGoblix } from '@/lib/store';

export default function MyListModal() {
  const { myListOpen, setMyListOpen, myList, movies, setSelectedMovie } = useGoblix();

  if (!myListOpen) return null;

  const listMovies = movies.filter(m => myList.includes(m.id) || myList.includes(m.slug));

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) setMyListOpen(false); }}
    >
      <div className="bg-gray-950 border border-gray-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative text-white">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center space-x-2">
            <i className="fa-solid fa-bookmark text-red-600 text-lg"></i>
            <h2 className="text-base sm:text-lg font-bold text-white">Daftar Tontonan Saya</h2>
          </div>
          <button
            onClick={() => setMyListOpen(false)}
            className="w-8 h-8 rounded-full bg-gray-900 hover:bg-red-600 text-gray-400 hover:text-white flex items-center justify-center transition border border-gray-800 text-sm"
          >
            <i className="fa-solid fa-xmark"></i>
          </button>
        </div>

        {/* Content */}
        {listMovies.length === 0 ? (
          <div className="text-center py-10 space-y-2 text-gray-400">
            <i className="fa-solid fa-film text-3xl text-gray-600"></i>
            <p className="text-sm">Belum ada film yang ditambahkan ke Daftar Saya.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-96 overflow-y-auto p-1">
            {listMovies.map(movie => (
              <div
                key={movie.id || movie.slug}
                onClick={() => { setMyListOpen(false); setSelectedMovie(movie); }}
                className="group bg-gray-900 border border-gray-800 hover:border-red-600 rounded-lg overflow-hidden cursor-pointer transition flex flex-col"
              >
                <div
                  className="aspect-[2/3] bg-cover bg-center relative"
                  style={{ backgroundImage: `url('${movie.poster || movie.backdrop}')` }}
                >
                  <span className="absolute top-1 left-1 bg-red-600 text-[9px] font-black px-1.5 py-0.5 rounded text-white">
                    {movie.quality || '1080p'}
                  </span>
                </div>
                <div className="p-2">
                  <h4 className="text-xs font-bold text-white truncate group-hover:text-red-500">{movie.title}</h4>
                  <span className="text-[10px] text-gray-400">{movie.year}</span>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
