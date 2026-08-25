// ===================================================================
// GOBLIX STATE MANAGEMENT MODULE (state.js)
// Single Source of Truth for Auth, Progress, Filters & Watchlist
// Max ~60 lines • Zero Dependencies
// ===================================================================

export const state = {
  currentUser: null,
  moviesData: [],
  watchProgress: {},
  myList: [],
  activeCategory: 'all',
  searchQuery: '',
  progressInterval: null,
  subtitleCues: [],
  subtitleEnabled: true
};

export function getToken() {
  return localStorage.getItem('goblix_token');
}

export function setToken(token) {
  if (token) localStorage.setItem('goblix_token', token);
  else localStorage.removeItem('goblix_token');
}

export function loadLocalProgress() {
  try {
    state.watchProgress = JSON.parse(localStorage.getItem('goblix_progress') || '{}');
  } catch (e) {
    state.watchProgress = {};
  }
}

export function saveLocalProgress(movieId, currentTime, duration) {
  state.watchProgress[movieId] = {
    movieId,
    currentTime: Math.floor(currentTime),
    duration: Math.floor(duration),
    percent: Math.min(100, Math.round((currentTime / (duration || 1)) * 100)),
    updatedAt: new Date().toISOString()
  };
  localStorage.setItem('goblix_progress', JSON.stringify(state.watchProgress));
}

export function loadMyList() {
  try {
    state.myList = JSON.parse(localStorage.getItem('goblix_my_list') || '[]');
  } catch (e) {
    state.myList = [];
  }
  updateMyListBadge();
}

export function updateMyListBadge() {
  const badge = document.getElementById('nav-list-badge');
  if (badge) badge.innerText = state.myList.length;
}

export function toggleMyList(movieId) {
  const idx = state.myList.indexOf(movieId);
  if (idx > -1) state.myList.splice(idx, 1);
  else state.myList.push(movieId);
  localStorage.setItem('goblix_my_list', JSON.stringify(state.myList));
  updateMyListBadge();
}
