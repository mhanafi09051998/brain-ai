'use client';

import React from 'react';
import Link from 'next/link';
import { useGoblix } from '@/lib/store';

export default function HeroBanner({ movie }) {
  const { setSelectedMovie, myList, toggleMyList, watchProgress } = useGoblix();
  if (!movie) return null;

  const inList = myList.includes(movie.id) || myList.includes(movie.slug);
  const prog = watchProgress[movie.id] || watchProgress[movie.slug];

  return (
    <header 
      className="relative w-full h-screen min-h-screen flex items-end pb-16 sm:pb-24 px-4 sm:px-8 md:px-12 bg-cover bg-[center_top] sm:bg-center overflow-hidden" 
      style={{ backgroundImage: `url('${movie.backdrop || movie.poster}')` }}
    >
      <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/60 to-black/30"></div>
      <div className="absolute inset-0 bg-gradient-to-r from-[#141414] via-[#141414]/75 to-transparent w-full md:w-3/4"></div>
      <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#141414] to-transparent"></div>

      <div className="relative z-10 max-w-2xl space-y-3 sm:space-y-4 pt-20">
        <div className="flex items-center space-x-2">
          <span className="bg-red-600 text-white text-[10px] sm:text-xs px-2.5 py-0.5 rounded font-black tracking-widest uppercase">
            GOBLIX ORIGINAL
          </span>
          <span className="border border-white/40 text-gray-200 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">
            {movie.quality || '1080p BluRay'}
          </span>
          <span className="border border-white/40 text-gray-200 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">
            {movie.ageRating || '13+'}
          </span>
          <span className="text-green-400 text-xs sm:text-sm font-bold">
            {movie.matchScore || '98% Cocok'}
          </span>
        </div>

        <h1 className="text-3xl sm:text-5xl md:text-6xl font-black text-white leading-none tracking-tight drop-shadow-2xl">
          {movie.title}
        </h1>

        <p className="text-gray-300 text-xs sm:text-sm line-clamp-3 md:line-clamp-4 leading-relaxed max-w-xl drop-shadow">
          {movie.synopsis}
        </p>

        <div className="flex flex-wrap items-center gap-1.5 text-[11px] sm:text-xs text-gray-400 font-medium pt-1">
          <span>{movie.year}</span>
          <span>•</span>
          <span>{movie.duration}</span>
          <span>•</span>
          <span className="text-gray-300">{Array.isArray(movie.genres) ? movie.genres.join(', ') : movie.genres}</span>
          <span>•</span>
          <span className="text-amber-400 font-semibold">{movie.subtitle}</span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3 pt-3">
          <Link
            href={`/watch/${movie.slug}`}
            className="bg-white hover:bg-gray-200 text-black font-extrabold px-6 sm:px-8 py-2.5 sm:py-3 rounded-md flex items-center space-x-2.5 transition text-xs sm:text-sm shadow-xl hover:scale-105 active:scale-95"
          >
            <i className="fa-solid fa-play text-sm"></i>
            <span>{prog ? `Lanjutkan (${prog.percent}%)` : 'Putar Film'}</span>
          </Link>

          <button
            onClick={() => setSelectedMovie(movie)}
            className="bg-gray-600/70 hover:bg-gray-600 text-white font-bold px-5 sm:px-6 py-2.5 sm:py-3 rounded-md flex items-center space-x-2 transition text-xs sm:text-sm backdrop-blur border border-white/20 hover:scale-105 active:scale-95"
          >
            <i className="fa-solid fa-circle-info text-sm"></i>
            <span>Selengkapnya</span>
          </button>

          <button
            onClick={() => toggleMyList(movie.id)}
            className={`w-10 h-10 rounded-full border border-gray-400/60 flex items-center justify-center transition text-sm ${
              inList ? 'bg-red-600 border-red-600 text-white' : 'bg-black/40 hover:bg-black/60 text-white'
            }`}
            title={inList ? 'Hapus dari Daftar' : 'Tambah ke Daftar'}
          >
            <i className={`fa-solid ${inList ? 'fa-check' : 'fa-plus'}`}></i>
          </button>
        </div>

        {/* Resume progress bar */}
        {prog && (
          <div className="pt-2 max-w-xs">
            <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
              <div className="bg-red-600 h-full rounded-full" style={{ width: `${prog.percent}%` }}></div>
            </div>
            <p className="text-[10px] text-gray-400 mt-1">Terakhir ditonton sampai menit {Math.round(prog.currentTime / 60)}</p>
          </div>
        )}
      </div>
    </header>
  );
}
