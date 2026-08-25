#!/usr/bin/env python3
"""
1. Download semua film Avengers (1080p) via YTS + aria2c
2. Fetch sub Indonesia via OpenSubtitles REST (no-key)
3. Hapus film tanpa sub Indonesia dari storage
"""
import urllib.request, urllib.parse, json, subprocess, os, time, gzip, shutil

AVENGERS = [
    {"name": "Iron Man",                    "year": "2008", "imdb": "0371746",  "folder": "Iron Man (2008)"},
    {"name": "The Incredible Hulk",         "year": "2008", "imdb": "0800080",  "folder": "The Incredible Hulk (2008)"},
    {"name": "Iron Man 2",                  "year": "2010", "imdb": "1228705",  "folder": "Iron Man 2 (2010)"},
    {"name": "Thor",                        "year": "2011", "imdb": "0800369",  "folder": "Thor (2011)"},
    {"name": "Captain America: The First Avenger", "year": "2011", "imdb": "0458339", "folder": "Captain America - The First Avenger (2011)"},
    {"name": "The Avengers",               "year": "2012", "imdb": "0848228",  "folder": "The Avengers (2012)"},
    {"name": "Thor: The Dark World",       "year": "2013", "imdb": "1981115",  "folder": "Thor - The Dark World (2013)"},
    {"name": "Captain America: The Winter Soldier", "year": "2014", "imdb": "1843866", "folder": "Captain America - The Winter Soldier (2014)"},
    {"name": "Guardians of the Galaxy",    "year": "2014", "imdb": "2015381",  "folder": "Guardians of the Galaxy (2014)"},
    {"name": "Avengers: Age of Ultron",    "year": "2015", "imdb": "2395427",  "folder": "Avengers - Age of Ultron (2015)"},
    {"name": "Ant-Man",                    "year": "2015", "imdb": "0478970",  "folder": "Ant-Man (2015)"},
    {"name": "Captain America: Civil War", "year": "2016", "imdb": "3498820",  "folder": "Captain America - Civil War (2016)"},
    {"name": "Doctor Strange",             "year": "2016", "imdb": "3960798",  "folder": "Doctor Strange (2016)"},
    {"name": "Guardians of the Galaxy Vol. 2", "year": "2017", "imdb": "3896198", "folder": "Guardians of the Galaxy Vol 2 (2017)"},
    {"name": "Thor: Ragnarok",             "year": "2017", "imdb": "3501632",  "folder": "Thor - Ragnarok (2017)"},
    {"name": "Black Panther",              "year": "2018", "imdb": "1825683",  "folder": "Black Panther (2018)"},
    {"name": "Avengers: Infinity War",     "year": "2018", "imdb": "4154756",  "folder": "Avengers - Infinity War (2018)"},
    {"name": "Ant-Man and the Wasp",       "year": "2018", "imdb": "5095030",  "folder": "Ant-Man and the Wasp (2018)"},
    {"name": "Captain Marvel",             "year": "2019", "imdb": "4154664",  "folder": "Captain Marvel (2019)"},
    {"name": "Avengers: Endgame",          "year": "2019", "imdb": "4154796",  "folder": "Avengers - Endgame (2019)"},
    {"name": "Spider-Man: Homecoming",     "year": "2017", "imdb": "2250912",  "folder": "Spider-Man - Homecoming (2017)"},
    {"name": "Spider-Man: Far From Home",  "year": "2019", "imdb": "6320628",  "folder": "Spider-Man - Far From Home (2019)"},
    {"name": "Spider-Man: No Way Home",    "year": "2021", "imdb": "10872600", "folder": "Spider-Man - No Way Home (2021)"},
]

DEST_BASE = "/home/ubuntu/media_storage/movies/Box Office & Masterpiece"
UA = "TemporaryUserAgent v1.0"
TRACKERS = "&tr=".join([
    "",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.tracker.cl:1337/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://tracker.torrent.eu.org:451/announce"
])

def search_yts(title):
    clean = title.replace(":", "").replace("-", " ")
    for domain in ["yts.mx", "yts.lt", "yts.am"]:
        try:
            url = f"https://{domain}/api/v2/list_movies.json?query_term={urllib.parse.quote(clean)}&limit=5"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
            movies = data.get("data", {}).get("movies", [])
            for m in movies:
                if str(m.get("year")) in title or True:
                    return m
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

# ── DELETE films without ID sub ──────────────────────────────────
NO_SUB_FILMS = [
    "A Nymphoid Barbarian in Dinosaur Hell (1990)",
    "Chris Claremont's X-Men (2018)",
    "Oppenheimer - The Real Story (2023)",
    "The Science of Interstellar (2015)",
    "Stealing Pulp Fiction (2024)",
    "The Substance of Fire (1996)",
]

print("=" * 60)
print("🗑️  MENGHAPUS FILM TANPA SUB INDONESIA")
print("=" * 60)
deleted = 0
for genre in os.listdir("/home/ubuntu/media_storage/movies"):
    gp = os.path.join("/home/ubuntu/media_storage/movies", genre)
    if not os.path.isdir(gp):
        continue
    for mdir in os.listdir(gp):
        if mdir in NO_SUB_FILMS:
            full = os.path.join(gp, mdir)
            shutil.rmtree(full)
            print(f"  [DELETED] {mdir}")
            deleted += 1
print(f"Total dihapus: {deleted} folder\n")

# ── DOWNLOAD AVENGERS ────────────────────────────────────────────
print("=" * 60)
print(f"⬇️  DOWNLOAD {len(AVENGERS)} FILM AVENGERS/MCU (1080p)")
print("=" * 60)

started = 0
sub_ok = 0

for m in AVENGERS:
    name = m["name"]
    year = m["year"]
    imdb = m["imdb"]
    folder_name = m["folder"]
    folder_path = os.path.join(DEST_BASE, folder_name)
    std_mp4 = os.path.join(folder_path, f"{folder_name}.mp4")

    # Skip if already exists with video
    if os.path.isdir(folder_path):
        has_video = any(f.lower().endswith((".mp4", ".mkv")) for f in os.listdir(folder_path))
        if has_video:
            print(f"  [SKIP] {name} - sudah ada")
            # Still try to fetch sub if missing
            has_sub = any(f.endswith(".id.srt") for f in os.listdir(folder_path))
            if not has_sub:
                sub_path = os.path.join(folder_path, f"{folder_name}.id.srt")
                if fetch_sub(imdb, sub_path):
                    print(f"    [SUB OK] Sub Indonesia ditambahkan")
                    sub_ok += 1
            continue

    print(f"\n▶ {name} ({year})")
    os.makedirs(folder_path, exist_ok=True)

    # Search YTS
    movie_data = search_yts(f"{name} {year}")
    if movie_data:
        # Pick 1080p if available, fallback 720p
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
                "--follow-torrent=mem", f"--dir={folder_path}", magnet
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  [STARTED] {quality} | {size} | {name}")
            started += 1
        else:
            print(f"  [WARN] Torrent tidak ditemukan untuk {name}")
    else:
        print(f"  [WARN] YTS tidak menemukan {name}")

    # Fetch sub
    sub_path = os.path.join(folder_path, f"{folder_name}.id.srt")
    if fetch_sub(imdb, sub_path):
        print(f"  [SUB OK] Sub Indonesia tersimpan")
        sub_ok += 1
    else:
        print(f"  [SUB MISS] Sub Indonesia tidak tersedia di OpenSubtitles")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"✅ Download dimulai: {started} film")
print(f"✅ Sub Indonesia   : {sub_ok} film")
print(f"{'='*60}")
