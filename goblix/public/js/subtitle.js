// ===================================================================
// GOBLIX SUBTITLE ENGINE MODULE (subtitle.js)
// WebVTT Parser & High-Visibility Dynamic Subtitle Layer
// Max ~75 lines • Zero Dependencies
// ===================================================================

import { state } from './state.js';

export async function loadSubtitles() {
  try {
    const res = await fetch('/sub_indo.vtt');
    const text = await res.text();
    state.subtitleCues = parseWebVTT(text);
  } catch (e) {
    console.error('[SUBTITLE ERROR]', e);
  }
}

export function parseWebVTT(vttText) {
  const cues = [];
  const lines = vttText.split(/\r?\n/);
  let currentStart = null;
  let currentEnd = null;
  let currentText = [];

  const timeToSeconds = (tStr) => {
    if (!tStr) return 0;
    const parts = tStr.trim().split(':');
    if (parts.length === 3) {
      const [h, m, s] = parts;
      return parseFloat(h) * 3600 + parseFloat(m) * 60 + parseFloat(s);
    } else if (parts.length === 2) {
      const [m, s] = parts;
      return parseFloat(m) * 60 + parseFloat(s);
    }
    return 0;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes('-->')) {
      const [startStr, endStr] = line.split('-->');
      currentStart = timeToSeconds(startStr);
      currentEnd = timeToSeconds(endStr);
      currentText = [];
    } else if (line === '' && currentStart !== null) {
      if (currentText.length > 0) {
        cues.push({
          start: currentStart,
          end: currentEnd,
          text: currentText.join('<br>')
        });
      }
      currentStart = null;
      currentEnd = null;
      currentText = [];
    } else if (currentStart !== null && !/^\d+$/.test(line)) {
      currentText.push(line);
    }
  }
  if (currentStart !== null && currentText.length > 0) {
    cues.push({ start: currentStart, end: currentEnd, text: currentText.join('<br>') });
  }
  return cues;
}

export function toggleSubtitle() {
  state.subtitleEnabled = !state.subtitleEnabled;
  const overlay = document.getElementById('subOverlay');
  if (!state.subtitleEnabled && overlay) overlay.innerHTML = '';
  const btn = document.getElementById('subToggleBtn');
  if (btn) {
    btn.className = state.subtitleEnabled 
      ? 'bg-yellow-500 text-black px-2 py-0.5 rounded font-bold border border-yellow-400 text-[10px] sm:text-xs transition cursor-pointer flex items-center space-x-1'
      : 'bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-semibold border border-gray-700 text-[10px] sm:text-xs transition cursor-pointer flex items-center space-x-1';
    btn.innerHTML = `<i class="fa-solid fa-closed-captioning"></i> <span>Sub Indo: ${state.subtitleEnabled ? 'ON' : 'OFF'}</span>`;
  }
}
