import fs from 'fs';
import path from 'path';
import { SUBTITLE_CONFIG } from '@/config/global.config';

const regexPatterns = SUBTITLE_CONFIG.forbiddenPatterns.map(p => new RegExp(p, 'i'));

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

    // Filter duplicate static banners or spam words
    const isSpam = regexPatterns.some(pattern => pattern.test(line));
    const isDuplicateBanner = line.includes('GOBLIX NONTON FILM') || line.includes('00:00:02.000 --> 00:00:07.000');

    if (isSpam || isDuplicateBanner) {
      cleanLines.push('');
    } else {
      cleanLines.push(line);
    }
  }

  const { headerText, openingBanner } = SUBTITLE_CONFIG;
  let bannerBlock = `${headerText}\n\n`;

  if (openingBanner && openingBanner.enabled) {
    bannerBlock += `${openingBanner.cueNumber || 1}\n${openingBanner.startTime} --> ${openingBanner.endTime}\n${openingBanner.text}\n\n`;
  }

  return bannerBlock + cleanLines.join('\n').replace(/^\n+/, '');
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
