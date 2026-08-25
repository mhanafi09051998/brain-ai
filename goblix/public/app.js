// ===================================================================
// GOBLIX CINEMA: CLIENT-SIDE AUTONOMOUS SPA ROUTER & PRO STREAMER
// Fullstack Vanilla JS • Zero UI Framework Overhead • Mobile & Desktop Responsive
// ===================================================================

let CURRENT_USER = null;
let MOVIES_DATA = [];
let WATCH_PROGRESS = {}; // { [movieId]: { currentTime, duration, percent } }
let PROGRESS_INTERVAL = null;

// -------------------------------------------------------------------
// 1. STATE & AUTHENTICATION MANAGEMENT
// -------------------------------------------------------------------
function getToken() {
  return localStorage.getItem('goblix_token');
}

function setToken(token) {
  if (token) {
    localStorage.setItem('goblix_token', token);
  } else {
    localStorage.removeItem('goblix_token');
  }
}

function getLocalProgress() {
  try {
    return JSON.parse(localStorage.getItem('goblix_progress') || '{}');
  } catch (e) {
    return {};
  }
}

function saveLocalProgress(movieId, currentTime, duration) {
  const local = getLocalProgress();
  local[movieId] = {
    movieId,
    currentTime: Math.floor(currentTime),
    duration: Math.floor(duration),
    percent: Math.min(100, Math.round((currentTime / (duration || 1)) * 100)),
    updatedAt: new Date().toISOString()
  };
  localStorage.setItem('goblix_progress', JSON.stringify(local));
  WATCH_PROGRESS = { ...local, ...WATCH_PROGRESS };
}

async function checkAuthSession() {
  const token = getToken();
  WATCH_PROGRESS = getLocalProgress();

  if (!token) {
    CURRENT_USER = null;
    updateNavbarAuth();
    return;
  }

  try {
    const res = await fetch('/api/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (data.success && data.user) {
      CURRENT_USER = data.user;
      await fetchServerWatchProgress();
    } else {
      setToken(null);
      CURRENT_USER = null;
    }
  } catch (e) {
    CURRENT_USER = null;
  }
  updateNavbarAuth();
}

async function fetchServerWatchProgress() {
  const token = getToken();
  if (!token) return;
  try {
    const res = await fetch('/api/user/progress', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (data.success && data.progress) {
      WATCH_PROGRESS = { ...WATCH_PROGRESS, ...data.progress };
    }
  } catch (e) {}
}

async function saveServerWatchProgress(movieId, currentTime, duration) {
  saveLocalProgress(movieId, currentTime, duration);
  const token = getToken();
  if (!token) return;
  try {
    await fetch('/api/user/progress', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ movieId, currentTime, duration })
    });
  } catch (e) {}
}

function updateNavbarAuth() {
  const container = document.getElementById('nav-auth-container');
  if (!container) return;

  if (CURRENT_USER) {
    container.innerHTML = `
      <div class="flex items-center space-x-2 sm:space-x-3">
        <div class="hidden sm:flex flex-col text-right">
          <span class="text-xs font-bold text-white leading-tight">${CURRENT_USER.name}</span>
          <span class="text-[10px] text-green-400 font-mono">Premium HD</span>
        </div>
        <button onclick="handleLogout()" class="bg-gray-800 hover:bg-red-600/80 text-white text-xs px-2.5 sm:px-3 py-1.5 rounded transition font-semibold border border-gray-700 flex items-center space-x-1.5">
          <i class="fa-solid fa-right-from-bracket text-[11px]"></i>
          <span class="hidden sm:inline">Keluar</span>
        </button>
      </div>
    `;
  } else {
    container.innerHTML = `
      <a href="/login" onclick="event.preventDefault(); navigateTo('/login')" class="text-xs font-bold text-gray-300 hover:text-white px-2 sm:px-3 py-1.5 transition">Masuk</a>
      <a href="/register" onclick="event.preventDefault(); navigateTo('/register')" class="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-3 sm:px-4 py-1.5 sm:py-2 rounded transition shadow-md shadow-red-600/30">Daftar</a>
    `;
  }
}

function handleLogout() {
  setToken(null);
  CURRENT_USER = null;
  updateNavbarAuth();
  navigateTo('/');
}

// -------------------------------------------------------------------
// 2. DATA FETCHER
// -------------------------------------------------------------------
async function fetchMovies() {
  try {
    const res = await fetch('/api/movies');
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      MOVIES_DATA = data.data;
    }
  } catch (e) {
    console.error("[GOBLIX ERROR] Failed to fetch movies:", e);
  }
}

// -------------------------------------------------------------------
// 3. SPA ROUTING SYSTEM
// -------------------------------------------------------------------
function navigateTo(path) {
  if (PROGRESS_INTERVAL) {
    clearInterval(PROGRESS_INTERVAL);
    PROGRESS_INTERVAL = null;
  }
  window.history.pushState({}, '', path);
  handleRoute();
}

window.addEventListener('popstate', () => {
  if (PROGRESS_INTERVAL) {
    clearInterval(PROGRESS_INTERVAL);
    PROGRESS_INTERVAL = null;
  }
  handleRoute();
});

async function handleRoute() {
  window.scrollTo({ top: 0, behavior: 'instant' });
  const path = window.location.pathname;

  const navEl = document.getElementById('navbar');
  const footerEl = document.querySelector('footer');

  if (path.startsWith('/watch/')) {
    if (navEl) navEl.classList.add('hidden');
    if (footerEl) footerEl.classList.add('hidden');
  } else {
    if (navEl) navEl.classList.remove('hidden');
    if (footerEl) footerEl.classList.remove('hidden');
  }

  if (MOVIES_DATA.length === 0) {
    await fetchMovies();
  }

  if (path === '/' || path === '') {
    renderHomePage();
  } else if (path.startsWith('/movie/')) {
    const slug = path.replace('/movie/', '');
    renderMovieDetailPage(slug);
  } else if (path.startsWith('/watch/')) {
    const slug = path.replace('/watch/', '');
    renderWatchPage(slug);
  } else if (path === '/login') {
    renderLoginPage();
  } else if (path === '/register') {
    renderRegisterPage();
  } else {
    renderHomePage();
  }
}

// -------------------------------------------------------------------
// 4. VIEW RENDERERS
// -------------------------------------------------------------------

// --- 4A. HOMEPAGE VIEW ---
function renderHomePage() {
  const main = document.getElementById('app-root');
  const featured = MOVIES_DATA[0] || {};
  const progressInfo = WATCH_PROGRESS[featured.id] || WATCH_PROGRESS[featured.slug];
  const hasResume = progressInfo && progressInfo.currentTime > 10;

  main.innerHTML = `
    <!-- HERO BANNER (RESPONSIVE) -->
    <header class="relative w-full min-h-[70vh] sm:min-h-[85vh] flex items-end pb-12 sm:pb-20 px-4 sm:px-8 md:px-12 bg-cover bg-center overflow-hidden" 
            style="background-image: url('${featured.backdrop || featured.poster}');">
      <div class="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/70 to-black/30"></div>
      <div class="absolute inset-0 bg-gradient-to-r from-[#141414] via-[#141414]/80 to-transparent w-full md:w-3/4"></div>

      <div class="relative z-10 max-w-2xl space-y-3 sm:space-y-4 pt-20">
        
        <div class="flex items-center space-x-2">
          <span class="bg-red-600 text-white text-[10px] sm:text-xs px-2.5 py-0.5 rounded font-black tracking-widest uppercase">GOBLIX ORIGINAL</span>
          <span class="border border-white/40 text-gray-200 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">${featured.quality || '1080p'}</span>
          <span class="bg-yellow-500 text-black text-[10px] sm:text-xs px-2 py-0.5 rounded font-extrabold">SUB INDO</span>
        </div>

        <h1 class="text-2xl sm:text-4xl md:text-6xl font-extrabold tracking-tight drop-shadow-md leading-tight text-white">
          ${featured.title || 'Loading...'}
        </h1>

        <div class="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm text-gray-300 font-medium">
          <span class="text-green-400 font-bold">${featured.matchScore} Match</span>
          <span>${featured.year}</span>
          <span class="border border-gray-500 px-1.5 py-0.2 rounded text-[10px]">${featured.ageRating}</span>
          <span>${featured.duration}</span>
          <span class="bg-gray-800 px-2 py-0.5 rounded text-white font-bold hidden sm:inline">${featured.audio}</span>
        </div>

        <p class="text-gray-300 text-xs sm:text-sm md:text-base line-clamp-3 md:line-clamp-4 leading-relaxed drop-shadow">
          ${featured.synopsis || ''}
        </p>

        <!-- STREAMING & RESUME ACTIONS -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2 sm:pt-4">
          <button onclick="navigateTo('/watch/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-white text-black px-6 sm:px-8 py-3 sm:py-3.5 rounded-md font-bold hover:bg-gray-200 transition active:scale-95 shadow-xl text-sm sm:text-base">
            <i class="fa-solid fa-play text-base sm:text-lg"></i>
            <span>${hasResume ? 'Lanjutkan Menonton (' + formatTime(progressInfo.currentTime) + ')' : 'Putar Film'}</span>
          </button>

          <button onclick="navigateTo('/movie/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-gray-800/80 sm:bg-gray-700/80 backdrop-blur text-white px-5 sm:px-7 py-3 sm:py-3.5 rounded-md font-semibold hover:bg-gray-600 transition active:scale-95 text-sm sm:text-base">
            <i class="fa-solid fa-circle-info text-base sm:text-lg"></i>
            <span>Selengkapnya</span>
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

    <!-- SINGLE MOVIE SHOWCASE CATALOG -->
    <section class="px-4 sm:px-8 md:px-12 py-8 md:py-12 relative z-20 space-y-8">
      <div>
        <div class="flex items-center justify-between mb-4 sm:mb-6">
          <h2 class="text-base sm:text-xl md:text-2xl font-bold tracking-wide text-white">
            Koleksi Film Pilihan 1080p BluRay Subtitle Indonesia
          </h2>
          <span class="text-[11px] sm:text-xs text-red-500 font-semibold uppercase tracking-wider">Streaming HD</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4 md:gap-5">
          ${MOVIES_DATA.map(movie => {
            const p = WATCH_PROGRESS[movie.id] || WATCH_PROGRESS[movie.slug];
            return `
            <div onclick="navigateTo('/movie/${movie.slug}')" class="group relative rounded-lg overflow-hidden bg-gray-900 cursor-pointer transition-all duration-300 hover:scale-105 hover:z-30 hover:shadow-2xl hover:shadow-red-600/20 border border-gray-800 hover:border-red-600 flex flex-col">
              <div class="aspect-[2/3] w-full bg-cover bg-center relative" style="background-image: url('${movie.poster}');">
                <div class="absolute top-1.5 left-1.5 sm:top-2 sm:left-2 flex flex-col gap-1">
                  <span class="bg-red-600 text-[9px] sm:text-[10px] font-black px-1.5 py-0.5 rounded uppercase text-white">${movie.quality}</span>
                  <span class="bg-yellow-500 text-black text-[9px] sm:text-[10px] font-extrabold px-1.5 py-0.5 rounded">SUB INDO</span>
                </div>
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
                  <span class="text-green-400 font-semibold">${movie.matchScore}</span>
                  <span>${movie.year}</span>
                </div>
              </div>
            </div>
          `}).join('')}
        </div>
      </div>
    </section>
  `;
}

// --- 4B. MOVIE DETAIL VIEW ---
function renderMovieDetailPage(slug) {
  const movie = MOVIES_DATA.find(m => m.slug === slug || m.id === slug) || MOVIES_DATA[0];
  const main = document.getElementById('app-root');
  const progressInfo = WATCH_PROGRESS[movie.id] || WATCH_PROGRESS[movie.slug];

  main.innerHTML = `
    <div class="min-h-screen pt-16 sm:pt-20 px-4 sm:px-8 md:px-12 pb-16 max-w-6xl mx-auto space-y-6 sm:space-y-8">
      
      <!-- Back Navigation -->
      <button onclick="navigateTo('/')" class="text-gray-400 hover:text-white flex items-center space-x-2 text-xs sm:text-sm transition">
        <i class="fa-solid fa-arrow-left"></i>
        <span>Kembali ke Beranda</span>
      </button>

      <!-- Main Detail Banner Card -->
      <div class="relative rounded-xl sm:rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 shadow-2xl">
        <div class="relative h-64 sm:h-80 md:h-[420px] w-full bg-cover bg-[center_top]" style="background-image: url('${movie.backdrop}');">
          <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent"></div>
        </div>

        <div class="p-4 sm:p-6 md:p-10 -mt-16 sm:-mt-24 relative z-10 grid grid-cols-1 md:grid-cols-4 gap-6 md:gap-8 items-start">
          
          <!-- Poster -->
          <div class="w-36 sm:w-48 md:w-full aspect-[2/3] rounded-lg sm:rounded-xl overflow-hidden shadow-2xl border border-gray-700 bg-black mx-auto md:mx-0">
            <img src="${movie.poster}" alt="${movie.title}" class="w-full h-full object-cover">
          </div>

          <!-- Info & Actions -->
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

            <!-- Action Button -->
            <div class="pt-2">
              <button onclick="navigateTo('/watch/${movie.slug}')" class="w-full sm:w-auto flex items-center justify-center space-x-3 bg-red-600 hover:bg-red-700 text-white px-8 py-3.5 rounded-lg font-bold transition active:scale-95 shadow-xl shadow-red-600/30 text-sm sm:text-base">
                <i class="fa-solid fa-play"></i>
                <span>${progressInfo && progressInfo.currentTime > 10 ? 'Lanjutkan Menonton (' + formatTime(progressInfo.currentTime) + ')' : 'Mulai Streaming Sekarang'}</span>
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

// --- 4C. CINEMA STREAMING PLAYER VIEW (PRO CINEMA SUITE - ZERO SCROLL DESKTOP FIT) ---
function renderWatchPage(slug) {
  const movie = MOVIES_DATA.find(m => m.slug === slug || m.id === slug) || MOVIES_DATA[0];
  const main = document.getElementById('app-root');
  const progressInfo = WATCH_PROGRESS[movie.id] || WATCH_PROGRESS[movie.slug];

  main.innerHTML = `
    <div class="fixed inset-0 z-50 bg-black flex flex-col justify-between overflow-hidden h-screen w-screen select-none">
      
      <!-- Top Cinema Header (Compact & Responsive) -->
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
          <!-- Quality Selector -->
          <select id="qualitySelect" onchange="changeQuality(this.value)" class="bg-gray-900 text-white text-xs border border-gray-700 rounded px-2 py-1 focus:outline-none focus:border-red-600 cursor-pointer">
            <option value="1080p">1080p BluRay</option>
            <option value="720p">720p HD</option>
            <option value="480p">480p SD</option>
          </select>
          <span class="bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded font-semibold border border-yellow-500/30 text-[10px] sm:text-xs hidden sm:inline">Sub Indo</span>
        </div>
      </header>

      <!-- Main Video Stream Area (Zero-Scroll Auto-Fitted to Viewport) -->
      <main class="relative flex-1 w-full flex items-center justify-center p-2 sm:p-4 min-h-0 overflow-hidden bg-black">
        <div class="relative w-full h-full max-w-[1400px] flex items-center justify-center">
          <div class="relative max-h-full max-w-full aspect-video flex items-center justify-center bg-black rounded-lg sm:rounded-xl overflow-hidden shadow-2xl border border-gray-800/80 group" style="max-height: calc(100vh - 110px); width: auto;">
            <video id="cinemaPlayer" class="w-full h-full max-h-full object-contain" controls playsinline preload="auto" poster="${movie.backdrop}">
              <source id="videoSource" src="${movie.streamUrl}" type="video/mp4">
              <track id="subTrack" label="Bahasa Indonesia" kind="subtitles" srclang="id" src="/sub_indo.vtt" default>
              Browser Anda tidak mendukung streaming video HTML5.
            </video>
          </div>
        </div>
      </main>

      <!-- Cinema Info Footer (Compact Pro Bar) -->
      <footer class="h-10 sm:h-11 bg-gray-950/95 backdrop-blur px-3 sm:px-6 border-t border-gray-800/80 flex items-center justify-between text-[11px] sm:text-xs text-gray-400 flex-shrink-0 z-30">
        <div class="flex items-center space-x-3 sm:space-x-6 truncate">
          <span><i class="fa-solid fa-closed-captioning text-yellow-400 text-xs mr-1"></i> Subtitle: <b class="text-gray-300">Bahasa Indonesia (Resmi)</b></span>
          <span class="hidden md:inline"><i class="fa-solid fa-bolt text-green-400 text-xs mr-1"></i> P2P Mesh Caching: <b class="text-gray-300">Aktif</b></span>
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

  // Auto-resume and playback listener
  setTimeout(() => {
    const vid = document.getElementById('cinemaPlayer');
    if (!vid) return;

    vid.addEventListener('loadedmetadata', () => {
      if (progressInfo && progressInfo.currentTime > 5 && progressInfo.currentTime < ((vid.duration || 100) - 30)) {
        vid.currentTime = progressInfo.currentTime;
      }
      vid.play().catch(() => {});
    });

    vid.play().catch(() => {});

    // Periodic Watch Progress Auto-Save
    PROGRESS_INTERVAL = setInterval(() => {
      if (vid && !vid.paused && vid.currentTime > 0) {
        saveServerWatchProgress(movie.id, vid.currentTime, vid.duration || 0);
      }
    }, 4000);

    vid.addEventListener('pause', () => {
      saveServerWatchProgress(movie.id, vid.currentTime, vid.duration || 0);
    });

    vid.addEventListener('ended', () => {
      saveServerWatchProgress(movie.id, 0, vid.duration || 0);
    });
  }, 100);
}

function changeSpeed(val) {
  const vid = document.getElementById('cinemaPlayer');
  if (vid) vid.playbackRate = parseFloat(val);
}

function changeQuality(val) {
  const vid = document.getElementById('cinemaPlayer');
  if (!vid) return;
  const curr = vid.currentTime;
  const isPaused = vid.paused;
  // Adaptive buffer reload
  vid.load();
  vid.currentTime = curr;
  if (!isPaused) vid.play().catch(() => {});
}

async function togglePiP() {
  const vid = document.getElementById('cinemaPlayer');
  if (!vid) return;
  if (document.pictureInPictureElement) {
    await document.exitPictureInPicture();
  } else {
    await vid.requestPictureInPicture();
  }
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return "00:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// --- 4D. AUTHENTICATION: LOGIN VIEW ---
function renderLoginPage() {
  const main = document.getElementById('app-root');
  main.innerHTML = `
    <div class="min-h-[85vh] flex items-center justify-center px-4 py-12 sm:py-16">
      <div class="w-full max-w-md bg-black/90 border border-gray-800 p-6 sm:p-10 rounded-xl sm:rounded-2xl shadow-2xl space-y-6 backdrop-blur">
        
        <div class="space-y-1.5">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Masuk ke Goblix</h1>
          <p class="text-xs text-gray-400">Akses streaming film 1080p BluRay kualitas bioskop.</p>
        </div>

        <div id="auth-alert" class="hidden p-3 rounded bg-red-900/50 border border-red-600 text-red-200 text-xs font-semibold"></div>

        <form id="loginForm" onsubmit="submitLogin(event)" class="space-y-4">
          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Email</label>
            <input type="email" id="loginEmail" required placeholder="nama@email.com" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Kata Sandi</label>
            <input type="password" id="loginPassword" required placeholder="••••••••" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <button type="submit" id="loginBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-lg text-sm transition shadow-lg shadow-red-600/30 flex items-center justify-center space-x-2">
            <span>Masuk</span>
          </button>
        </form>

        <div class="text-center text-xs text-gray-400 pt-2 border-t border-gray-800">
          Belum punya akun? 
          <a href="/register" onclick="event.preventDefault(); navigateTo('/register')" class="text-white hover:text-red-500 font-bold ml-1 transition">Daftar sekarang</a>
        </div>
      </div>
    </div>
  `;
}

// --- 4E. AUTHENTICATION: REGISTER VIEW ---
function renderRegisterPage() {
  const main = document.getElementById('app-root');
  main.innerHTML = `
    <div class="min-h-[85vh] flex items-center justify-center px-4 py-12 sm:py-16">
      <div class="w-full max-w-md bg-black/90 border border-gray-800 p-6 sm:p-10 rounded-xl sm:rounded-2xl shadow-2xl space-y-6 backdrop-blur">
        
        <div class="space-y-1.5">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Daftar Akun Baru</h1>
          <p class="text-xs text-gray-400">Mulai streaming film kualitas 1080p BluRay gratis.</p>
        </div>

        <div id="auth-alert" class="hidden p-3 rounded bg-red-900/50 border border-red-600 text-red-200 text-xs font-semibold"></div>

        <form id="registerForm" onsubmit="submitRegister(event)" class="space-y-4">
          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Nama Lengkap</label>
            <input type="text" id="regName" required placeholder="Nama Anda" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Email</label>
            <input type="email" id="regEmail" required placeholder="nama@email.com" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Kata Sandi (Minimal 6 Karakter)</label>
            <input type="password" id="regPassword" required minlength="6" placeholder="••••••••" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <button type="submit" id="registerBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-lg text-sm transition shadow-lg shadow-red-600/30 flex items-center justify-center space-x-2">
            <span>Buat Akun</span>
          </button>
        </form>

        <div class="text-center text-xs text-gray-400 pt-2 border-t border-gray-800">
          Sudah memiliki akun? 
          <a href="/login" onclick="event.preventDefault(); navigateTo('/login')" class="text-white hover:text-red-500 font-bold ml-1 transition">Masuk di sini</a>
        </div>
      </div>
    </div>
  `;
}

// -------------------------------------------------------------------
// 5. AUTH SUBMIT HANDLERS
// -------------------------------------------------------------------
async function submitLogin(e) {
  e.preventDefault();
  const alertEl = document.getElementById('auth-alert');
  const btn = document.getElementById('loginBtn');
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  alertEl.classList.add('hidden');
  btn.disabled = true;
  btn.innerText = "Memproses...";

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.success && data.token) {
      setToken(data.token);
      CURRENT_USER = data.user;
      updateNavbarAuth();
      await fetchServerWatchProgress();
      navigateTo('/');
    } else {
      alertEl.innerText = data.error || 'Login gagal.';
      alertEl.classList.remove('hidden');
    }
  } catch (err) {
    alertEl.innerText = 'Gagal terhubung ke server.';
    alertEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerText = "Masuk";
  }
}

async function submitRegister(e) {
  e.preventDefault();
  const alertEl = document.getElementById('auth-alert');
  const btn = document.getElementById('registerBtn');
  const name = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;

  alertEl.classList.add('hidden');
  btn.disabled = true;
  btn.innerText = "Mendaftarkan...";

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();

    if (data.success && data.token) {
      setToken(data.token);
      CURRENT_USER = data.user;
      updateNavbarAuth();
      navigateTo('/');
    } else {
      alertEl.innerText = data.error || 'Pendaftaran gagal.';
      alertEl.classList.remove('hidden');
    }
  } catch (err) {
    alertEl.innerText = 'Gagal terhubung ke server.';
    alertEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerText = "Buat Akun";
  }
}

// -------------------------------------------------------------------
// 6. INITIALIZATION
// -------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuthSession();
  await handleRoute();
});
