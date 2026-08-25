// ===================================================================
// GOBLIX AUTH & MODAL VIEWS MODULE (auth_views.js)
// Login, Register, Modal Watchlist & Form Submissions
// Max ~130 lines • Zero Dependencies
// ===================================================================

import { state, setToken, updateMyListBadge } from './state.js';
import { checkAuthSession } from './api.js';

export function renderLoginPage() {
  const main = document.getElementById('app-root');
  main.innerHTML = `
    <div class="min-h-[85vh] flex items-center justify-center px-4 py-12 sm:py-16">
      <div class="w-full max-w-md bg-black/90 border border-gray-800 p-6 sm:p-10 rounded-xl sm:rounded-2xl shadow-2xl space-y-6 backdrop-blur">
        <div class="space-y-1.5">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Masuk ke Goblix</h1>
          <p class="text-xs text-gray-400">Akses streaming film 1080p BluRay kualitas bioskop.</p>
        </div>
        <div id="auth-alert" class="hidden p-3 rounded bg-red-900/50 border border-red-600 text-red-200 text-xs font-semibold"></div>
        <form id="loginForm" onsubmit="window.submitLogin(event)" class="space-y-4">
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
          Belum punya akun? <a href="/register" onclick="event.preventDefault(); navigateTo('/register')" class="text-white hover:text-red-500 font-bold ml-1 transition">Daftar sekarang</a>
        </div>
      </div>
    </div>
  `;
}

export function renderRegisterPage() {
  const main = document.getElementById('app-root');
  main.innerHTML = `
    <div class="min-h-[85vh] flex items-center justify-center px-4 py-12 sm:py-16">
      <div class="w-full max-w-md bg-black/90 border border-gray-800 p-6 sm:p-10 rounded-xl sm:rounded-2xl shadow-2xl space-y-6 backdrop-blur">
        <div class="space-y-1.5">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Daftar Akun Baru</h1>
          <p class="text-xs text-gray-400">Mulai streaming film kualitas 1080p BluRay gratis.</p>
        </div>
        <div id="auth-alert" class="hidden p-3 rounded bg-red-900/50 border border-red-600 text-red-200 text-xs font-semibold"></div>
        <form id="registerForm" onsubmit="window.submitRegister(event)" class="space-y-4">
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
          Sudah memiliki akun? <a href="/login" onclick="event.preventDefault(); navigateTo('/login')" class="text-white hover:text-red-500 font-bold ml-1 transition">Masuk di sini</a>
        </div>
      </div>
    </div>
  `;
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
    <div class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div class="bg-gray-950 border border-gray-800 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative">
        <div class="flex items-center justify-between border-b border-gray-800 pb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-bookmark text-red-600 text-lg"></i>
            <h2 class="text-base sm:text-lg font-bold text-white">Daftar Tontonan Saya</h2>
          </div>
          <button onclick="document.getElementById('${modalId}').remove()" class="text-gray-400 hover:text-white text-lg"><i class="fa-solid fa-xmark"></i></button>
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
