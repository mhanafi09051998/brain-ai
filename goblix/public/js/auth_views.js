// ===================================================================
// GOBLIX AUTH & MODAL VIEWS MODULE (auth_views.js)
// Login, Register, Modal Watchlist & Form Submissions
// Max ~150 lines • Zero Dependencies
// ===================================================================

import { state, setToken, updateMyListBadge } from './state.js';
import { checkAuthSession } from './api.js';

// --- IN-PLACE AUTH MODAL POPUP (ZERO PAGE RELOAD) ---
export function showAuthModal(initialTab = 'login') {
  const modalId = 'authModal';
  let modal = document.getElementById(modalId);
  if (!modal) {
    modal = document.createElement('div');
    modal.id = modalId;
    document.body.appendChild(modal);
  }

  const isLogin = initialTab === 'login';

  modal.innerHTML = `
    <div class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in" onclick="if(event.target === this) document.getElementById('${modalId}').remove()">
      <div class="w-full max-w-md bg-gray-950/95 border border-gray-800 p-6 sm:p-8 rounded-2xl shadow-2xl space-y-5 relative my-auto text-white">
        
        <!-- Close Button -->
        <button onclick="document.getElementById('${modalId}').remove()" class="absolute top-4 right-4 w-8 h-8 rounded-full bg-gray-900 hover:bg-red-600 text-gray-400 hover:text-white flex items-center justify-center transition border border-gray-800 text-sm">
          <i class="fa-solid fa-xmark"></i>
        </button>

        <!-- Header -->
        <div class="space-y-1">
          <div class="flex items-center space-x-2">
            <span class="goblix-logo text-2xl font-bold tracking-wider">GOBLIX</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-extrabold text-white tracking-tight">${isLogin ? 'Masuk ke Akun Anda' : 'Daftar Akun Baru'}</h2>
          <p class="text-xs text-gray-400">${isLogin ? 'Akses streaming film 1080p BluRay kualitas bioskop gratis.' : 'Mulai tonton koleksi film box office subtitle Indonesia.'}</p>
        </div>

        <!-- Alert Notification -->
        <div id="auth-alert" class="hidden p-3 rounded-lg bg-red-950/80 border border-red-800 text-red-200 text-xs font-medium"></div>

        <!-- Forms -->
        ${isLogin ? `
          <form id="loginForm" onsubmit="window.submitLogin(event)" class="space-y-3.5">
            <div>
              <label class="block text-xs text-gray-300 font-semibold mb-1">Email</label>
              <input type="email" id="loginEmail" required placeholder="nama@email.com" class="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition">
            </div>
            <div>
              <label class="block text-xs text-gray-300 font-semibold mb-1">Kata Sandi</label>
              <input type="password" id="loginPassword" required placeholder="••••••••" class="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition">
            </div>
            <button type="submit" id="loginBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg text-sm transition shadow-lg shadow-red-600/30 flex items-center justify-center space-x-2">
              <i class="fa-solid fa-right-to-bracket text-xs"></i>
              <span>Masuk</span>
            </button>
          </form>
          <div class="text-center text-xs text-gray-400 pt-2 border-t border-gray-900">
            Belum punya akun? <button type="button" onclick="showAuthModal('register')" class="text-white hover:text-red-500 font-bold ml-1 transition">Daftar sekarang</button>
          </div>
        ` : `
          <form id="registerForm" onsubmit="window.submitRegister(event)" class="space-y-3.5">
            <div>
              <label class="block text-xs text-gray-300 font-semibold mb-1">Nama Lengkap</label>
              <input type="text" id="regName" required placeholder="Nama Anda" class="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition">
            </div>
            <div>
              <label class="block text-xs text-gray-300 font-semibold mb-1">Email</label>
              <input type="email" id="regEmail" required placeholder="nama@email.com" class="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition">
            </div>
            <div>
              <label class="block text-xs text-gray-300 font-semibold mb-1">Kata Sandi (Minimal 6 Karakter)</label>
              <input type="password" id="regPassword" required minlength="6" placeholder="••••••••" class="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition">
            </div>
            <button type="submit" id="registerBtn" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg text-sm transition shadow-lg shadow-red-600/30 flex items-center justify-center space-x-2">
              <i class="fa-solid fa-user-plus text-xs"></i>
              <span>Buat Akun</span>
            </button>
          </form>
          <div class="text-center text-xs text-gray-400 pt-2 border-t border-gray-900">
            Sudah memiliki akun? <button type="button" onclick="showAuthModal('login')" class="text-white hover:text-red-500 font-bold ml-1 transition">Masuk di sini</button>
          </div>
        `}

      </div>
    </div>
  `;
}

export function renderLoginPage() {
  showAuthModal('login');
}

export function renderRegisterPage() {
  showAuthModal('register');
}

export function showMyListModal() {
  const modalId = 'myListModal';
  let modal = document.getElementById(modalId);
  if (!modal) {
    modal = document.createElement('div');
    modal.id = modalId;
    document.body.appendChild(modal);
  }
  const listMovies = state.moviesData.filter(m => state.myList.includes(m.id) || state.myList.includes(m.slug));

  modal.innerHTML = `
    <div class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4" onclick="if(event.target === this) document.getElementById('${modalId}').remove()">
      <div class="bg-gray-950 border border-gray-800 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative text-white">
        <div class="flex items-center justify-between border-b border-gray-800 pb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-bookmark text-red-600 text-lg"></i>
            <h2 class="text-base sm:text-lg font-bold text-white">Daftar Tontonan Saya</h2>
          </div>
          <button onclick="document.getElementById('${modalId}').remove()" class="w-8 h-8 rounded-full bg-gray-900 hover:bg-red-600 text-gray-400 hover:text-white flex items-center justify-center transition border border-gray-800 text-sm"><i class="fa-solid fa-xmark"></i></button>
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
              <div onclick="document.getElementById('${modalId}').remove(); showMovieModal('${movie.slug}')" class="group bg-gray-900 border border-gray-800 hover:border-red-600 rounded-lg overflow-hidden cursor-pointer transition flex flex-col">
                <div class="aspect-[2/3] bg-cover bg-center relative" style="background-image: url('${movie.poster}');">
                  <span class="absolute top-1 left-1 bg-red-600 text-[9px] font-black px-1.5 py-0.5 rounded text-white">${movie.quality || '1080p'}</span>
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
