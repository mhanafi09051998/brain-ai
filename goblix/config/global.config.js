// ===================================================================
// GOBLIX GLOBAL MASTER CONFIGURATION
// Satu pusat kendali untuk seluruh pengaturan platform & subtitle
// ===================================================================

export const APP_CONFIG = {
  name: 'GOBLIX',
  brandName: 'GOBLIX Cinema',
  domain: 'goblix.my.id',
  port: 3070,
  tagline: 'Nonton Film 1080p BluRay Subtitle Indonesia',
  description: 'Platform Streaming Film 1080p BluRay Subtitle Indonesia Resmi Tanpa Iklan Pop-up.',
  copyright: '© 2026 GOBLIX Cinema. Hak Cipta Dilindungi.',
  badge: 'GOBLIX ORIGINAL',
  liveBadge: 'GOBLIX LIVE',
  region: 'Indonesia'
};

// --- PUSAT KENDALI GLOBAL SUBTITLE & WEB VTT BANNER ---
export const SUBTITLE_CONFIG = {
  headerText: 'WEBVTT - Goblix Cinema Subtitle Track',
  
  // Banner pembuka yang disuntikkan secara global ke semua subtitle film
  openingBanner: {
    enabled: true,
    startTime: '00:00:02.000',
    endTime: '00:00:07.000',
    cueNumber: 1,
    text: 'GOBLIX NONTON FILM LUAR NEGERI GRATIS'
  },

  // Daftar kata terlarang (Anti-Judi / Anti-Slot / Anti-Promo)
  forbiddenPatterns: [
    '\\bslot\\b', '\\bjudi\\b', '\\bgacor\\b', '\\bpoker\\b',
    '\\bdeposit\\b', '\\bbonus\\b', '\\b1xbet\\b', '\\bsbobet\\b',
    '\\bmaxwin\\b', '\\bpragmatic\\b', '\\bzeus\\b', 'link alternatif',
    '\\bpromo\\b', '\\bagen\\b', 'official website', 't\\.me/',
    'bit\\.ly/'
  ]
};

// --- GENRE RESMI IMDB ---
export const IMDB_GENRES = [
  'Action',
  'Adventure',
  'Comedy',
  'Crime',
  'Drama',
  'Mystery',
  'Sci-Fi',
  'Thriller',
  'Animation',
  'Horror',
  'Romance'
];

// --- PENGATURAN VIDEO PLAYER & RESOLUSI ---
export const PLAYER_CONFIG = {
  playbackRates: [0.5, 0.75, 1, 1.25, 1.5, 2],
  qualities: ['1080p BluRay', '720p HD', 'Auto'],
  defaultQuality: '1080p BluRay',
  defaultSubtitleLang: 'Bahasa Indonesia (Resmi)',
  seekStepSeconds: 10,
  progressIntervalMs: 5000,
  controlsTimeoutMs: 3500
};

// --- MENU LEGALITAS & KEBIJAKAN ---
export const LEGAL_LINKS = [
  { id: 'terms', label: 'Syarat & Ketentuan Penggunaan' },
  { id: 'privacy', label: 'Kebijakan Privasi' },
  { id: 'cookie', label: 'Preferensi Cookie' },
  { id: 'faq', label: 'Pusat Bantuan & FAQ' }
];
