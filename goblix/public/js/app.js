// ===================================================================
// GOBLIX MASTER ENTRY POINT & ROUTER (app.js)
// Modular Architecture • Total Lines < 150
// ===================================================================

import { state, setToken, loadLocalProgress, loadMyList, toggleMyList as stateToggleMyList } from './state.js';
import { fetchMovies, checkAuthSession } from './api.js';
import { toggleSubtitle as subToggle } from './subtitle.js';
import { changeSpeed as plChangeSpeed, changeQuality as plChangeQuality, togglePiP as plTogglePiP } from './player.js';
import { renderHomePage, renderMovieDetailPage, renderWatchPage } from './views.js';
import { renderLoginPage, renderRegisterPage, showMyListModal as authShowMyList } from './auth_views.js';

// --- Global Window Bindings for Inline HTML Event Handlers ---
window.navigateTo = navigateTo;
window.setCategoryFilter = setCategoryFilter;
window.toggleSearchInput = toggleSearchInput;
window.handleSearchQuery = handleSearchQuery;
window.clearSearch = clearSearch;
window.toggleMyList = (id) => { stateToggleMyList(id); renderHomePage(); };
window.showMyListModal = authShowMyList;
window.toggleSubtitle = subToggle;
window.changeSpeed = plChangeSpeed;
window.changeQuality = plChangeQuality;
window.togglePiP = plTogglePiP;
window.handleLogout = handleLogout;
window.submitLogin = submitLogin;
window.submitRegister = submitRegister;

// --- Navbar Transparency Scroll Controller ---
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

export function updateNavbarAuth() {
  const container = document.getElementById('nav-auth-container');
  if (!container) return;

  if (state.currentUser) {
    container.innerHTML = `
      <div class="relative group">
        <button class="flex items-center space-x-2 focus:outline-none py-1">
          <div class="w-8 h-8 rounded bg-red-600 flex items-center justify-center font-bold text-xs text-white border border-red-500 shadow-md">
            ${state.currentUser.name ? state.currentUser.name.charAt(0).toUpperCase() : 'G'}
          </div>
          <i class="fa-solid fa-caret-down text-gray-400 text-xs transition group-hover:rotate-180 hidden sm:inline"></i>
        </button>
        <div class="absolute right-0 top-full mt-2 w-48 bg-gray-950/95 border border-gray-800 rounded-md shadow-2xl py-2 hidden group-hover:block backdrop-blur z-50 text-xs">
          <div class="px-4 py-2 border-b border-gray-800">
            <p class="font-bold text-white truncate">${state.currentUser.name}</p>
            <p class="text-[10px] text-green-400 font-mono">Paket HD Sinema</p>
          </div>
          <a href="javascript:void(0)" onclick="showMyListModal()" class="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white transition">Daftar Saya (${state.myList.length})</a>
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

export function handleLogout() {
  setToken(null);
  state.currentUser = null;
  updateNavbarAuth();
  navigateTo('/');
}

export function toggleSearchInput() {
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

export function handleSearchQuery(q) {
  state.searchQuery = q.toLowerCase().trim();
  const closeBtn = document.getElementById('searchCloseBtn');
  if (closeBtn) {
    if (state.searchQuery) closeBtn.classList.remove('hidden');
    else closeBtn.classList.add('hidden');
  }
  if (window.location.pathname !== '/' && window.location.pathname !== '') navigateTo('/');
  else renderHomePage();
}

export function clearSearch() {
  state.searchQuery = '';
  const input = document.getElementById('netflixSearchInput');
  if (input) input.value = '';
  toggleSearchInput();
  renderHomePage();
}

export function setCategoryFilter(category) {
  state.activeCategory = category;
  state.searchQuery = '';
  const input = document.getElementById('netflixSearchInput');
  if (input) input.value = '';
  if (window.location.pathname !== '/' && window.location.pathname !== '') navigateTo('/');
  else renderHomePage();
}

// --- Auth Submission Handlers ---
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
      state.currentUser = data.user;
      updateNavbarAuth();
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
      state.currentUser = data.user;
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

// --- SPA Router ---
export function navigateTo(path) {
  if (state.progressInterval) {
    clearInterval(state.progressInterval);
    state.progressInterval = null;
  }
  window.history.pushState({}, '', path);
  handleRoute();
}

window.addEventListener('popstate', () => {
  if (state.progressInterval) {
    clearInterval(state.progressInterval);
    state.progressInterval = null;
  }
  handleRoute();
});

export async function handleRoute() {
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

  if (state.moviesData.length === 0) await fetchMovies();

  if (path === '/' || path === '') renderHomePage();
  else if (path.startsWith('/movie/')) renderMovieDetailPage(path.replace('/movie/', ''));
  else if (path.startsWith('/watch/')) renderWatchPage(path.replace('/watch/', ''));
  else if (path === '/login') renderLoginPage();
  else if (path === '/register') renderRegisterPage();
  else renderHomePage();
}

// --- App Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
  loadLocalProgress();
  loadMyList();
  await checkAuthSession();
  updateNavbarAuth();
  await handleRoute();
});
