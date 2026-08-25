import fs from 'fs';
import { getSubtitlePath, sanitizeWebVTT } from '@/lib/subtitles';

export const dynamic = 'force-dynamic';

export async function GET(request, { params }) {
  const { slug } = params;
  const subFilePath = getSubtitlePath(slug);

  if (!subFilePath || !fs.existsSync(subFilePath)) {
    const defaultVtt = `WEBVTT - Goblix Cinema Subtitle Track\n\n1\n00:00:02.000 --> 00:00:07.000\nGOBLIX NONTON FILM LUAR NEGERI GRATIS\n\n`;
    return new Response(defaultVtt, {
      status: 200,
      headers: {
        'Content-Type': 'text/vtt; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }

  try {
    const rawContent = fs.readFileSync(subFilePath, 'utf8');
    const sanitized = sanitizeWebVTT(rawContent);
    return new Response(sanitized, {
      status: 200,
      headers: {
        'Content-Type': 'text/vtt; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (e) {
    return new Response('WEBVTT\n\n', {
      status: 500,
      headers: { 'Content-Type': 'text/vtt; charset=utf-8' }
    });
  }
}
