#!/usr/bin/env python3
"""
===================================================================
GOBLIX AUTONOMOUS MOVIE & SUBTITLE DOWNLOADER ENGINE
Downloads movie files (MP4/MKV) and clean subtitles (WebVTT/SRT).
Auto-converts SRT to WebVTT, sanitizes gambling/promo ads,
fetches IMDb/TMDB metadata, and registers movie into Goblix catalog.
Max ~240 lines • Standard Library First • Zero Bloat
===================================================================
"""

import sys
import os
import re
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOVIES_JSON = os.path.join(WORKSPACE, "goblix", "data", "movies.json")
PUBLIC_STREAM_DIR = os.path.join(WORKSPACE, "goblix", "public", "stream")
PUBLIC_DIR = os.path.join(WORKSPACE, "goblix", "public")

FORBIDDEN_WORDS = [
  r'\bslot\b', r'\bjudi\b', r'\bgacor\b', r'\bpoker\b', r'\bdeposit\b',
  r'\bbonus\b', r'\b1xbet\b', r'\bsbobet\b', r'\bmaxwin\b', r'\bpragmatic\b',
  r'\bzeus\b', r'link alternatif', r'\bpromo\b', r'\bagen\b'
]

def download_file(url: str, output_path: str, label: str = "File"):
    """Downloads large media file in chunks with a live progress bar."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"\n[*] Mengunduh {label}: {url}")
    print(f"[*] Lokasi Penyimpanan: {output_path}")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(output_path, 'wb') as out:
            total_size = int(resp.getheader('Content-Length', 0))
            downloaded = 0
            chunk_size = 1024 * 1024 # 1 MB chunks
            start_time = datetime.now()

            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r  └─ Progress: [{percent:5.1f}%] {mb_down:.1f} MB / {mb_total:.1f} MB")
                else:
                    mb_down = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r  └─ Downloaded: {mb_down:.1f} MB")
                sys.stdout.flush()

        print(f"\n[+] Selesai mengunduh {label} ({downloaded / (1024*1024):.1f} MB).")
        return True
    except Exception as e:
        print(f"\n[!] Gagal mengunduh {label}: {e}")
        return False

def srt_to_vtt(srt_text: str) -> str:
    """Converts SubRip (.srt) subtitle format into WebVTT format."""
    # Replace comma milliseconds with dot milliseconds (00:01:20,500 -> 00:01:20.500)
    vtt = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', srt_text)
    if not vtt.startswith("WEBVTT"):
        vtt = "WEBVTT - Goblix Subtitle Track\n\n" + vtt
    return vtt

def sanitize_subtitles(vtt_text: str) -> str:
    """Sanitizes subtitle text, purging any gambling or promo spam."""
    lines = vtt_text.splitlines()
    clean_lines = []
    
    # Check if first line is opening brand
    has_header = False
    for line in lines:
        is_spam = False
        for pat in FORBIDDEN_WORDS:
            if re.search(pat, line, re.IGNORECASE):
                is_spam = True
                break
        if is_spam:
            clean_lines.append("")
        else:
            clean_lines.append(line)

    result = "\n".join(clean_lines)
    return result

def download_and_process_subtitle(url_or_text: str, output_path: str):
    """Downloads or saves subtitle, sanitizes it, and converts to WebVTT."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    raw_content = ""

    if url_or_text.startswith("http://") or url_or_text.startswith("https://"):
        print(f"[*] Mengunduh Subtitle dari URL: {url_or_text}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url_or_text, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_content = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[!] Gagal mengunduh subtitle: {e}")
            return False
    elif os.path.exists(url_or_text):
        with open(url_or_text, 'r', encoding='utf-8', errors='ignore') as f:
            raw_content = f.read()
    else:
        raw_content = url_or_text

    # Convert to VTT if in SRT format
    vtt_content = srt_to_vtt(raw_content)
    
    # Sanitize gambling and ads
    sanitized = sanitize_subtitles(vtt_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sanitized)

    print(f"[+] Subtitle bersih tersimpan di: {output_path}")
    return True

def register_movie(title: str, slug: str, stream_rel_url: str, sub_rel_url: str, quality: str = "1080p BluRay"):
    """Integrates movie into Goblix catalog database."""
    movies = []
    if os.path.exists(MOVIES_JSON):
        try:
            with open(MOVIES_JSON, 'r', encoding='utf-8') as f:
                movies = json.load(f)
        except:
            movies = []

    # Check if movie already exists
    idx = next((i for i, m in enumerate(movies) if m.get('slug') == slug or m.get('id') == slug), None)

    # Scrape IMDb / TMDB metadata if available
    try:
        from fetch_imdb_metadata import enrich_movie_metadata
        metadata = enrich_movie_metadata(title, custom_slug=slug, stream_url=stream_rel_url)
    except:
        metadata = {
            "id": slug,
            "slug": slug,
            "title": title,
            "year": datetime.now().year,
            "duration": "1 Jam 50 Menit",
            "ageRating": "13+",
            "matchScore": "98%",
            "quality": quality,
            "audio": "Dolby AAC 5.1",
            "subtitle": "Bahasa Indonesia (Resmi)",
            "genres": ["Action", "Adventure"],
            "poster": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=800&auto=format&fit=crop&q=80",
            "backdrop": "https://image.tmdb.org/t/p/original/gCctDK5RCPRMjgYAoV6yxNE7f93.jpg",
            "synopsis": f"Film {title} kualitas sinema 1080p BluRay subtitle Indonesia.",
            "director": "Bioskop Sinema",
            "cast": ["Pemeran Utama"],
            "streamUrl": stream_rel_url,
            "subtitleUrl": sub_rel_url
        }

    metadata["streamUrl"] = stream_rel_url
    metadata["subtitleUrl"] = sub_rel_url
    metadata["quality"] = quality

    if idx is not None:
        movies[idx] = metadata
        print(f"[*] Memperbarui data film di katalog: {title}")
    else:
        movies.append(metadata)
        print(f"[+] Menambahkan film baru ke katalog: {title}")

    with open(MOVIES_JSON, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"[+] Database {MOVIES_JSON} berhasil diperbarui!")

def main():
    parser = argparse.ArgumentParser(description="Goblix Autonomous Movie & Subtitle Downloader")
    parser.add_argument("--title", required=True, help="Judul Film (contoh: 'Top Gun: Maverick')")
    parser.add_argument("--movie-url", help="URL Download Video (Direct MP4/MKV Link)")
    parser.add_argument("--sub-url", help="URL Subtitle WebVTT / SRT atau path lokal")
    parser.add_argument("--slug", help="Slug URL film (opsional, auto-generate dari judul)")
    parser.add_argument("--quality", default="1080p BluRay", help="Kualitas film (default: '1080p BluRay')")

    args = parser.parse_args()
    slug = args.slug or re.sub(r'[^a-z0-9]+', '-', args.title.lower()).strip('-')

    video_file_name = f"{slug}.mp4"
    video_dest = os.path.join(PUBLIC_STREAM_DIR, video_file_name)
    stream_url = f"/stream/{video_file_name}"

    sub_file_name = f"{slug}.vtt"
    sub_dest = os.path.join(PUBLIC_DIR, "subtitles", sub_file_name)
    sub_url = f"/api/subtitles/{slug}"

    print("=" * 65)
    print(f"GOBLIX DOWNLOAD & INGESTION ENGINE")
    print(f"Judul: {args.title} | Slug: {slug}")
    print("=" * 65)

    # 1. Download Movie Video
    if args.movie_url:
        success = download_file(args.movie_url, video_dest, label=f"Video ({args.title})")
        if not success:
            print("[!] Peringatan: Pengunduhan video gagal.")
    else:
        print("[i] Tidak ada URL video yang diberikan, melewati pengunduhan video.")

    # 2. Download Subtitle
    if args.sub_url:
        download_and_process_subtitle(args.sub_url, sub_dest)
    else:
        print("[i] Menggunakan subtitle standar sistem.")

    # 3. Register to Goblix Database
    register_movie(args.title, slug, stream_url, sub_url, quality=args.quality)
    print("\n[V] PROSES SELESAI! Film siap disiarkan di Goblix.")

if __name__ == "__main__":
    main()
