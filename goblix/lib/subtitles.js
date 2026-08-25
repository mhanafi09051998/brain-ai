import fs from 'fs';
import path from 'path';

const FORBIDDEN_WORDS = [
  rString('\\bslot\\b'), rString('\\bjudi\\b'), rString('\\bgacor\\b'), rString('\\bpoker\\b'),
  rString('\\bdeposit\\b'), rString('\\bbonus\\b'), rString('\\b1xbet\\b'), rString('\\bsbobet\\b'),
  rString('\\bmaxwin\\b'), rString('\\bpragmatic\\b'), rString('\\bzeus\\b'), rString('link alternatif'),
  rString('\\bpromo\\b'), rString('\\bagen\\b'), rString('official website'), rString('t\\.me/'),
  rString('bit\\.ly/')
];

function rString(pattern) {
  return new RegExp(pattern, 'i');
}

export function sanitizeWebVTT(rawText) {
  const lines = rawText.split(/\r?\n/);
  const cleanLines = [];
  let isHeader = true;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (isHeader) {
      if (line.startsWith('WEBVTT') || line.trim() === '') {
        continue;
      }
      isHeader = false;
    }

    const isSpam = FORBIDDEN_WORDS.some(pattern => pattern.test(line));
    if (isSpam) {
      cleanLines.push('');
    } else {
      cleanLines.push(line);
    }
  }

  const openingBanner = `WEBVTT - Goblix Cinema Subtitle Track\n\n1\n00:00:02.000 --> 00:00:07.000\nGOBLIX NONTON FILM LUAR NEGERI GRATIS\n\n`;
  return openingBanner + cleanLines.join('\n');
}

export function getSubtitlePath(slug) {
  const publicDir = path.join(process.cwd(), 'public');
  const candidates = [
    path.join(publicDir, 'subtitles', `${slug}.vtt`),
    path.join(publicDir, `${slug}.vtt`),
    path.join(publicDir, 'subtitles', 'sub_indo.vtt'),
    path.join(publicDir, 'sub_indo.vtt')
  ];

  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}
