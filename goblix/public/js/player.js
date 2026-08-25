// ===================================================================
// GOBLIX CINEMA PLAYER MODULE (player.js)
// Playback Rate, Adaptive Quality, PiP, and Time Formatter
// Max ~70 lines • Zero Dependencies
// ===================================================================

export function changeSpeed(val) {
  const vid = document.getElementById('cinemaPlayer');
  if (vid) vid.playbackRate = parseFloat(val);
}

export function changeQuality(val) {
  const vid = document.getElementById('cinemaPlayer');
  if (!vid) return;
  const curr = vid.currentTime;
  const isPaused = vid.paused;
  vid.load();
  vid.currentTime = curr;
  if (!isPaused) vid.play().catch(() => {});
}

export async function togglePiP() {
  const vid = document.getElementById('cinemaPlayer');
  if (!vid) return;
  if (document.pictureInPictureElement) {
    await document.exitPictureInPicture();
  } else {
    await vid.requestPictureInPicture();
  }
}

export function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return "00:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}
