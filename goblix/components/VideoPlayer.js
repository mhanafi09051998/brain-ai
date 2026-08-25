'use client';

import React, { useRef, useState, useEffect } from 'react';
import Link from 'next/link';
import { useGoblix } from '@/lib/store';
import { APP_CONFIG, PLAYER_CONFIG } from '@/config/global.config';

export default function VideoPlayer({ movie }) {
  const { updateProgress, watchProgress } = useGoblix();
  const videoRef = useRef(null);
  const containerRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const [quality, setQuality] = useState(PLAYER_CONFIG.defaultQuality);
  const [showQualityMenu, setShowQualityMenu] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Resume progress on mount
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !movie) return;

    const prog = watchProgress[movie.id] || watchProgress[movie.slug];
    if (prog && prog.currentTime > 5 && prog.currentTime < prog.duration - 15) {
      video.currentTime = prog.currentTime;
    }

    // Auto play
    video.play().catch(() => {});
  }, [movie]);

  // Hide controls after timeout
  useEffect(() => {
    let timer;
    const handleMouseMove = () => {
      setShowControls(true);
      clearTimeout(timer);
      timer = setTimeout(() => {
        if (isPlaying) setShowControls(false);
      }, PLAYER_CONFIG.controlsTimeoutMs);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      clearTimeout(timer);
    };
  }, [isPlaying]);

  // Periodic watch progress tracker
  useEffect(() => {
    const interval = setInterval(() => {
      const video = videoRef.current;
      if (video && !video.paused && video.duration) {
        updateProgress(movie.id, video.currentTime, video.duration);
      }
    }, PLAYER_CONFIG.progressIntervalMs);

    return () => clearInterval(interval);
  }, [movie, updateProgress]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) {
      video.play();
      setIsPlaying(true);
    } else {
      video.pause();
      setIsPlaying(false);
    }
  };

  const handleSeek = (e) => {
    const video = videoRef.current;
    if (!video || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    video.currentTime = pos * duration;
  };

  const handleVolumeChange = (e) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (videoRef.current) {
      videoRef.current.volume = val;
      videoRef.current.muted = val === 0;
      setIsMuted(val === 0);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      const nextMuted = !isMuted;
      videoRef.current.muted = nextMuted;
      setIsMuted(nextMuted);
    }
  };

  const changeSpeed = (rate) => {
    setPlaybackRate(rate);
    if (videoRef.current) videoRef.current.playbackRate = rate;
    setShowSpeedMenu(false);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  };

  const togglePiP = async () => {
    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
      } else if (videoRef.current) {
        await videoRef.current.requestPictureInPicture();
      }
    } catch (e) {}
  };

  const toggleSubtitles = () => {
    const video = videoRef.current;
    if (!video || !video.textTracks || video.textTracks.length === 0) return;
    const nextState = !subtitlesEnabled;
    setSubtitlesEnabled(nextState);
    for (let i = 0; i < video.textTracks.length; i++) {
      video.textTracks[i].mode = nextState ? 'showing' : 'hidden';
    }
  };

  const formatTime = (secs) => {
    if (!secs || isNaN(secs)) return '00:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    const h = Math.floor(m / 60);
    if (h > 0) {
      return `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  if (!movie) return null;

  return (
    <div ref={containerRef} className="relative w-screen h-screen bg-black overflow-hidden select-none font-sans">
      
      {/* Video Element */}
      <video
        ref={videoRef}
        src={`/api/stream/${movie.slug}`}
        crossOrigin="anonymous"
        playsInline
        className="w-full h-full object-contain cursor-pointer"
        onClick={togglePlay}
        onTimeUpdate={() => {
          if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
            setDuration(videoRef.current.duration || 0);
          }
        }}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onWaiting={() => setIsLoading(true)}
        onPlaying={() => setIsLoading(false)}
      >
        <track
          label={PLAYER_CONFIG.defaultSubtitleLang}
          kind="subtitles"
          srcLang="id"
          src={`/api/subtitles/${movie.slug}`}
          default
        />
      </video>

      {/* Loading Spinner */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-20">
          <div className="w-14 h-14 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {/* Top Bar Header */}
      <div className={`absolute top-0 inset-x-0 p-4 sm:p-6 bg-gradient-to-b from-black/90 via-black/40 to-transparent flex items-center justify-between transition-opacity duration-300 z-30 ${
        showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}>
        <div className="flex items-center space-x-4">
          <Link href="/" className="w-10 h-10 rounded-full bg-black/60 hover:bg-white hover:text-black text-white flex items-center justify-center transition border border-white/20">
            <i className="fa-solid fa-arrow-left text-sm"></i>
          </Link>
          <div>
            <h1 className="text-white text-base sm:text-lg font-bold drop-shadow">{movie.title}</h1>
            <p className="text-gray-400 text-xs">{movie.quality} • {movie.subtitle}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="bg-red-600 text-white text-[10px] font-black px-2 py-0.5 rounded">{APP_CONFIG.liveBadge}</span>
        </div>
      </div>

      {/* Bottom Controls Bar */}
      <div className={`absolute bottom-0 inset-x-0 p-4 sm:p-6 bg-gradient-to-t from-black/95 via-black/60 to-transparent transition-opacity duration-300 z-30 space-y-3 ${
        showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}>
        
        {/* Progress Bar */}
        <div onClick={handleSeek} className="relative w-full h-2 bg-gray-800/80 hover:h-3 rounded-full cursor-pointer transition-all group">
          <div className="h-full bg-red-600 rounded-full relative" style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}>
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-red-600 rounded-full scale-0 group-hover:scale-100 transition shadow"></div>
          </div>
        </div>

        {/* Buttons Row */}
        <div className="flex items-center justify-between text-white text-sm sm:text-base">
          
          {/* Left Controls */}
          <div className="flex items-center space-x-3 sm:space-x-5">
            <button onClick={togglePlay} className="hover:text-red-500 transition text-lg sm:text-xl">
              <i className={`fa-solid ${isPlaying ? 'fa-pause' : 'fa-play'}`}></i>
            </button>

            <button onClick={() => { if (videoRef.current) videoRef.current.currentTime -= PLAYER_CONFIG.seekStepSeconds; }} className="hover:text-gray-300 transition text-xs sm:text-sm" title="Mundur 10s">
              <i className="fa-solid fa-rotate-left mr-1"></i>10s
            </button>

            <button onClick={() => { if (videoRef.current) videoRef.current.currentTime += PLAYER_CONFIG.seekStepSeconds; }} className="hover:text-gray-300 transition text-xs sm:text-sm" title="Maju 10s">
              <i className="fa-solid fa-rotate-right mr-1"></i>10s
            </button>

            {/* Volume */}
            <div className="flex items-center space-x-2">
              <button onClick={toggleMute} className="hover:text-gray-300 transition text-sm">
                <i className={`fa-solid ${isMuted || volume === 0 ? 'fa-volume-xmark text-red-500' : 'fa-volume-high'}`}></i>
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-16 sm:w-20 accent-red-600 h-1 bg-gray-700 rounded cursor-pointer"
              />
            </div>

            {/* Time Stamp */}
            <div className="text-[11px] sm:text-xs text-gray-400 font-mono">
              <span>{formatTime(currentTime)}</span> / <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Right Controls */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            
            {/* Speed Controller */}
            <div className="relative">
              <button onClick={() => setShowSpeedMenu(!showSpeedMenu)} className="hover:text-red-500 text-xs font-bold px-2 py-1 bg-gray-900 border border-gray-800 rounded transition">
                {playbackRate}x
              </button>
              {showSpeedMenu && (
                <div className="absolute bottom-full right-0 mb-2 w-24 bg-gray-950 border border-gray-800 rounded-md shadow-2xl py-1 z-50 text-xs">
                  {PLAYER_CONFIG.playbackRates.map(rate => (
                    <button
                      key={rate}
                      onClick={() => changeSpeed(rate)}
                      className={`w-full text-left px-3 py-1 hover:bg-red-600 hover:text-white ${playbackRate === rate ? 'text-red-500 font-bold' : 'text-gray-300'}`}
                    >
                      {rate}x
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Quality Selector */}
            <div className="relative">
              <button onClick={() => setShowQualityMenu(!showQualityMenu)} className="hover:text-red-500 text-xs font-bold px-2 py-1 bg-gray-900 border border-gray-800 rounded transition hidden sm:inline">
                {quality}
              </button>
              {showQualityMenu && (
                <div className="absolute bottom-full right-0 mb-2 w-32 bg-gray-950 border border-gray-800 rounded-md shadow-2xl py-1 z-50 text-xs">
                  {PLAYER_CONFIG.qualities.map(q => (
                    <button
                      key={q}
                      onClick={() => { setQuality(q); setShowQualityMenu(false); }}
                      className={`w-full text-left px-3 py-1 hover:bg-red-600 hover:text-white ${quality === q ? 'text-red-500 font-bold' : 'text-gray-300'}`}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Subtitle Toggle */}
            <button
              onClick={toggleSubtitles}
              className={`text-xs font-bold px-2 py-1 rounded transition border ${
                subtitlesEnabled ? 'bg-red-600 border-red-600 text-white' : 'bg-gray-900 border-gray-800 text-gray-500'
              }`}
              title="Aktifkan / Nonaktifkan Subtitle Indonesia"
            >
              SUB
            </button>

            {/* PiP */}
            <button onClick={togglePiP} className="hover:text-gray-300 transition text-sm" title="Picture in Picture">
              <i className="fa-solid fa-clone"></i>
            </button>

            {/* Fullscreen */}
            <button onClick={toggleFullscreen} className="hover:text-gray-300 transition text-sm" title="Layar Penuh">
              <i className="fa-solid fa-expand"></i>
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}
