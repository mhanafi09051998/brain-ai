'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useGoblix } from '@/lib/store';

const IMDB_GENRES = [
  'Action', 'Adventure', 'Comedy', 'Crime', 'Drama', 'Mystery',
  'Sci-Fi', 'Thriller', 'Animation', 'Horror', 'Romance'
];

export default function Navbar() {
  const {
    activeCategory,
    setActiveCategory,
    searchQuery,
    setSearchQuery,
    setAuthModal,
    setMyListOpen,
    currentUser,
    setToken,
    myList
  } = useGoblix();

  const [isScrolled, setIsScrolled] = useState(false);
  const [searchActive, setSearchActive] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 w-full z-40 transition-colors duration-300 px-4 sm:px-8 md:px-12 py-3.5 flex items-center justify-between ${
      isScrolled ? 'bg-[#141414] border-b border-gray-800/80 shadow-2xl' : 'bg-gradient-to-b from-black/95 via-black/60 to-transparent'
    }`}>
      
      {/* Left: Brand & Navigation */}
      <div className="flex items-center space-x-4 md:space-x-8">
        <Link href="/" onClick={() => setActiveCategory('all')} className="text-2xl sm:text-3xl md:text-4xl font-black tracking-wider text-red-600 font-bebas transition hover:scale-105">
          GOBLIX
        </Link>

        <ul className="hidden lg:flex items-center space-x-5 text-xs sm:text-sm font-medium text-gray-300">
          <li>
            <button onClick={() => { setActiveCategory('all'); setSearchQuery(''); }} className={`hover:text-white transition font-semibold ${activeCategory === 'all' ? 'text-white font-bold' : ''}`}>
              Beranda
            </button>
          </li>
          <li>
            <button onClick={() => setActiveCategory('Action')} className={`hover:text-white transition ${activeCategory === 'Action' ? 'text-white font-bold' : ''}`}>
              Action
            </button>
          </li>
          <li>
            <button onClick={() => setActiveCategory('Sci-Fi')} className={`hover:text-white transition ${activeCategory === 'Sci-Fi' ? 'text-white font-bold' : ''}`}>
              Sci-Fi
            </button>
          </li>
          <li>
            <button onClick={() => setMyListOpen(true)} className="hover:text-white transition flex items-center space-x-1">
              <span>Daftar Saya</span>
              <span className="bg-red-600 text-white text-[9px] px-1.5 py-0.2 rounded-full font-bold">{myList.length}</span>
            </button>
          </li>

          {/* Official IMDb Genre Dropdown */}
          <li className="relative group">
            <button className="hover:text-white flex items-center space-x-1 py-1 font-semibold text-gray-300 group-hover:text-white transition">
              <span>Kategori</span>
              <i className="fa-solid fa-caret-down text-xs transition-transform group-hover:rotate-180"></i>
            </button>
            <div className="absolute left-0 top-full mt-1.5 w-48 bg-gray-950/95 border border-gray-800 rounded-md shadow-2xl py-2 hidden group-hover:block backdrop-blur z-50">
              <button onClick={() => setActiveCategory('all')} className="w-full text-left px-4 py-1.5 text-xs text-gray-300 hover:bg-red-600 hover:text-white transition font-medium">
                Semua Genre
              </button>
              {IMDB_GENRES.map(genre => (
                <button key={genre} onClick={() => setActiveCategory(genre)} className="w-full text-left px-4 py-1.5 text-xs text-gray-300 hover:bg-red-600 hover:text-white transition font-medium">
                  {genre}
                </button>
              ))}
            </div>
          </li>
        </ul>
      </div>

      {/* Right: Search, Notification & Auth */}
      <div className="flex items-center space-x-3 sm:space-x-5">
        
        {/* Expandable Search Input */}
        <div className="relative flex items-center">
          <div className={`flex items-center border rounded-md transition-all duration-300 px-2 py-1 ${
            searchActive ? 'bg-black/90 border-red-600' : 'border-transparent bg-transparent'
          }`}>
            <button onClick={() => setSearchActive(!searchActive)} className="text-gray-300 hover:text-white focus:outline-none" title="Cari film">
              <i className="fa-solid fa-magnifying-glass text-sm sm:text-base"></i>
            </button>
            <input
              type="text"
              placeholder="Judul, genre, aktor..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`bg-transparent text-white text-xs sm:text-sm focus:outline-none transition-all duration-300 pl-2 ${
                searchActive ? 'w-36 sm:w-56 opacity-100' : 'w-0 opacity-0 pointer-events-none'
              }`}
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="text-gray-400 hover:text-white text-xs ml-1">
                <i className="fa-solid fa-xmark"></i>
              </button>
            )}
          </div>
        </div>

        {/* User Auth Profile Suite */}
        {currentUser ? (
          <div className="relative group">
            <button className="flex items-center space-x-2 focus:outline-none py-1">
              <div className="w-8 h-8 rounded bg-red-600 flex items-center justify-center font-bold text-xs text-white border border-red-500 shadow-md">
                {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'G'}
              </div>
              <i className="fa-solid fa-caret-down text-gray-400 text-xs transition group-hover:rotate-180 hidden sm:inline"></i>
            </button>
            <div className="absolute right-0 top-full mt-2 w-48 bg-gray-950/95 border border-gray-800 rounded-md shadow-2xl py-2 hidden group-hover:block backdrop-blur z-50 text-xs">
              <div className="px-4 py-2 border-b border-gray-800">
                <p className="font-bold text-white truncate">{currentUser.name}</p>
                <p className="text-[10px] text-green-400 font-mono">Paket HD Sinema</p>
              </div>
              <button onClick={() => setMyListOpen(true)} className="w-full text-left px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white transition">
                Daftar Saya ({myList.length})
              </button>
              <button onClick={() => setToken(null)} className="w-full text-left px-4 py-2 text-red-400 hover:bg-red-600 hover:text-white transition border-t border-gray-800 font-semibold">
                Keluar dari Goblix
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <button onClick={() => setAuthModal('login')} className="text-xs font-bold text-gray-300 hover:text-white px-2.5 py-1.5 transition">
              Masuk
            </button>
            <button onClick={() => setAuthModal('register')} className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-3.5 py-1.5 rounded transition shadow-md shadow-red-600/30">
              Daftar
            </button>
          </div>
        )}

      </div>
    </nav>
  );
}
