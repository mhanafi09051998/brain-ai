'use client';

import React, { useState } from 'react';
import { useGoblix } from '@/lib/store';

export default function AuthModal() {
  const { authModal, setAuthModal, setToken, setCurrentUser } = useGoblix();

  const [isLogin, setIsLogin] = useState(authModal === 'login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Sync mode with authModal prop changes
  React.useEffect(() => {
    if (authModal) setIsLogin(authModal === 'login');
    setError('');
  }, [authModal]);

  if (!authModal) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const payload = isLogin ? { email, password } : { name, email, password };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success && data.token) {
        setToken(data.token);
        setCurrentUser(data.user);
        setAuthModal(null);
      } else {
        setError(data.error || 'Terjadi kesalahan');
      }
    } catch (err) {
      setError('Gagal menghubungi server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) setAuthModal(null); }}
    >
      <div className="w-full max-w-md bg-gray-950/95 border border-gray-800 p-6 sm:p-8 rounded-2xl shadow-2xl space-y-5 relative my-auto text-white">
        
        {/* Close Button */}
        <button
          onClick={() => setAuthModal(null)}
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-gray-900 hover:bg-red-600 text-gray-400 hover:text-white flex items-center justify-center transition border border-gray-800 text-sm"
        >
          <i className="fa-solid fa-xmark"></i>
        </button>

        {/* Header */}
        <div className="space-y-1">
          <span className="text-2xl font-bold tracking-wider text-red-600 font-bebas">GOBLIX</span>
          <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
            {isLogin ? 'Masuk ke Akun Anda' : 'Daftar Akun Baru'}
          </h2>
          <p className="text-xs text-gray-400">
            {isLogin ? 'Akses streaming film 1080p BluRay kualitas bioskop.' : 'Mulai tonton koleksi film box office subtitle Indonesia.'}
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3 rounded-lg bg-red-950/80 border border-red-800 text-red-200 text-xs font-medium">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {!isLogin && (
            <div>
              <label className="block text-xs text-gray-300 font-semibold mb-1">Nama Lengkap</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Nama Anda"
                className="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition"
              />
            </div>
          )}

          <div>
            <label className="block text-xs text-gray-300 font-semibold mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="nama@email.com"
              className="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-300 font-semibold mb-1">Kata Sandi</label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-gray-900 border border-gray-800 focus:border-red-600 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold py-3 rounded-lg text-sm transition shadow-lg shadow-red-600/30 flex items-center justify-center space-x-2"
          >
            {loading ? (
              <span>Memproses...</span>
            ) : (
              <>
                <i className={`fa-solid ${isLogin ? 'fa-right-to-bracket' : 'fa-user-plus'} text-xs`}></i>
                <span>{isLogin ? 'Masuk' : 'Buat Akun'}</span>
              </>
            )}
          </button>
        </form>

        {/* Footer Toggle */}
        <div className="text-center text-xs text-gray-400 pt-2 border-t border-gray-900">
          {isLogin ? (
            <>
              Belum punya akun?{' '}
              <button
                type="button"
                onClick={() => { setIsLogin(false); setError(''); }}
                className="text-white hover:text-red-500 font-bold ml-1 transition"
              >
                Daftar sekarang
              </button>
            </>
          ) : (
            <>
              Sudah memiliki akun?{' '}
              <button
                type="button"
                onClick={() => { setIsLogin(true); setError(''); }}
                className="text-white hover:text-red-500 font-bold ml-1 transition"
              >
                Masuk di sini
              </button>
            </>
          )}
        </div>

      </div>
    </div>
  );
}
