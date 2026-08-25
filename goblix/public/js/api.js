// ===================================================================
// GOBLIX API CLIENT MODULE (api.js)
// HTTP Fetchers for Movies, Progress, and Auth Endpoints
// Max ~65 lines • Zero Dependencies
// ===================================================================

import { state, getToken, setToken, saveLocalProgress } from './state.js';

export async function fetchMovies() {
  try {
    const res = await fetch('/api/movies');
    const data = await res.json();
    if (data.success && Array.isArray(data.data)) {
      state.moviesData = data.data;
    }
  } catch (e) {
    console.error('[API ERROR] Failed to fetch movies:', e);
  }
}

export async function checkAuthSession() {
  const token = getToken();
  if (!token) {
    state.currentUser = null;
    return;
  }
  try {
    const res = await fetch('/api/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (data.success && data.user) {
      state.currentUser = data.user;
      await fetchServerWatchProgress();
    } else {
      setToken(null);
      state.currentUser = null;
    }
  } catch (e) {
    state.currentUser = null;
  }
}

export async function fetchServerWatchProgress() {
  const token = getToken();
  if (!token) return;
  try {
    const res = await fetch('/api/user/progress', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (data.success && data.progress) {
      state.watchProgress = { ...state.watchProgress, ...data.progress };
    }
  } catch (e) {}
}

export async function saveServerWatchProgress(movieId, currentTime, duration) {
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
