// ===================================================================
// GOBLIX CINEMA: CLIENT-SIDE AUTONOMOUS SPA ROUTER & NETFLIX CINEMA SUITE
// Fullstack Vanilla JS • Zero UI Framework Overhead • Mobile & Desktop Responsive
// ===================================================================

let CURRENT_USER = null;
let MOVIES_DATA = [];
let WATCH_PROGRESS = {}; // { [movieId]: { currentTime, duration, percent } }
let PROGRESS_INTERVAL = null;

// Netflix Suite State
let ACTIVE_CATEGORY = 'all';
let SEARCH_QUERY = '';
let MY_LIST = [];

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

function loadMyList() {
  try {
    MY_LIST = JSON.parse(localStorage.getItem('goblix_my_list') || '[]');
  } catch (e) {
    MY_LIST = [];
  }
  updateMyListBadge();
}

function updateMyListBadge() {
  const badge = document.getElementById('nav-list-badge');
  if (badge) {
    badge.innerText = MY_LIST.length;
  }
}

function toggleMyList(movieId) {
  const idx = MY_LIST.indexOf(movieId);
  if (idx > -1) {
    MY_LIST.splice(idx, 1);
  } else {
    MY_LIST.push(movieId);
  }
  localStorage.setItem('goblix_my_list', JSON.stringify(MY_LIST));
  updateMyListBadge();
  if (window.location.pathname === '/' || window.location.pathname === '') {
    renderHomePage();
  }
}

async function checkAuthSession() {
  const token = getToken();
  WATCH_PROGRESS = getLocalProgress();
  loadMyList();

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
      <!-- Netflix User Profile Avatar & Dropdown -->
      <div class="relative group">
        <button class="flex items-center space-x-2 focus:outline-none py-1">
          <div class="w-8 h-8 rounded bg-red-600 flex items-center justify-center font-bold text-xs text-white border border-red-500 shadow-md">
            ${CURRENT_USER.name ? CURRENT_USER.name.charAt(0).toUpperCase() : 'G'}
          </div>
          <i class="fa-solid fa-caret-down text-gray-400 text-xs transition group-hover:rotate-180 hidden sm:inline"></i>
        </button>
        <div class="absolute right-0 top-full mt-2 w-48 bg-gray-950/95 border border-gray-800 rounded-md shadow-2xl py-2 hidden group-hover:block backdrop-blur z-50 text-xs">
          <div class="px-4 py-2 border-b border-gray-800">
            <p class="font-bold text-white truncate">${CURRENT_USER.name}</p>
            <p class="text-[10px] text-green-400 font-mono">Paket HD Sinema</p>
          </div>
          <a href="javascript:void(0)" onclick="showMyListModal()" class="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white transition">Daftar Saya (${MY_LIST.length})</a>
          <a href="javascript:void(0)" onclick="handleLogout()" class="block px-4 py-2 text-red-400 hover:bg-red-600 hover:text-white transition border-t border-gray-800 font-semibold">Keluar dari Goblix</a>
        </div>
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
// 2. DATA FETCHER & NETFLIX SEARCH / CATEGORY CONTROLLERS
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

function toggleSearchInput() {
  const wrap = document.getElementById('searchWrapper');
  const input = document.getElementById('netflixSearchInput');
  const closeBtn = document.getElementById('searchCloseBtn');
  
  if (!wrap || !input) return;

  if (wrap.classList.contains('search-box-active')) {
    if (!input.value.trim()) {
      wrap.classList.remove('search-box-active');
      input.classList.remove('w-44', 'sm:w-60', 'opacity-100');
      input.classList.add('w-0', 'opacity-0');
      if (closeBtn) closeBtn.classList.add('hidden');
    }
  } else {
    wrap.classList.add('search-box-active');
    input.classList.remove('w-0', 'opacity-0');
    input.classList.add('w-44', 'sm:w-60', 'opacity-100');
    input.focus();
    if (closeBtn) closeBtn.classList.remove('hidden');
  }
}

function handleSearchQuery(q) {
  SEARCH_QUERY = q.toLowerCase().trim();
  const closeBtn = document.getElementById('searchCloseBtn');
  if (closeBtn) {
    if (SEARCH_QUERY) closeBtn.classList.remove('hidden');
    else closeBtn.classList.add('hidden');
  }

  if (window.location.pathname !== '/' && window.location.pathname !== '') {
    navigateTo('/');
  } else {
    renderHomePage();
  }
}

function clearSearch() {
  SEARCH_QUERY = '';
  const input = document.getElementById('netflixSearchInput');
  if (input) input.value = '';
  toggleSearchInput();
  renderHomePage();
}

function setCategoryFilter(category) {
  ACTIVE_CATEGORY = category;
  SEARCH_QUERY = '';
  const input = document.getElementById('netflixSearchInput');
  if (input) input.value = '';
  if (window.location.pathname !== '/' && window.location.pathname !== '') {
    navigateTo('/');
  } else {
    renderHomePage();
  }
}

function showMyListModal() {
  const modalId = 'myListModal';
  let modal = document.getElementById(modalId);
  if (!modal) {
    modal = document.createElement('div');
    modal.id = modalId;
    document.body.appendChild(modal);
  }

  const listMovies = MOVIES_DATA.filter(m => MY_LIST.includes(m.id) || MY_LIST.includes(m.slug));

  modal.innerHTML = `
    <div class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div class="bg-gray-950 border border-gray-800 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative">
        <div class="flex items-center justify-between border-b border-gray-800 pb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-bookmark text-red-600 text-lg"></i>
            <h2 class="text-base sm:text-lg font-bold text-white">Daftar Tontonan Saya</h2>
          </div>
          <button onclick="document.getElementById('${modalId}').remove()" class="text-gray-400 hover:text-white text-lg">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        ${listMovies.length === 0 ? `
          <div class="text-center py-10 space-y-2 text-gray-400">
            <i class="fa-solid fa-film text-3xl text-gray-600"></i>
            <p class="text-sm">Belum ada film yang ditambahkan ke Daftar Saya.</p>
            <button onclick="document.getElementById('${modalId}').remove(); navigateTo('/')" class="text-xs text-red-500 font-bold hover:underline">Jelajahi Koleksi Film</button>
          </div>
        ` : `
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-96 overflow-y-auto p-1">
            ${listMovies.map(movie => `
              <div onclick="document.getElementById('${modalId}').remove(); navigateTo('/movie/${movie.slug}')" class="group bg-gray-900 border border-gray-800 hover:border-red-600 rounded-lg overflow-hidden cursor-pointer transition flex flex-col">
                <div class="aspect-[2/3] bg-cover bg-center relative" style="background-image: url('${movie.poster}');">
                  <span class="absolute top-1 left-1 bg-red-600 text-[9px] font-black px-1.5 py-0.5 rounded text-white">${movie.quality}</span>
                </div>
                <div class="p-2">
                  <h4 class="text-xs font-bold text-white truncate group-hover:text-red-500">${movie.title}</h4>
                  <span class="text-[10px] text-gray-400">${movie.year}</span>
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    </div>
  `;
}

// -------------------------------------------------------------------
// 3. SPA ROUTING SYSTEM & NAVBAR SCROLL ANIMATION
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

// Netflix Navbar Scroll Transparency Controller
window.addEventListener('scroll', () => {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  if (window.scrollY > 40) {
    nav.classList.add('bg-[#141414]', 'border-b', 'border-gray-800/80', 'shadow-2xl');
    nav.classList.remove('bg-gradient-to-b', 'from-black/90');
  } else {
    nav.classList.remove('bg-[#141414]', 'border-b', 'border-gray-800/80', 'shadow-2xl');
    nav.classList.add('bg-gradient-to-b', 'from-black/90');
  }
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
// 4. VIEW RENDERERS (NETFLIX PRO EDITION)
// -------------------------------------------------------------------

// --- 4A. HOMEPAGE VIEW ---
function renderHomePage() {
  const main = document.getElementById('app-root');
  const featured = MOVIES_DATA[0] || {};
  const progressInfo = WATCH_PROGRESS[featured.id] || WATCH_PROGRESS[featured.slug];
  const hasResume = progressInfo && progressInfo.currentTime > 10;
  const isFeaturedInList = MY_LIST.includes(featured.id) || MY_LIST.includes(featured.slug);

  // Filter Catalog
  let filteredMovies = MOVIES_DATA;

  if (ACTIVE_CATEGORY !== 'all') {
    filteredMovies = filteredMovies.filter(m => 
      m.genres && m.genres.some(g => g.toLowerCase().includes(ACTIVE_CATEGORY.toLowerCase()))
    );
  }

  if (SEARCH_QUERY) {
    filteredMovies = filteredMovies.filter(m => {
      const titleMatch = m.title.toLowerCase().includes(SEARCH_QUERY);
      const genreMatch = m.genres && m.genres.some(g => g.toLowerCase().includes(SEARCH_QUERY));
      const castMatch = m.cast && m.cast.some(c => c.toLowerCase().includes(SEARCH_QUERY));
      const directorMatch = m.director && m.director.toLowerCase().includes(SEARCH_QUERY);
      return titleMatch || genreMatch || castMatch || directorMatch;
    });
  }

  const categories = [
    { id: 'all', label: 'Semua Film' },
    { id: 'Action', label: 'Action' },
    { id: 'Sci-Fi', label: 'Sci-Fi & Mutan' },
    { id: 'Superhero', label: 'Superhero' },
    { id: 'Adventure', label: 'Petualangan' },
    { id: 'Drama', label: 'Drama' }
  ];

  main.innerHTML = `
    <!-- HERO BANNER (NETFLIX HERO) -->
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
        <div class="flex flex-wrap items-center gap-3 pt-2 sm:pt-4">
          <button onclick="navigateTo('/watch/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-white text-black px-6 sm:px-8 py-3 sm:py-3.5 rounded-md font-bold hover:bg-gray-200 transition active:scale-95 shadow-xl text-sm sm:text-base">
            <i class="fa-solid fa-play text-base sm:text-lg"></i>
            <span>${hasResume ? 'Lanjutkan Menonton (' + formatTime(progressInfo.currentTime) + ')' : 'Putar Film'}</span>
          </button>

          <button onclick="navigateTo('/movie/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-gray-800/80 sm:bg-gray-700/80 backdrop-blur text-white px-5 sm:px-7 py-3 sm:py-3.5 rounded-md font-semibold hover:bg-gray-600 transition active:scale-95 text-sm sm:text-base">
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

    <!-- NETFLIX CATEGORY FILTER PILLS & SEARCH RESULTS -->
    <section class="px-4 sm:px-8 md:px-12 py-6 md:py-8 relative z-20 space-y-6">
      
      <!-- Category Filter Tabs -->
      <div class="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
        <span class="text-xs text-gray-400 font-semibold uppercase tracking-wider mr-2 hidden sm:inline">Filter:</span>
        ${categories.map(cat => `
          <button onclick="setCategoryFilter('${cat.id}')" 
                  class="px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all duration-200 border ${ACTIVE_CATEGORY === cat.id ? 'bg-red-600 text-white border-red-600 shadow-md shadow-red-600/30 font-bold' : 'bg-gray-900/90 text-gray-300 border-gray-800 hover:border-gray-600 hover:text-white'}">
            ${cat.label}
          </button>
        `).join('')}
      </div>

      <!-- Catalog Showcase Grid -->
      <div>
        <div class="flex items-center justify-between mb-4 sm:mb-6">
          <h2 class="text-base sm:text-xl md:text-2xl font-bold tracking-wide text-white flex items-center space-x-2">
            <span>${SEARCH_QUERY ? `Hasil Pencarian: "${SEARCH_QUERY}"` : (ACTIVE_CATEGORY === 'all' ? 'Koleksi Film 1080p BluRay Subtitle Indonesia' : `Koleksi Genre ${ACTIVE_CATEGORY}`)}</span>
            <span class="text-xs font-normal text-gray-500 font-mono">(${filteredMovies.length})</span>
          </h2>
          <span class="text-[11px] sm:text-xs text-red-500 font-semibold uppercase tracking-wider">Streaming HD</span>
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
              const p = WATCH_PROGRESS[movie.id] || WATCH_PROGRESS[movie.slug];
              const isInList = MY_LIST.includes(movie.id) || MY_LIST.includes(movie.slug);
              return `
              <div onclick="navigateTo('/movie/${movie.slug}')" class="group relative rounded-lg overflow-hidden bg-gray-900 cursor-pointer transition-all duration-300 hover:scale-105 hover:z-30 hover:shadow-2xl hover:shadow-red-600/20 border border-gray-800 hover:border-red-600 flex flex-col">
                <div class="aspect-[2/3] w-full bg-cover bg-center relative" style="background-image: url('${movie.poster}');">
                  <div class="absolute top-1.5 left-1.5 sm:top-2 sm:left-2 flex flex-col gap-1">
                    <span class="bg-red-600 text-[9px] sm:text-[10px] font-black px-1.5 py-0.5 rounded uppercase text-white">${movie.quality}</span>
                    <span class="bg-yellow-500 text-black text-[9px] sm:text-[10px] font-extrabold px-1.5 py-0.5 rounded">SUB INDO</span>
                  </div>
                  
                  <!-- Quick Watchlist Button -->
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
                    <span class="text-green-400 font-semibold">${movie.matchScore}</span>
                    <span>${movie.year}</span>
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

// --- 4B. MOVIE DETAIL VIEW ---
function renderMovieDetailPage(slug) {
  const movie = MOVIES_DATA.find(m => m.slug === slug || m.id === slug) || MOVIES_DATA[0];
  const main = document.getElementById('app-root');
  const progressInfo = WATCH_PROGRESS[movie.id] || WATCH_PROGRESS[movie.slug];
  const isInList = MY_LIST.includes(movie.id) || MY_LIST.includes(movie.slug);

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

            <!-- Action Buttons -->
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

      <!-- Main Video Stream Area (Full Theater Edge-to-Edge with Subtitle Overlay) -->
      <main class="relative flex-1 w-full h-full flex items-center justify-center p-0 m-0 min-h-0 overflow-hidden bg-black">
        <video id="cinemaPlayer" class="w-full h-full max-w-full max-h-full object-contain bg-black" controls playsinline preload="auto" poster="${movie.backdrop}">
          <source id="videoSource" src="${movie.streamUrl}" type="video/mp4">
          <track id="subTrack" label="Bahasa Indonesia" kind="subtitles" srclang="id" src="/sub_indo.vtt" default>
          Browser Anda tidak mendukung streaming video HTML5.
        </video>

        <!-- Dynamic High-Visibility Subtitle Overlay -->
        <div id="subOverlay" class="pointer-events-none absolute bottom-14 sm:bottom-16 md:bottom-20 inset-x-0 flex flex-col items-center justify-center px-4 text-center z-20 transition-all duration-100 select-none"></div>
      </main>

      <!-- Cinema Info Footer (Compact Pro Bar) -->
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

  // Auto-resume, Subtitle Engine & playback listener
  setTimeout(async () => {
    const vid = document.getElementById('cinemaPlayer');
    if (!vid) return;

    await loadSubtitles();

    if (vid.textTracks && vid.textTracks[0]) {
      vid.textTracks[0].mode = "showing";
    }

    vid.addEventListener('timeupdate', () => {
      if (!SUBTITLE_ENABLED) return;
      const overlay = document.getElementById('subOverlay');
      if (!overlay) return;
      const ct = vid.currentTime;
      const activeCue = SUBTITLE_CUES.find(c => ct >= c.start && ct <= c.end);
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

let SUBTITLE_CUES = [];
let SUBTITLE_ENABLED = true;

async function loadSubtitles() {
  try {
    const res = await fetch('/sub_indo.vtt');
    const text = await res.text();
    SUBTITLE_CUES = parseWebVTT(text);
  } catch (e) {
    console.error('[SUBTITLE ERROR]', e);
  }
}

function parseWebVTT(vttText) {
  const cues = [];
  const lines = vttText.split(/\r?\n/);
  let currentStart = null;
  let currentEnd = null;
  let currentText = [];

  const timeToSeconds = (tStr) => {
    if (!tStr) return 0;
    const parts = tStr.trim().split(':');
    if (parts.length === 3) {
      const [h, m, s] = parts;
      return parseFloat(h) * 3600 + parseFloat(m) * 60 + parseFloat(s);
    } else if (parts.length === 2) {
      const [m, s] = parts;
      return parseFloat(m) * 60 + parseFloat(s);
    }
    return 0;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes('-->')) {
      const [startStr, endStr] = line.split('-->');
      currentStart = timeToSeconds(startStr);
      currentEnd = timeToSeconds(endStr);
      currentText = [];
    } else if (line === '' && currentStart !== null) {
      if (currentText.length > 0) {
        cues.push({
          start: currentStart,
          end: currentEnd,
          text: currentText.join('<br>')
        });
      }
      currentStart = null;
      currentEnd = null;
      currentText = [];
    } else if (currentStart !== null && !/^\d+$/.test(line)) {
      currentText.push(line);
    }
  }
  if (currentStart !== null && currentText.length > 0) {
    cues.push({ start: currentStart, end: currentEnd, text: currentText.join('<br>') });
  }
  return cues;
}

function toggleSubtitle() {
  SUBTITLE_ENABLED = !SUBTITLE_ENABLED;
  const overlay = document.getElementById('subOverlay');
  if (!SUBTITLE_ENABLED && overlay) overlay.innerHTML = '';
  const btn = document.getElementById('subToggleBtn');
  if (btn) {
    btn.className = SUBTITLE_ENABLED 
      ? 'bg-yellow-500 text-black px-2 py-0.5 rounded font-bold border border-yellow-400 text-[10px] sm:text-xs transition cursor-pointer flex items-center space-x-1'
      : 'bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-semibold border border-gray-700 text-[10px] sm:text-xs transition cursor-pointer flex items-center space-x-1';
    btn.innerHTML = `<i class="fa-solid fa-closed-captioning"></i> <span>Sub Indo: ${SUBTITLE_ENABLED ? 'ON' : 'OFF'}</span>`;
  }
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
