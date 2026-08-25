// GOBLIX FULL-STACK CLIENT ROUTER & CONTROLLER (RESPONSIVE MOBILE & DESKTOP)
const API_MOVIES = '/api/movies';
const API_AUTH = '/api/auth';
let MOVIES_DATA = [];
let CURRENT_USER = null;

// Initialize Application
async function initApp() {
  await checkAuthSession();
  await fetchMovies();
  updateNavbarState();
  handleRoute();
}

// Fetch Movies Catalog
async function fetchMovies() {
  try {
    const res = await fetch(API_MOVIES);
    const json = await res.json();
    if (json.success) {
      MOVIES_DATA = json.data;
    }
  } catch (e) {
    console.error("Goblix Movies API Error:", e);
  }
}

// Verify User Auth Session
async function checkAuthSession() {
  const token = localStorage.getItem('goblix_token');
  if (!token) {
    CURRENT_USER = null;
    return;
  }
  try {
    const res = await fetch(`${API_AUTH}/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const json = await res.json();
    if (json.success) {
      CURRENT_USER = json.user;
    } else {
      localStorage.removeItem('goblix_token');
      CURRENT_USER = null;
    }
  } catch (e) {
    CURRENT_USER = null;
  }
}

// Router Event Listeners
window.addEventListener('popstate', handleRoute);
document.addEventListener('DOMContentLoaded', initApp);

function navigateTo(url) {
  history.pushState(null, null, url);
  updateNavbarState();
  handleRoute();
}

// Update Navbar Authentication State
function updateNavbarState() {
  const navAuthContainer = document.getElementById('nav-auth-container');
  if (!navAuthContainer) return;

  if (CURRENT_USER) {
    navAuthContainer.innerHTML = `
      <div class="relative group cursor-pointer flex items-center space-x-2">
        <div class="flex items-center space-x-2">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded bg-red-600 flex items-center justify-center font-bold text-white text-xs sm:text-sm shadow-md">
            ${CURRENT_USER.name.charAt(0).toUpperCase()}
          </div>
          <span class="text-xs font-semibold text-gray-200 hidden md:inline truncate max-w-[120px]">${CURRENT_USER.name}</span>
          <i class="fa-solid fa-caret-down text-[10px] text-gray-400 group-hover:rotate-180 transition"></i>
        </div>

        <!-- Dropdown Menu -->
        <div class="absolute right-0 top-full mt-2 w-48 bg-gray-900 border border-gray-800 rounded-lg shadow-2xl py-2 hidden group-hover:block z-50">
          <div class="px-4 py-2 border-b border-gray-800 text-xs">
            <p class="text-gray-400 font-medium">Masuk sebagai</p>
            <p class="text-white font-bold truncate">${CURRENT_USER.email}</p>
          </div>
          <a href="/" onclick="event.preventDefault(); navigateTo('/')" class="block px-4 py-2 text-xs text-gray-300 hover:bg-red-600 hover:text-white transition">
            <i class="fa-solid fa-film mr-2"></i> Beranda Film
          </a>
          <button onclick="handleLogout()" class="w-full text-left px-4 py-2 text-xs text-red-400 hover:bg-red-600 hover:text-white transition flex items-center">
            <i class="fa-solid fa-arrow-right-from-bracket mr-2"></i> Keluar (Logout)
          </button>
        </div>
      </div>
    `;
  } else {
    navAuthContainer.innerHTML = `
      <div class="flex items-center space-x-2 sm:space-x-3">
        <button onclick="navigateTo('/login')" class="text-xs font-bold text-gray-300 hover:text-white px-2.5 sm:px-3 py-1.5 transition">
          Masuk
        </button>
        <button onclick="navigateTo('/register')" class="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-3 sm:px-4 py-1.5 sm:py-2 rounded transition shadow-md shadow-red-600/30 whitespace-nowrap">
          Daftar
        </button>
      </div>
    `;
  }
}

// Handle Logout
function handleLogout() {
  localStorage.removeItem('goblix_token');
  CURRENT_USER = null;
  updateNavbarState();
  navigateTo('/');
}

// Main Route Dispatcher
function handleRoute() {
  const path = window.location.pathname;
  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (path === '/login') {
    renderLoginPage();
  } else if (path === '/register') {
    renderRegisterPage();
  } else if (path.startsWith('/watch/')) {
    const slug = path.replace('/watch/', '');
    renderWatchPage(slug);
  } else if (path.startsWith('/movie/')) {
    const slug = path.replace('/movie/', '');
    renderMovieDetailPage(slug);
  } else {
    renderHomePage();
  }
}

// ==========================================
// 1. HOME PAGE VIEW (MOBILE & DESKTOP OPTIMIZED)
// ==========================================
function renderHomePage() {
  const main = document.getElementById('app-root');
  const featured = MOVIES_DATA[0] || {};

  main.innerHTML = `
    <!-- HERO SECTION -->
    <header class="relative w-full min-h-[75vh] md:min-h-[85vh] bg-cover bg-center flex items-end md:items-center pb-12 md:pb-0" style="background-image: url('${featured.backdrop || ''}');">
      <div class="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-black via-black/70 to-transparent"></div>
      <div class="absolute inset-0 bg-gradient-to-t from-[#141414] via-transparent to-black/40"></div>
      
      <div class="relative z-10 max-w-2xl px-4 sm:px-8 md:px-12 space-y-3 sm:space-y-4 pt-20 md:pt-0">
        <div class="flex flex-wrap items-center gap-2">
          <span class="bg-red-600 text-white text-[10px] sm:text-xs font-black px-2 py-0.5 rounded tracking-widest uppercase">Goblix Original</span>
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

        <!-- STREAMING ACTIONS -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2 sm:pt-4">
          <button onclick="navigateTo('/watch/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-white text-black px-6 sm:px-8 py-3 sm:py-3.5 rounded-md font-bold hover:bg-gray-200 transition active:scale-95 shadow-xl text-sm sm:text-base">
            <i class="fa-solid fa-play text-base sm:text-lg"></i>
            <span>Putar Film</span>
          </button>

          <button onclick="navigateTo('/movie/${featured.slug}')" class="flex items-center justify-center space-x-2 bg-gray-800/80 sm:bg-gray-700/80 backdrop-blur text-white px-5 sm:px-7 py-3 sm:py-3.5 rounded-md font-semibold hover:bg-gray-600 transition active:scale-95 text-sm sm:text-base">
            <i class="fa-solid fa-circle-info text-base sm:text-lg"></i>
            <span>Selengkapnya</span>
          </button>
        </div>
      </div>
    </header>

    <!-- CATALOG GRID (RESPONSIVE: 2 COLS ON MOBILE, 3-6 ON TABLET/DESKTOP) -->
    <section class="px-4 sm:px-8 md:px-12 py-8 md:py-12 relative z-20 space-y-8">
      <div>
        <div class="flex items-center justify-between mb-4 sm:mb-6">
          <h2 class="text-base sm:text-xl md:text-2xl font-bold tracking-wide text-white">
            Rilis Terbaru 1080p BluRay Subtitle Indonesia
          </h2>
          <span class="text-[11px] sm:text-xs text-red-500 font-semibold uppercase tracking-wider">Streaming HD</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4 md:gap-5">
          ${MOVIES_DATA.map(movie => `
            <div onclick="navigateTo('/movie/${movie.slug}')" class="group relative rounded-lg overflow-hidden bg-gray-900 cursor-pointer transition-all duration-300 hover:scale-105 hover:z-30 hover:shadow-2xl hover:shadow-red-600/20 border border-gray-800 hover:border-red-600 flex flex-col">
              <div class="aspect-[2/3] w-full bg-cover bg-center relative" style="background-image: url('${movie.poster}');">
                <div class="absolute top-1.5 left-1.5 sm:top-2 sm:left-2 flex flex-col gap-1">
                  <span class="bg-red-600 text-[9px] sm:text-[10px] font-black px-1.5 py-0.5 rounded uppercase text-white">${movie.quality}</span>
                  <span class="bg-yellow-500 text-black text-[9px] sm:text-[10px] font-extrabold px-1.5 py-0.5 rounded">SUB INDO</span>
                </div>
              </div>
              <div class="p-2.5 sm:p-3.5 bg-gradient-to-t from-black via-black/90 to-transparent flex-1 flex flex-col justify-between">
                <h3 class="font-bold text-xs sm:text-sm text-white truncate group-hover:text-red-500 transition">${movie.title}</h3>
                <div class="flex items-center justify-between text-[10px] sm:text-[11px] text-gray-400 mt-1">
                  <span class="text-green-400 font-semibold">${movie.matchScore}</span>
                  <span>${movie.year}</span>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}

// ==========================================
// 2. MOVIE DETAIL WEBPAGE VIEW (/movie/:slug)
// ==========================================
function renderMovieDetailPage(slug) {
  const movie = MOVIES_DATA.find(m => m.slug === slug || m.id === slug) || MOVIES_DATA[0];
  const main = document.getElementById('app-root');

  main.innerHTML = `
    <div class="min-h-screen pt-16 sm:pt-20 px-4 sm:px-8 md:px-12 pb-16 max-w-6xl mx-auto space-y-6 sm:space-y-8">
      
      <!-- Back Navigation -->
      <button onclick="navigateTo('/')" class="text-gray-400 hover:text-white flex items-center space-x-2 text-xs sm:text-sm transition">
        <i class="fa-solid fa-arrow-left"></i>
        <span>Kembali ke Beranda</span>
      </button>

      <!-- Main Detail Banner Card -->
      <div class="relative rounded-xl sm:rounded-2xl overflow-hidden bg-gray-900 border border-gray-800 shadow-2xl">
        <div class="relative h-48 sm:h-72 md:h-96 w-full bg-cover bg-center" style="background-image: url('${movie.backdrop}');">
          <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/70 to-transparent"></div>
        </div>

        <div class="p-4 sm:p-6 md:p-10 -mt-20 sm:-mt-32 relative z-10 grid grid-cols-1 md:grid-cols-4 gap-6 md:gap-8 items-start">
          
          <!-- Poster -->
          <div class="w-36 sm:w-48 md:w-full aspect-[2/3] rounded-lg sm:rounded-xl overflow-hidden shadow-2xl border border-gray-700 bg-black mx-auto md:mx-0">
            <img src="${movie.poster}" alt="${movie.title}" class="w-full h-full object-cover">
          </div>

          <!-- Info & Actions -->
          <div class="md:col-span-3 space-y-4 sm:space-y-5">
            <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
              <span class="bg-red-600 text-white text-[10px] sm:text-xs font-black px-2 py-0.5 rounded uppercase">1080p BluRay</span>
              <span class="bg-yellow-500 text-black text-[10px] sm:text-xs font-extrabold px-2 py-0.5 rounded">SUB INDONESIA</span>
              <span class="bg-gray-800 text-gray-300 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">${movie.year}</span>
              <span class="bg-gray-800 text-gray-300 text-[10px] sm:text-xs px-2 py-0.5 rounded font-semibold">${movie.duration}</span>
              <span class="text-green-400 font-bold text-xs sm:text-sm ml-1">${movie.matchScore} Match</span>
            </div>

            <h1 class="text-2xl sm:text-3xl md:text-4xl font-extrabold text-white leading-tight">${movie.title}</h1>

            <p class="text-gray-300 text-xs sm:text-sm md:text-base leading-relaxed">
              ${movie.synopsis}
            </p>

            <!-- Metadata Specs -->
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4 pt-2 text-[11px] sm:text-xs text-gray-400 border-t border-gray-800">
              <div>
                <span class="block text-gray-500 font-semibold">Sutradara</span>
                <span class="text-white font-medium">${movie.director}</span>
              </div>
              <div>
                <span class="block text-gray-500 font-semibold">Audio Channel</span>
                <span class="text-white font-medium">${movie.audio}</span>
              </div>
              <div>
                <span class="block text-gray-500 font-semibold">Bahasa Subtitle</span>
                <span class="text-yellow-400 font-medium">${movie.subtitle}</span>
              </div>
            </div>

            <!-- Action Navigation Button (STREAMING ONLY) -->
            <div class="pt-2 sm:pt-4">
              <button onclick="navigateTo('/watch/${movie.slug}')" class="w-full sm:w-auto flex items-center justify-center space-x-3 bg-red-600 hover:bg-red-700 text-white px-8 sm:px-10 py-3.5 sm:py-4 rounded-lg font-bold text-sm sm:text-base transition shadow-xl shadow-red-600/30 active:scale-95">
                <i class="fa-solid fa-play text-base sm:text-lg"></i>
                <span>Putar Sekarang</span>
              </button>
            </div>

          </div>

        </div>
      </div>

    </div>
  `;
}

// ==========================================
// 3. WATCH / STREAMING WEBPAGE (/watch/:slug)
// ==========================================
function renderWatchPage(slug) {
  const movie = MOVIES_DATA.find(m => m.slug === slug || m.id === slug) || MOVIES_DATA[0];
  const main = document.getElementById('app-root');

  main.innerHTML = `
    <div class="min-h-screen bg-black flex flex-col justify-between pt-14 sm:pt-16">
      
      <!-- Top Cinema Control Bar -->
      <div class="px-4 sm:px-8 md:px-12 py-2.5 sm:py-3 bg-gray-950/95 border-b border-gray-800 flex items-center justify-between z-30">
        <div class="flex items-center space-x-3 sm:space-x-4 truncate">
          <button onclick="navigateTo('/movie/${movie.slug}')" class="text-gray-400 hover:text-white flex items-center space-x-1.5 font-semibold text-xs sm:text-sm transition flex-shrink-0">
            <i class="fa-solid fa-arrow-left text-sm sm:text-base"></i>
            <span class="hidden sm:inline">Kembali ke Detail</span>
          </button>
          <span class="text-gray-700 hidden sm:inline">|</span>
          <h2 class="text-white font-bold text-xs sm:text-sm md:text-base truncate max-w-[180px] sm:max-w-md">${movie.title}</h2>
        </div>

        <div class="flex items-center space-x-2 text-[10px] sm:text-xs text-gray-400 flex-shrink-0">
          <span class="bg-red-600 text-white px-2 py-0.5 rounded font-black">1080p HD</span>
          <span class="bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded font-semibold border border-yellow-500/30">Sub Indo</span>
        </div>
      </div>

      <!-- Native HTML5 Video Streamer (Responsive Aspect Ratio) -->
      <div class="relative w-full max-w-6xl mx-auto flex-1 flex items-center justify-center p-2 sm:p-4 md:p-6">
        <div class="w-full aspect-video bg-black rounded-lg sm:rounded-xl overflow-hidden shadow-2xl border border-gray-800">
          <video id="cinemaPlayer" class="w-full h-full" controls autoplay playsinline crossorigin="anonymous" poster="${movie.backdrop}">
            <source src="${movie.streamUrl}" type="video/mp4">
            <track label="Bahasa Indonesia" kind="subtitles" srclang="id" src="/sub_indo.vtt" default>
            Browser Anda tidak mendukung streaming video HTML5.
          </video>
        </div>
      </div>

      <!-- Info Bar Footer -->
      <div class="bg-gray-950 px-4 sm:px-8 md:px-12 py-3 sm:py-4 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-2 sm:gap-4 text-[11px] sm:text-xs text-gray-400 text-center sm:text-left">
        <div class="flex flex-wrap items-center justify-center sm:justify-start gap-3 sm:gap-6">
          <span><i class="fa-solid fa-closed-captioning text-yellow-400 text-xs sm:text-sm mr-1"></i> Subtitle: <b>Bahasa Indonesia</b></span>
          <span><i class="fa-solid fa-display text-blue-400 text-xs sm:text-sm mr-1"></i> Resolusi: <b>1080p BluRay</b></span>
          <span class="hidden md:inline"><i class="fa-solid fa-volume-high text-green-400 text-xs sm:text-sm mr-1"></i> Audio: <b>${movie.audio}</b></span>
        </div>
        <span class="text-gray-500 text-[10px] sm:text-xs">Goblix Streaming Engine</span>
      </div>

    </div>
  `;

  setTimeout(() => {
    const vid = document.getElementById('cinemaPlayer');
    if (vid) {
      vid.play().catch(() => {});
    }
  }, 150);
}

// ==========================================
// 4. AUTHENTICATION: LOGIN WEBPAGE (/login)
// ==========================================
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

        <div class="pt-4 border-t border-gray-800 text-center text-xs text-gray-400">
          Belum punya akun Goblix? 
          <a href="/register" onclick="event.preventDefault(); navigateTo('/register')" class="text-red-500 font-bold hover:underline ml-1">Daftar Sekarang</a>
        </div>

      </div>
    </div>
  `;
}

// Submit Login Form
async function submitLogin(e) {
  e.preventDefault();
  const alertEl = document.getElementById('auth-alert');
  const btn = document.getElementById('loginBtn');
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  alertEl.classList.add('hidden');
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> Memproses...`;

  try {
    const res = await fetch(`${API_AUTH}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.success) {
      localStorage.setItem('goblix_token', data.token);
      CURRENT_USER = data.user;
      updateNavbarState();
      navigateTo('/');
    } else {
      alertEl.textContent = data.error || 'Login gagal.';
      alertEl.classList.remove('hidden');
    }
  } catch (err) {
    alertEl.textContent = 'Gagal menghubungi server.';
    alertEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Masuk</span>`;
  }
}

// ==========================================
// 5. AUTHENTICATION: REGISTER WEBPAGE (/register)
// ==========================================
function renderRegisterPage() {
  const main = document.getElementById('app-root');

  main.innerHTML = `
    <div class="min-h-[85vh] flex items-center justify-center px-4 py-12 sm:py-16">
      <div class="w-full max-w-md bg-black/90 border border-gray-800 p-6 sm:p-10 rounded-xl sm:rounded-2xl shadow-2xl space-y-6 backdrop-blur">
        
        <div class="space-y-1.5">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Daftar Akun Goblix</h1>
          <p class="text-xs text-gray-400">Buat akun untuk menonton film 1080p BluRay tanpa batas.</p>
        </div>

        <div id="reg-alert" class="hidden p-3 rounded bg-red-900/50 border border-red-600 text-red-200 text-xs font-semibold"></div>

        <form id="regForm" onsubmit="submitRegister(event)" class="space-y-4">
          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Nama Lengkap</label>
            <input type="text" id="regName" required placeholder="Contoh: Muhammad Hanafi" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Email</label>
            <input type="email" id="regEmail" required placeholder="nama@email.com" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <div>
            <label class="block text-xs text-gray-300 font-semibold mb-1">Kata Sandi (Minimal 6 Karakter)</label>
            <input type="password" id="regPassword" minlength="6" required placeholder="••••••••" class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-600 transition">
          </div>

          <button type="submit" id="regBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-lg text-sm transition shadow-lg shadow-red-600/30 flex items-center justify-center space-x-2">
            <span>Daftar Sekarang</span>
          </button>
        </form>

        <div class="pt-4 border-t border-gray-800 text-center text-xs text-gray-400">
          Sudah memiliki akun? 
          <a href="/login" onclick="event.preventDefault(); navigateTo('/login')" class="text-red-500 font-bold hover:underline ml-1">Masuk Saja</a>
        </div>

      </div>
    </div>
  `;
}

// Submit Register Form
async function submitRegister(e) {
  e.preventDefault();
  const alertEl = document.getElementById('reg-alert');
  const btn = document.getElementById('regBtn');
  const name = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;

  alertEl.classList.add('hidden');
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> Mendaftarkan...`;

  try {
    const res = await fetch(`${API_AUTH}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();

    if (data.success) {
      localStorage.setItem('goblix_token', data.token);
      CURRENT_USER = data.user;
      updateNavbarState();
      navigateTo('/');
    } else {
      alertEl.textContent = data.error || 'Pendaftaran gagal.';
      alertEl.classList.remove('hidden');
    }
  } catch (err) {
    alertEl.textContent = 'Gagal menghubungi server.';
    alertEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Daftar Sekarang</span>`;
  }
}
