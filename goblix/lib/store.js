'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

const GoblixContext = createContext(null);

export function GoblixProvider({ children, initialMovies = [] }) {
  const [movies, setMovies] = useState(initialMovies);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [authModal, setAuthModal] = useState(null); // 'login' | 'register' | null
  const [myListOpen, setMyListOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setTokenState] = useState(null);
  const [myList, setMyList] = useState([]);
  const [watchProgress, setWatchProgress] = useState({});

  // Initialize from LocalStorage & Token on mount
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem('goblix_token');
      if (savedToken) {
        setTokenState(savedToken);
        fetch('/api/auth/me', { headers: { Authorization: `Bearer ${savedToken}` } })
          .then(res => res.json())
          .then(data => {
            if (data.success && data.user) setCurrentUser(data.user);
            else localStorage.removeItem('goblix_token');
          })
          .catch(() => {});
      }

      const savedList = localStorage.getItem('goblix_my_list');
      if (savedList) setMyList(JSON.parse(savedList));

      const savedProg = localStorage.getItem('goblix_watch_progress');
      if (savedProg) setWatchProgress(JSON.parse(savedProg));
    } catch (e) {}
  }, []);

  const setToken = (newToken) => {
    setTokenState(newToken);
    if (newToken) localStorage.setItem('goblix_token', newToken);
    else {
      localStorage.removeItem('goblix_token');
      setCurrentUser(null);
    }
  };

  const toggleMyList = (movieId) => {
    setMyList(prev => {
      const exists = prev.includes(movieId);
      const next = exists ? prev.filter(id => id !== movieId) : [...prev, movieId];
      try { localStorage.setItem('goblix_my_list', JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  const updateProgress = (movieId, currentTime, duration) => {
    if (!duration || duration <= 0) return;
    const percent = Math.min(100, Math.round((currentTime / duration) * 100));
    setWatchProgress(prev => {
      const next = {
        ...prev,
        [movieId]: { currentTime, duration, percent, updatedAt: Date.now() }
      };
      try { localStorage.setItem('goblix_watch_progress', JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  return (
    <GoblixContext.Provider value={{
      movies,
      setMovies,
      activeCategory,
      setActiveCategory,
      searchQuery,
      setSearchQuery,
      selectedMovie,
      setSelectedMovie,
      authModal,
      setAuthModal,
      myListOpen,
      setMyListOpen,
      currentUser,
      setCurrentUser,
      token,
      setToken,
      myList,
      toggleMyList,
      watchProgress,
      updateProgress
    }}>
      {children}
    </GoblixContext.Provider>
  );
}

export function useGoblix() {
  const context = useContext(GoblixContext);
  if (!context) throw new Error('useGoblix must be used within GoblixProvider');
  return context;
}
