// ===================================================================
// GOBLIX SUBTITLE SANITIZER & HANDLER (subtitles.js)
// Zero-Tolerance Filter against Gambling Ads & Promo
// Max ~45 lines • Fast Stream Processor
// ===================================================================

const fs = require('fs');
const path = require('path');

const FORBIDDEN_WORDS = [
  /slot/gi, /judi/gi, /gacor/gi, /poker/gi, /deposit/gi, /bonus/gi,
  /1xbet/gi, /sbobet/gi, /maxwin/gi, /pragmatic/gi, /zeus/gi,
  /link alternatif/gi, /promo/gi, /agen/gi
];

function serveSanitizedSubtitle(req, res, subFilePath) {
  fs.readFile(subFilePath, 'utf8', (err, rawData) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Subtitle tidak ditemukan');
      return;
    }

    const lines = rawData.split('\n');
    const sanitizedLines = lines.map(line => {
      let isForbidden = false;
      for (const pattern of FORBIDDEN_WORDS) {
        if (pattern.test(line)) {
          isForbidden = true;
          break;
        }
      }
      return isForbidden ? '' : line;
    });

    const sanitizedVTT = sanitizedLines.join('\n');

    res.writeHead(200, {
      'Content-Type': 'text/vtt; charset=utf-8',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Content-Disposition': 'inline; filename="subtitle_indonesia.vtt"'
    });
    res.end(sanitizedVTT);
  });
}

module.exports = { serveSanitizedSubtitle };
