const fs = require('fs');

function parseWebVTT(vttText) {
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
      currentEnd = timeToSeconds(endStr.trim().split(/\s+/)[0]);
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

const vtt1 = fs.readFileSync('goblix/public/sub_indo.vtt', 'utf8');
const cues1 = parseWebVTT(vtt1);
console.log('X-Men cues parsed:', cues1.length, cues1[0]);

const vtt2 = fs.readFileSync('goblix/public/subtitles/top-gun-maverick.vtt', 'utf8');
const cues2 = parseWebVTT(vtt2);
console.log('Top Gun cues parsed:', cues2.length, cues2[0]);
