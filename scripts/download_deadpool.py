#!/usr/bin/env python3
import urllib.request, urllib.parse, json, subprocess, os, gzip, time

DEADPOOL = [
    {"name": "Deadpool",              "year": "2016", "imdb": "1431045", "folder": "Deadpool (2016)"},
    {"name": "Deadpool 2",            "year": "2018", "imdb": "5463162", "folder": "Deadpool 2 (2018)"},
    {"name": "Deadpool & Wolverine",  "year": "2024", "imdb": "6263850", "folder": "Deadpool & Wolverine (2024)"},
]

DEST_BASE = "/home/ubuntu/media_storage/movies/Box Office & Masterpiece"
UA = "TemporaryUserAgent v1.0"
TRACKERS = "&tr=".join([
    "",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.tracker.cl:1337/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://tracker.torrent.eu.org:451/announce",
])

def search_yts(title, year):
    clean = title.replace(":", "").replace("&", "and")
    for domain in ["yts.mx", "yts.lt", "yts.am"]:
        try:
            url = f"https://{domain}/api/v2/list_movies.json?query_term={urllib.parse.quote(clean)}&limit=10"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
            for m in data.get("data", {}).get("movies", []):
                if str(m.get("year")) == str(year):
                    return m
            movies = data.get("data", {}).get("movies", [])
            if movies:
                return movies[0]
        except Exception:
            pass
    return None

def fetch_sub(imdb_id, out_path):
    url = f"https://rest.opensubtitles.org/search/imdbid-{imdb_id}/sublanguageid-ind"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode())
        if not data:
            return False
        sub_url = data[0].get("SubDownloadLink", "")
        if not sub_url:
            return False
        raw = urllib.request.urlopen(
            urllib.request.Request(sub_url, headers={"User-Agent": UA}), timeout=20
        ).read()
        try:
            content = gzip.decompress(raw)
        except Exception:
            content = raw
        with open(out_path, "wb") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"      [SUB ERR] {e}")
        return False

print("=" * 60)
print("⬇️  DOWNLOAD DEADPOOL TRILOGY (1080p + Sub Indonesia)")
print("=" * 60)

for m in DEADPOOL:
    name    = m["name"]
    year    = m["year"]
    imdb    = m["imdb"]
    folder  = m["folder"]
    fp      = os.path.join(DEST_BASE, folder)
    os.makedirs(fp, exist_ok=True)

    print(f"\n▶ {name} ({year})")

    # Check if video already exists
    has_video = any(
        f.lower().endswith((".mp4", ".mkv")) and not os.path.islink(os.path.join(fp, f))
        for f in os.listdir(fp)
    )
    if has_video:
        print(f"  [SKIP] Video sudah ada")
    else:
        movie_data = search_yts(name, year)
        if movie_data:
            torrents = movie_data.get("torrents", [])
            torr = next((t for t in torrents if t.get("quality") == "1080p"), None)
            if not torr:
                torr = next((t for t in torrents if t.get("quality") == "720p"), None)
            if not torr and torrents:
                torr = torrents[0]

            if torr:
                h = torr.get("hash")
                title_long = movie_data.get("title_long", name)
                size = torr.get("size", "?")
                quality = torr.get("quality", "?")
                magnet = f"magnet:?xt=urn:btih:{h}&dn={urllib.parse.quote(title_long)}{TRACKERS}"
                subprocess.run([
                    "aria2c", "--daemon=true", "--seed-time=0",
                    "--max-connection-per-server=16", "--bt-max-peers=80",
                    "--follow-torrent=mem", f"--dir={fp}", magnet
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  [STARTED] {quality} | {size} | {name}")
            else:
                print(f"  [WARN] Torrent tidak ditemukan")
        else:
            print(f"  [WARN] YTS tidak menemukan {name}")

    # Sub Indonesia
    sub_path = os.path.join(fp, f"{folder}.id.srt")
    existing_sub_size = os.path.getsize(sub_path) if os.path.exists(sub_path) else 0
    if existing_sub_size > 1000:
        print(f"  [SUB OK] Sub Indonesia sudah ada ({existing_sub_size//1024}KB)")
    else:
        if fetch_sub(imdb, sub_path):
            print(f"  [SUB OK] Sub Indonesia berhasil diunduh")
        else:
            print(f"  [SUB MISS] Tidak tersedia di OpenSubtitles")

    time.sleep(1)

print(f"\n{'='*60}")
print("✅ DEADPOOL TRILOGY DOWNLOAD SELESAI DIANTREKAN!")
print(f"{'='*60}")
