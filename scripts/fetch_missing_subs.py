#!/usr/bin/env python3
"""
Download Indonesian subtitles (via rest.opensubtitles.org, no key needed)
for the 6 movies missing id.srt.
Uses IMDB search by title+year as fallback.
"""
import urllib.request, urllib.parse, json, gzip, os, time

UA = "TemporaryUserAgent v1.0"
ROOT = "/home/ubuntu/media_storage/movies"

TARGETS = [
    # (title, year, imdb_id)
    ("A Nymphoid Barbarian in Dinosaur Hell", 1990, "tt0097448"),
    ("Chris Claremont's X-Men",               2018, "tt9138356"),
    ("Oppenheimer - The Real Story",           2023, "tt28014126"),
    ("The Science of Interstellar",            2015, "tt4270600"),
    ("Stealing Pulp Fiction",                  2024, "tt32267866"),
    ("The Substance of Fire",                  1996, "tt0117946"),
]

def fetch_sub(imdb_id, title, year, dest_folder):
    imdb_num = imdb_id.replace("tt", "")
    url = f"https://rest.opensubtitles.org/search/imdbid-{imdb_num}/sublanguageid-ind"
    print(f"  [*] Fetching: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
        if not data:
            print(f"  [MISS] No Indonesian sub found for {title} ({year})")
            return False
        # Pick best: prefer MovieFPS closest to film's typical fps, pick first
        entry = data[0]
        sub_url = entry.get("SubDownloadLink", "")
        if not sub_url:
            print(f"  [MISS] No download link for {title}")
            return False
        # Download
        sub_req = urllib.request.Request(sub_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(sub_req, timeout=20) as sresp:
            raw = sresp.read()
        try:
            content = gzip.decompress(raw)
        except Exception:
            content = raw
        # Write
        folder_name = next(
            (d for d in os.listdir(ROOT + "/Box Office & Masterpiece") if title.lower().split()[0] in d.lower()),
            None
        )
        # Find actual folder across all genres
        out_path = None
        for genre in os.listdir(ROOT):
            gp = os.path.join(ROOT, genre)
            if not os.path.isdir(gp):
                continue
            for mdir in os.listdir(gp):
                if title.lower().split()[0] in mdir.lower() and str(year) in mdir:
                    out_path = os.path.join(gp, mdir, f"{mdir}.id.srt")
                    break
            if out_path:
                break
        if not out_path:
            out_path = os.path.join(dest_folder, f"{os.path.basename(dest_folder)}.id.srt")
        with open(out_path, "wb") as f:
            f.write(content)
        print(f"  [OK] Saved: {out_path}")
        return True
    except Exception as e:
        print(f"  [ERR] {title}: {e}")
        return False

ok = 0
for title, year, imdb_id in TARGETS:
    print(f"\n>> {title} ({year})")
    if fetch_sub(imdb_id, title, year, ROOT):
        ok += 1
    time.sleep(1.5)  # rate limit

print(f"\n=== SELESAI: {ok}/{len(TARGETS)} sub berhasil diunduh ===")
