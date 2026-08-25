import fs from 'fs';
import path from 'path';

const MOVIES_FILE = path.join(process.cwd(), 'data', 'movies.json');

export function normalizeMovie(m) {
  if (!m || typeof m !== 'object') return null;
  const slug = String(m.slug || m.id || 'movie');
  return {
    id: String(m.id || slug),
    slug: slug,
    imdbId: String(m.imdbId || ''),
    title: String(m.title || 'Judul Film'),
    year: Number(m.year) || new Date().getFullYear(),
    duration: String(m.duration || '2 Jam'),
    ageRating: String(m.ageRating || '13+'),
    matchScore: String(m.matchScore || '98%'),
    quality: String(m.quality || '1080p BluRay'),
    audio: String(m.audio || 'Dolby AAC 5.1'),
    subtitle: String(m.subtitle || 'Bahasa Indonesia (Resmi)'),
    genres: Array.isArray(m.genres) ? m.genres : (typeof m.genres === 'string' ? m.genres.split(',').map(s => s.trim()) : ['Action']),
    poster: String(m.poster || `/images/posters/${slug}.jpg`),
    backdrop: String(m.backdrop || `/images/backdrops/${slug}.jpg`),
    synopsis: String(m.synopsis || 'Sinopsis film belum tersedia.'),
    director: String(m.director || 'Sutradara'),
    cast: Array.isArray(m.cast) ? m.cast : (typeof m.cast === 'string' ? m.cast.split(',').map(s => s.trim()) : ['Aktor Terkenal']),
    streamUrl: String(m.streamUrl || `/stream/${slug}.mp4`),
    subtitleUrl: String(m.subtitleUrl || `/api/subtitles/${slug}`)
  };
}

export function getAllMovies() {
  try {
    if (!fs.existsSync(MOVIES_FILE)) return [];
    const raw = JSON.parse(fs.readFileSync(MOVIES_FILE, 'utf8') || '[]');
    return (Array.isArray(raw) ? raw : []).map(normalizeMovie).filter(Boolean);
  } catch (e) {
    console.error('[MOVIES ERROR]', e);
    return [];
  }
}

export function getMovieBySlug(slug) {
  const movies = getAllMovies();
  return movies.find(m => m.slug === slug || m.id === slug) || null;
}
