// ===================================================================
// GOBLIX VIEW RENDERERS MODULE (views.js)
// Responsive Netflix-Style Views: Home, Movie Detail, Watch, Auth, Modal
// Max ~250 lines • Clean Separation of Concerns
// ===================================================================

import { state, toggleMyList } from './state.js';
import { formatTime } from './player.js';
import { loadSubtitles } from './subtitle.js';
import { saveServerWatchProgress } from './api.js';

export function renderHomePage() {
  const main = document.getElementById('app-root');
  const featured = state.moviesData[0] || {};
  const progressInfo = state.watchProgress[featured.id] || state.watchProgress[featured.slug];
  const hasResume = progressInfo && progressInfo.currentTime > 10;
  const isFeaturedInList = state.myList.includes(featured.id) || state.myList.includes(featured.slug);

  let filteredMovies = Array.isArray(state.moviesData) ? state.moviesData : [];
  if (state.activeCategory !== 'all') {
    filteredMovies = filteredMovies.filter(m => 
      Array.isArray(m.genres) && m.genres.some(g => (g || '').toLowerCase().includes(state.activeCategory.toLowerCase()))
    );
  }
  if (state.searchQuery) {
    const q = (state.searchQuery || '').toLowerCase();
    filteredMovies = filteredMovies.filter(m => {
      const titleMatch = (m.title || '').toLowerCase().includes(q);
      const genreMatch = Array.isArray(m.genres) && m.genres.some(g => (g || '').toLowerCase().includes(q));
      const castMatch = Array.isArray(m.cast) && m.cast.some(c => (c || '').toLowerCase().includes(q));
      const directorMatch = (m.director || '').toLowerCase().includes(q);
      const synopsisMatch = (m.synopsis || '').toLowerCase().includes(q);
      return titleMatch || genreMatch || castMatch || directorMatch || synopsisMatch;
    });
  }

  const categories = [
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

  let collectionTitle = 'Koleksi Film Pilihan';
  let collectionBadge = 'Trending di Indonesia';

  if (state.searchQuery) {
    collectionTitle = `Hasil Pencarian: "${state.searchQuery}"`;
    collectionBadge = 'Pencarian Instan';
  } else if (state.activeCategory !== 'all') {
    collectionTitle = `Kategori: ${state.activeCategory}`;
    collectionBadge = 'Kategori IMDb';
  }

  main.innerHTML = `
    <!-- HERO BANNER (NETFLIX HERO 100vh FULL VIEWPORT) -->
    <header class="relative w-full h-screen min-h-screen flex items-end pb-16 sm:pb-24 px-4 sm:px-8 md:px-12 bg-cover bg-[center_top] sm:bg-center overflow-hidden" 
            style="background-image: url('${featured.backdrop || featured.poster}');">
      <div class="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/60 to-black/30"></div>
      <div class="absolute inset-0 bg-gradient-to-r from-[#141414] via-[#141414]/75 to-transparent w-full md:w-3/4"></div>
      <div class="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#141414] to-transparent"></div>

      <div class="relative z-10 max-w-2xl space-y-3 sm:space-y-4 pt-20">
        <div class="flex items-center space-x-2">
          <span class="bg-red-600 text-white text-[10px] sm:text-xs px-2.5 py-0.5 rounded font-black tracking-widest uppercase">GOBLIX ORIGINAL</span>
          <span class="border border-white/40 text-gray-200 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">${featured.quality || '1080p'}</span>
          <span class="bg-yellow-500 text-black text-[10px] sm:text-xs px-2 py-0.5 rounded font-extrabold">SUB INDO</span>
        </div>

        <h1 class="text-2xl sm:text-4xl md:text-6xl font-extrabold tracking-tight drop-shadow-md leading-tight text-white">${featured.title || 'Loading...'}</h1>

        <div class="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-300 font-medium">
          <span class="text-green-400 font-bold">${featured.matchScore} Match</span>
          <span>${featured.year}</span>
          <span class="border border-gray-500 px-1.5 py-0.2 rounded text-[10px]">${featured.ageRating}</span>
          <span>${featured.duration}</span>
          <span class="bg-gray-800 px-2 py-0.5 rounded text-white font-bold hidden sm:inline">${featured.audio}</span>
        </div>

        <p class="text-gray-300 text-xs sm:text-sm md:text-base line-clamp-3 md:line-clamp-4 leading-relaxed drop-shadow">${featured.synopsis || ''}</p>

        <!-- STREAMING & RESUME ACTIONS -->
        <div class="flex flex-wrap items-center gap-3 pt-2 sm:pt-4">
          <button onclick="navigateTo('/watch/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-white text-black px-6 sm:px-8 py-3 sm:py-3.5 rounded-md font-bold hover:bg-gray-200 transition active:scale-95 shadow-xl text-sm sm:text-base">
            <i class="fa-solid fa-play text-base sm:text-lg"></i>
            <span>${hasResume ? 'Lanjutkan Menonton (' + formatTime(progressInfo.currentTime) + ')' : 'Putar Film'}</span>
          </button>
          <button onclick="showMovieModal('${featured.slug}')" class="flex items-center justify-center space-x-2 bg-gray-800/80 sm:bg-gray-700/80 backdrop-blur text-white px-5 sm:px-7 py-3 sm:py-3.5 rounded-md font-semibold hover:bg-gray-600 transition active:scale-95 text-sm sm:text-base">
            <i class="fa-solid fa-circle-info text-base sm:text-lg"></i>
            <span>Selengkapnya</span>
          </button>
          <button onclick="toggleMyList('${featured.id}')" class="flex items-center justify-center space-x-2 bg-gray-900/80 border border-gray-700 text-white px-4 py-3 sm:py-3.5 rounded-md font-semibold hover:border-red-600 transition active:scale-95 text-sm sm:text-base" title="Daftar Saya">
            <i class="fa-solid ${isFeaturedInList ? 'fa-check text-red-500' : 'fa-plus'}"></i>
            <span class="hidden sm:inline">${isFeaturedInList ? 'Tersimpan' : 'Daftar Saya'}</span>
          </button>
        </div>

        ${hasResume ? `
          <div class="w-full max-w-sm pt-2">
            <div class="flex justify-between text-[11px] text-gray-400 mb-1">
              <span>Progress Tontonan</span>
              <span>${progressInfo.percent}%</span>
            </div>
            <div class="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
              <div class="bg-red-600 h-full rounded-full" style="width: ${progressInfo.percent}%"></div>
            </div>
          </div>
        ` : ''}
      </div>
    </header>

    <!-- NETFLIX THEMATIC FRANCHISE & COLLECTION SHELVES -->
    <section class="px-4 sm:px-8 md:px-12 py-6 md:py-8 relative z-20 space-y-6">
      <div class="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
        <span class="text-xs text-gray-400 font-semibold uppercase tracking-wider mr-2 hidden sm:inline">Koleksi:</span>
        ${categories.map(cat => `
          <button onclick="setCategoryFilter('${cat.id}')" 
                  class="px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all duration-200 border ${state.activeCategory === cat.id ? 'bg-red-600 text-white border-red-600 shadow-md shadow-red-600/30 font-bold' : 'bg-gray-900/90 text-gray-300 border-gray-800 hover:border-gray-600 hover:text-white'}">
            ${cat.label}
          </button>
        `).join('')}
      </div>

      <div>
        <div class="flex items-center justify-between mb-4 sm:mb-6">
          <h2 class="text-base sm:text-xl md:text-2xl font-bold tracking-wide text-white flex items-center space-x-2">
            <span>${collectionTitle}</span>
            <span class="text-xs font-normal text-gray-500 font-mono">(${filteredMovies.length})</span>
          </h2>
          <span class="text-[11px] sm:text-xs text-red-400 font-bold uppercase tracking-wider flex items-center space-x-1.5 bg-red-950/40 border border-red-800/60 px-2.5 py-1 rounded-md shadow-sm">
            <i class="fa-solid fa-fire text-red-500 text-xs"></i>
            <span>${collectionBadge}</span>
          </span>
        </div>

        ${filteredMovies.length === 0 ? `
          <div class="text-center py-16 space-y-3 bg-gray-950/60 border border-gray-800/80 rounded-xl">
            <i class="fa-solid fa-magnifying-glass text-3xl text-gray-600"></i>
            <p class="text-sm text-gray-400">Tidak ada film yang cocok dengan kriteria pencarian.</p>
            <button onclick="setCategoryFilter('all'); clearSearch()" class="bg-red-600 text-white text-xs px-4 py-2 rounded font-bold hover:bg-red-700 transition">Lihat Semua Film</button>
          </div>
        ` : `
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4 md:gap-5">
            ${filteredMovies.map(movie => {
              const p = state.watchProgress[movie.id] || state.watchProgress[movie.slug];
              const isInList = state.myList.includes(movie.id) || state.myList.includes(movie.slug);
              return `
              <div onclick="showMovieModal('${movie.slug}')" class="group relative rounded-lg overflow-hidden bg-gray-900 cursor-pointer transition-all duration-300 hover:scale-105 hover:z-30 hover:shadow-2xl hover:shadow-red-600/20 border border-gray-800 hover:border-red-600 flex flex-col">
                <div class="aspect-[2/3] w-full bg-cover bg-center relative" style="background-image: url('${movie.poster}');">
                  <div class="absolute top-1.5 left-1.5 sm:top-2 sm:left-2 flex flex-col gap-1">
                    <span class="bg-red-600 text-[9px] sm:text-[10px] font-black px-1.5 py-0.5 rounded uppercase text-white">${movie.quality || '1080p'}</span>
                    <span class="bg-yellow-500 text-black text-[9px] sm:text-[10px] font-extrabold px-1.5 py-0.5 rounded">SUB INDO</span>
                  </div>
                  <button onclick="event.stopPropagation(); toggleMyList('${movie.id}')" class="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 w-7 h-7 rounded-full bg-black/70 hover:bg-red-600 text-white flex items-center justify-center transition border border-gray-700 hover:border-red-600" title="Daftar Saya">
                    <i class="fa-solid ${isInList ? 'fa-check text-red-400 hover:text-white' : 'fa-plus'} text-xs"></i>
                  </button>
                  ${p && p.percent > 0 ? `
                    <div class="absolute bottom-0 inset-x-0 bg-black/70 p-1">
                      <div class="w-full bg-gray-700 h-1 rounded-full overflow-hidden">
                        <div class="bg-red-600 h-full" style="width: ${p.percent}%"></div>
                      </div>
                    </div>
                  ` : ''}
                </div>
                <div class="p-2.5 sm:p-3.5 bg-gradient-to-t from-black via-black/90 to-transparent flex-1 flex flex-col justify-between">
                  <h3 class="font-bold text-xs sm:text-sm text-white truncate group-hover:text-red-500 transition">${movie.title}</h3>
                  <div class="flex items-center justify-between text-[10px] sm:text-[11px] text-gray-400 mt-1">
                    <span class="text-green-400 font-semibold">${movie.matchScore || '98%'}</span>
                    <span>${movie.year || '2023'}</span>
                  </div>
                </div>
              </div>
            `}).join('')}
          </div>
        `}
      </div>
    </section>
  `;
}

// --- NETFLIX QUICK PREVIEW MODAL (ZERO PAGE RELOAD POPUP) ---
export function showMovieModal(slug) {
  const modalId = 'movieDetailModal';
  let modal = document.getElementById(modalId);
  if (!modal) {
    modal = document.createElement('div');
    modal.id = modalId;
    document.body.appendChild(modal);
  }

  const movie = state.moviesData.find(m => m.slug === slug || m.id === slug) || state.moviesData[0];
  if (!movie) return;

  const progressInfo = state.watchProgress[movie.id] || state.watchProgress[movie.slug];
  const isInList = state.myList.includes(movie.id) || state.myList.includes(movie.slug);
  const genres = Array.isArray(movie.genres) ? movie.genres : [];
  const cast = Array.isArray(movie.cast) ? movie.cast : [];
  const director = movie.director || 'Sutradara';
  const synopsis = movie.synopsis || 'Sinopsis belum tersedia.';

  modal.innerHTML = `
    <div class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto" onclick="if(event.target === this) document.getElementById('${modalId}').remove()">
      <div class="bg-gray-950 border border-gray-800 rounded-2xl max-w-3xl w-full overflow-hidden shadow-2xl relative my-auto animate-fade-in text-white">
        
        <!-- Modal Backdrop Header (16:9 Banner with Close Button) -->
        <div class="relative h-60 sm:h-80 md:h-96 w-full bg-cover bg-[center_top]" style="background-image: url('${movie.backdrop || movie.poster}');">
          <div class="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/40 to-transparent"></div>
          
          <!-- Close Button -->
          <button onclick="document.getElementById('${modalId}').remove()" class="absolute top-3 right-3 w-9 h-9 rounded-full bg-black/70 hover:bg-red-600 text-white flex items-center justify-center transition border border-gray-700 shadow-lg text-sm z-20">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <!-- Banner Floating Actions -->
          <div class="absolute bottom-4 left-4 sm:left-8 right-4 sm:right-8 flex flex-col space-y-2 z-10">
            <h2 class="text-xl sm:text-3xl md:text-4xl font-extrabold text-white leading-tight drop-shadow-lg">${movie.title}</h2>
            
            <div class="flex flex-wrap items-center gap-3 pt-1">
              <button onclick="document.getElementById('${modalId}').remove(); navigateTo('/watch/${movie.slug}')" class="flex items-center space-x-2 bg-white text-black px-6 sm:px-8 py-2.5 sm:py-3 rounded-md font-bold hover:bg-gray-200 transition active:scale-95 shadow-xl text-xs sm:text-sm">
                <i class="fa-solid fa-play text-sm"></i>
                <span>${progressInfo && progressInfo.currentTime > 10 ? 'Lanjutkan (' + formatTime(progressInfo.currentTime) + ')' : 'Putar Film'}</span>
              </button>

              <button onclick="toggleMyList('${movie.id}')" class="flex items-center space-x-2 bg-gray-900/80 border border-gray-700 text-white px-4 py-2.5 sm:py-3 rounded-md font-semibold hover:border-red-600 transition active:scale-95 text-xs sm:text-sm">
                <i class="fa-solid ${isInList ? 'fa-check text-red-500' : 'fa-plus'}"></i>
                <span>${isInList ? 'Tersimpan' : 'Daftar Saya'}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Modal Body Info & Metadata -->
        <div class="p-4 sm:p-8 space-y-5">
          <div class="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-300">
            <span class="text-green-400 font-bold">${movie.matchScore || '98%'} Match</span>
            <span class="bg-gray-800 text-white text-[10px] px-2 py-0.5 rounded font-bold">${movie.year || '2023'}</span>
            <span class="border border-gray-700 text-gray-300 text-[10px] px-1.5 py-0.2 rounded font-semibold">${movie.ageRating || '13+'}</span>
            <span>${movie.duration || '2 Jam'}</span>
            <span class="bg-red-600 text-white text-[10px] px-2 py-0.5 rounded font-black uppercase tracking-wider">${movie.quality || '1080p BluRay'}</span>
            <span class="bg-yellow-500 text-black text-[10px] px-2 py-0.5 rounded font-extrabold">SUB INDO</span>
          </div>

          <p class="text-gray-300 text-xs sm:text-sm leading-relaxed">${synopsis}</p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-gray-400 pt-3 border-t border-gray-800/80">
            <div><span class="text-gray-500">Sutradara:</span> <span class="text-gray-200 font-semibold">${director}</span></div>
            <div><span class="text-gray-500">Pemeran:</span> <span class="text-gray-200 font-semibold">${cast.join(', ')}</span></div>
            <div><span class="text-gray-500">Genre:</span> <span class="text-gray-200 font-semibold">${genres.join(' • ')}</span></div>
            <div><span class="text-gray-500">Audio:</span> <span class="text-cyan-400 font-semibold">${movie.audio || 'Dolby AAC 5.1'}</span></div>
          </div>
        </div>

      </div>
    </div>
  `;
}

export function renderMovieDetailPage(slug) {
  const movie = state.moviesData.find(m => m.slug === slug || m.id === slug) || state.moviesData[0];
  const main = document.getElementById('app-root');
  const progressInfo = state.watchProgress[movie.id] || state.watchProgress[movie.slug];
  const isInList = state.myList.includes(movie.id) || state.myList.includes(movie.slug);

  main.innerHTML = `
    <div class="min-h-screen pt-16 sm:pt-20 px-4 sm:px-8 md:px-12 pb-16 max-w-6xl mx-auto space-y-6 sm:space-y-8">
      <button onclick="navigateTo('/')" class="text-gray-400 hover:text-white flex items-center space-x-2 text-xs sm:text-sm transition">
        <i class="fa-solid fa-arrow-left"></i>
        <span>Kembali ke Beranda</span>
      </button>

      <div class="relative rounded-xl sm:rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 shadow-2xl">
        <div class="relative h-64 sm:h-80 md:h-[420px] w-full bg-cover bg-[center_top]" style="background-image: url('${movie.backdrop}');">
          <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent"></div>
        </div>

        <div class="p-4 sm:p-6 md:p-10 -mt-16 sm:-mt-24 relative z-10 grid grid-cols-1 md:grid-cols-4 gap-6 md:gap-8 items-start">
          <div class="w-36 sm:w-48 md:w-full aspect-[2/3] rounded-lg sm:rounded-xl overflow-hidden shadow-2xl border border-gray-700 bg-black mx-auto md:mx-0">
            <img src="${movie.poster}" alt="${movie.title}" class="w-full h-full object-cover">
          </div>

          <div class="md:col-span-3 space-y-4 sm:space-y-5">
            <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
              <span class="bg-red-600 text-white text-[10px] sm:text-xs px-2.5 py-0.5 rounded font-black uppercase">FULL HD 1080P</span>
              <span class="bg-yellow-500 text-black text-[10px] sm:text-xs px-2 py-0.5 rounded font-extrabold">SUB INDONESIA</span>
              <span class="bg-gray-800 text-gray-300 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">${movie.audio}</span>
            </div>

            <h1 class="text-xl sm:text-3xl md:text-4xl font-extrabold text-white leading-tight">${movie.title}</h1>

            <div class="flex flex-wrap items-center gap-3 sm:gap-4 text-xs sm:text-sm text-gray-300">
              <span class="text-green-400 font-bold">${movie.matchScore} Match</span>
              <span>Tahun: <b>${movie.year}</b></span>
              <span>Durasi: <b>${movie.duration}</b></span>
              <span>Rating: <b>${movie.ageRating}</b></span>
            </div>

            <div class="flex flex-wrap items-center gap-3 pt-2">
              <button onclick="navigateTo('/watch/${movie.slug}')" class="flex-1 sm:flex-initial flex items-center justify-center space-x-3 bg-red-600 hover:bg-red-700 text-white px-8 py-3.5 rounded-lg font-bold transition active:scale-95 shadow-xl shadow-red-600/30 text-sm sm:text-base">
                <i class="fa-solid fa-play"></i>
                <span>${progressInfo && progressInfo.currentTime > 10 ? 'Lanjutkan Menonton (' + formatTime(progressInfo.currentTime) + ')' : 'Mulai Streaming Sekarang'}</span>
              </button>

              <button onclick="toggleMyList('${movie.id}')" class="flex items-center justify-center space-x-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white px-5 py-3.5 rounded-lg font-semibold transition active:scale-95 text-sm sm:text-base">
                <i class="fa-solid ${isInList ? 'fa-check text-red-500' : 'fa-plus'}"></i>
                <span>${isInList ? 'Di Daftar Saya' : 'Tambah ke Daftar'}</span>
              </button>
            </div>

            <div class="space-y-2 pt-2 border-t border-gray-800">
              <h3 class="text-xs sm:text-sm font-bold text-gray-200">Sinopsis Lengkap:</h3>
              <p class="text-xs sm:text-sm text-gray-400 leading-relaxed">${movie.synopsis}</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm text-gray-400 pt-2 border-t border-gray-800">
              <div><span class="text-gray-500">Sutradara:</span> <span class="text-gray-200 font-semibold">${movie.director}</span></div>
              <div><span class="text-gray-500">Pemeran:</span> <span class="text-gray-200 font-semibold">${movie.cast.join(', ')}</span></div>
              <div><span class="text-gray-500">Genre:</span> <span class="text-gray-200 font-semibold">${movie.genres.join(' • ')}</span></div>
              <div><span class="text-gray-500">Subtitle:</span> <span class="text-yellow-400 font-semibold">${movie.subtitle}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function renderWatchPage(slug) {
  const movie = state.moviesData.find(m => m.slug === slug || m.id === slug) || state.moviesData[0];
  const main = document.getElementById('app-root');
  const progressInfo = state.watchProgress[movie.id] || state.watchProgress[movie.slug];

  main.innerHTML = `
    <div class="fixed inset-0 z-50 bg-black flex flex-col justify-between overflow-hidden h-screen w-screen select-none">
      <header class="h-12 sm:h-14 bg-gray-950/95 backdrop-blur px-3 sm:px-6 border-b border-gray-800/80 flex items-center justify-between z-30 flex-shrink-0">
        <div class="flex items-center space-x-3 sm:space-x-4 min-w-0">
          <button onclick="navigateTo('/movie/${movie.slug}')" class="text-gray-300 hover:text-white flex items-center space-x-1.5 font-semibold text-xs sm:text-sm transition flex-shrink-0 bg-gray-800/80 hover:bg-gray-700 px-3 py-1.5 rounded-md">
            <i class="fa-solid fa-arrow-left text-xs sm:text-sm"></i>
            <span class="hidden sm:inline">Kembali</span>
          </button>
          <span class="text-gray-700 hidden sm:inline">|</span>
          <h2 class="text-white font-bold text-xs sm:text-sm md:text-base truncate max-w-[200px] sm:max-w-md">${movie.title}</h2>
          <span class="bg-red-600/90 text-white text-[9px] sm:text-[10px] px-2 py-0.5 rounded font-black tracking-wider uppercase hidden md:inline">1080p BluRay</span>
        </div>

        <div class="flex items-center space-x-2 sm:space-x-3 flex-shrink-0 text-xs">
          <select id="qualitySelect" onchange="changeQuality(this.value)" class="bg-gray-900 text-white text-xs border border-gray-700 rounded px-2 py-1 focus:outline-none focus:border-red-600 cursor-pointer">
            <option value="1080p">1080p BluRay</option>
            <option value="720p">720p HD</option>
            <option value="480p">480p SD</option>
          </select>
          <span class="bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded font-semibold border border-yellow-500/30 text-[10px] sm:text-xs hidden sm:inline">Sub Indo</span>
        </div>
      </header>

      <main class="relative flex-1 w-full h-full flex items-center justify-center p-0 m-0 min-h-0 overflow-hidden bg-black">
        <video id="cinemaPlayer" class="w-full h-full max-w-full max-h-full object-contain bg-black" controls playsinline preload="auto" poster="${movie.backdrop}">
          <source id="videoSource" src="${movie.streamUrl}" type="video/mp4">
          <track id="subTrack" label="Bahasa Indonesia" kind="subtitles" srclang="id" src="${movie.subtitleUrl || '/sub_indo.vtt'}" default>
          Browser Anda tidak mendukung streaming video HTML5.
        </video>
        <div id="subOverlay" class="pointer-events-none absolute bottom-14 sm:bottom-16 md:bottom-20 inset-x-0 flex flex-col items-center justify-center px-4 text-center z-20 transition-all duration-100 select-none"></div>
      </main>

      <footer class="h-10 sm:h-11 bg-gray-950/95 backdrop-blur px-3 sm:px-6 border-t border-gray-800/80 flex items-center justify-between text-[11px] sm:text-xs text-gray-400 flex-shrink-0 z-30">
        <div class="flex items-center space-x-2 sm:space-x-5 truncate">
          <button id="subToggleBtn" onclick="toggleSubtitle()" class="bg-yellow-500 text-black px-2 py-0.5 rounded font-bold border border-yellow-400 text-[10px] sm:text-xs transition cursor-pointer flex items-center space-x-1">
            <i class="fa-solid fa-closed-captioning"></i>
            <span>Sub Indo: ON</span>
          </button>
          <span class="hidden md:inline"><i class="fa-solid fa-bolt text-green-400 text-xs mr-1"></i> P2P Mesh: <b class="text-gray-300">Aktif</b></span>
          <span class="hidden lg:inline"><i class="fa-solid fa-volume-high text-cyan-400 text-xs mr-1"></i> Audio: <b class="text-gray-300">${movie.audio}</b></span>
        </div>
        <div class="flex items-center space-x-3 flex-shrink-0">
          <label class="flex items-center space-x-1 cursor-pointer">
            <span class="hidden sm:inline text-gray-400">Kecepatan:</span>
            <select onchange="changeSpeed(this.value)" class="bg-gray-900 text-white text-[11px] border border-gray-700 rounded px-1.5 py-0.5">
              <option value="0.75">0.75x</option>
              <option value="1" selected>1.0x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2.0x</option>
            </select>
          </label>
          <button onclick="togglePiP()" class="hover:text-white transition flex items-center space-x-1 text-gray-400 hover:text-white" title="Picture-in-Picture">
            <i class="fa-solid fa-clone text-xs"></i>
            <span class="hidden sm:inline">PiP</span>
          </button>
        </div>
      </footer>
    </div>
  `;

  setTimeout(async () => {
    const vid = document.getElementById('cinemaPlayer');
    if (!vid) return;

    await loadSubtitles(movie.subtitleUrl || `/subtitles/${movie.slug}.vtt` || '/sub_indo.vtt');

    if (vid.textTracks && vid.textTracks[0]) vid.textTracks[0].mode = "showing";

    vid.addEventListener('timeupdate', () => {
      if (!state.subtitleEnabled) return;
      const overlay = document.getElementById('subOverlay');
      if (!overlay) return;
      const ct = vid.currentTime;
      const activeCue = state.subtitleCues.find(c => ct >= c.start && ct <= c.end);
      if (activeCue) {
        overlay.innerHTML = `<div class="inline-block bg-black/85 backdrop-blur-sm px-3.5 sm:px-5 py-1 sm:py-1.5 rounded-md text-yellow-300 font-extrabold text-sm sm:text-base md:text-xl lg:text-2xl tracking-wide shadow-2xl border border-black/60 max-w-3xl leading-snug">${activeCue.text}</div>`;
      } else {
        overlay.innerHTML = '';
      }
    });

    vid.addEventListener('loadedmetadata', () => {
      if (progressInfo && progressInfo.currentTime > 5 && progressInfo.currentTime < ((vid.duration || 100) - 30)) {
        vid.currentTime = progressInfo.currentTime;
      }
      vid.play().catch(() => {});
    });

    vid.play().catch(() => {});

    state.progressInterval = setInterval(() => {
      if (vid && !vid.paused && vid.currentTime > 0) {
        saveServerWatchProgress(movie.id, vid.currentTime, vid.duration || 0);
      }
    }, 4000);

    vid.addEventListener('pause', () => saveServerWatchProgress(movie.id, vid.currentTime, vid.duration || 0));
    vid.addEventListener('ended', () => saveServerWatchProgress(movie.id, 0, vid.duration || 0));
  }, 100);
}
