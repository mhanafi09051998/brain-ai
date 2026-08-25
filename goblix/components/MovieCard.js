'use client';

import React from 'react';
import { useGoblix } from '@/lib/store';

export default function MovieCard({ movie }) {
  const { setSelectedMovie, myList, toggleMyList, watchProgress } = useGoblix();
  if (!movie) return null;

  const inList = myList.includes(movie.id) || myList.includes(movie.slug);
  const prog = watchProgress[movie.id] || watchProgress[movie.slug];

  return (
    <div
      onClick={() => setSelectedMovie(movie)}
      className="group relative bg-[#181818] rounded-md overflow-hidden cursor-pointer transition-all duration-300 transform hover:scale-105 hover:z-20 hover:shadow-2xl hover:shadow-black border border-gray-800/80 hover:border-gray-600 flex flex-col"
    >
      {/* Poster Image */}
      <div 
        className="aspect-[2/3] w-full bg-cover bg-center relative bg-gray-900"
        style={{ backgroundImage: `url('${movie.poster || movie.backdrop}')` }}
      >
        {/* Badges */}
        <div className="absolute top-2 left-2 flex flex-col space-y-1">
          <span className="bg-red-600 text-white text-[9px] font-black px-1.5 py-0.5 rounded shadow">
            {movie.quality || '1080p'}
          </span>
          <span className="bg-black/70 backdrop-blur text-amber-300 text-[8px] font-bold px-1.5 py-0.2 rounded border border-amber-500/30">
            SUB INDO
          </span>
        </div>

        {/* Quick Add to Watchlist */}
        <button
          onClick={(e) => { e.stopPropagation(); toggleMyList(movie.id); }}
          className={`absolute top-2 right-2 w-7 h-7 rounded-full flex items-center justify-center text-xs transition backdrop-blur border ${
            inList ? 'bg-red-600 border-red-600 text-white' : 'bg-black/60 border-white/40 text-white hover:bg-black/90'
          }`}
          title={inList ? 'Hapus dari Daftar' : 'Tambah ke Daftar'}
        >
          <i className={`fa-solid ${inList ? 'fa-check' : 'fa-plus'}`}></i>
        </button>

        {/* Watch Progress Bar */}
        {prog && (
          <div className="absolute bottom-0 inset-x-0 h-1 bg-gray-900">
            <div className="h-full bg-red-600" style={{ width: `${prog.percent}%` }}></div>
          </div>
        )}
      </div>

      {/* Info footer */}
      <div className="p-2.5 sm:p-3 flex-1 flex flex-col justify-between space-y-1 bg-[#181818]">
        <h3 className="text-xs sm:text-sm font-bold text-white group-hover:text-red-500 truncate transition">
          {movie.title}
        </h3>
        <div className="flex items-center justify-between text-[10px] text-gray-400">
          <span className="text-green-400 font-semibold">{movie.matchScore || '98% Cocok'}</span>
          <span>{movie.year}</span>
        </div>
      </div>
    </div>
  );
}
