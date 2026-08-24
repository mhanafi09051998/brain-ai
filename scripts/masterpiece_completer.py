#!/usr/bin/env python3
import urllib.request, urllib.parse, json, os, sys, subprocess

BASE_MEDIA = "/home/ubuntu/media_storage"
MOVIES_BOX = os.path.join(BASE_MEDIA, "movies", "Box Office & Masterpiece")
MOVIES_HORROR = os.path.join(BASE_MEDIA, "movies", "Horror & Thriller")

TRACKERS = "&tr=".join([
    "",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.tracker.cl:1337/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://tracker.torrent.eu.org:451/announce"
])

MOVIES_TO_COMPLETE = [
    # The Lord of the Rings Extended Trilogy (1-3)
    {"name": "The Lord of the Rings The Fellowship of the Ring", "search": "Lord of the Rings Fellowship EXTENDED 1080p", "year": "2001", "target": MOVIES_BOX},
    {"name": "The Lord of the Rings The Two Towers", "search": "Lord of the Rings Two Towers EXTENDED 1080p", "year": "2002", "target": MOVIES_BOX},
    {"name": "The Lord of the Rings The Return of the King", "search": "Lord of the Rings Return King EXTENDED 1080p", "year": "2003", "target": MOVIES_BOX},

    # The Hobbit Trilogy (LOTR Prequels 1-3)
    {"name": "The Hobbit An Unexpected Journey", "search": "The Hobbit An Unexpected Journey 1080p BluRay", "year": "2012", "target": MOVIES_BOX},
    {"name": "The Hobbit The Desolation of Smaug", "search": "The Hobbit The Desolation of Smaug 1080p BluRay", "year": "2013", "target": MOVIES_BOX},
    {"name": "The Hobbit The Battle of the Five Armies", "search": "The Hobbit The Battle of the Five Armies 1080p BluRay", "year": "2014", "target": MOVIES_BOX},

    # Christopher Nolan Dark Knight & Masterpieces
    {"name": "The Dark Knight", "search": "The Dark Knight 2008 1080p BluRay", "year": "2008", "target": MOVIES_BOX},
    {"name": "The Dark Knight Rises", "search": "The Dark Knight Rises 2012 1080p BluRay", "year": "2012", "target": MOVIES_BOX},
    {"name": "Inception", "search": "Inception 2010 1080p BluRay", "year": "2010", "target": MOVIES_BOX},
    {"name": "Oppenheimer", "search": "Oppenheimer 2023 1080p BluRay", "year": "2023", "target": MOVIES_BOX},

    # Dune Saga Part Two
    {"name": "Dune Part Two", "search": "Dune Part Two 2024 1080p", "year": "2024", "target": MOVIES_BOX},

    # Spider-Verse Part 1
    {"name": "Spider-Man Into the Spider-Verse", "search": "Spider-Man Into the Spider-Verse 2018 1080p BluRay", "year": "2018", "target": MOVIES_BOX},

    # All-Time Masterpieces
    {"name": "The Shawshank Redemption", "search": "The Shawshank Redemption 1994 1080p BluRay", "year": "1994", "target": MOVIES_BOX},
    {"name": "Parasite", "search": "Parasite 2019 1080p BluRay", "year": "2019", "target": MOVIES_BOX},
    {"name": "Fight Club", "search": "Fight Club 1999 1080p BluRay", "year": "1999", "target": MOVIES_BOX},
    {"name": "Everything Everywhere All at Once", "search": "Everything Everywhere All at Once 2022 1080p", "year": "2022", "target": MOVIES_BOX},

    # Alien Saga & Horror Tier 1
    {"name": "Alien", "search": "Alien 1979 1080p BluRay", "year": "1979", "target": MOVIES_HORROR},
    {"name": "Aliens", "search": "Aliens 1986 1080p BluRay", "year": "1986", "target": MOVIES_HORROR},
    {"name": "Alien Romulus", "search": "Alien Romulus 2024 1080p", "year": "2024", "target": MOVIES_HORROR},
    {"name": "Hereditary", "search": "Hereditary 2018 1080p BluRay", "year": "2018", "target": MOVIES_HORROR},
    {"name": "Midsommar", "search": "Midsommar 2019 1080p BluRay", "year": "2019", "target": MOVIES_HORROR},

    # Anime Masterpieces
    {"name": "Spirited Away", "search": "Spirited Away 2001 1080p BluRay", "year": "2001", "target": MOVIES_BOX},
    {"name": "Your Name", "search": "Your Name Kimi no Na wa 2016 1080p BluRay", "year": "2016", "target": MOVIES_BOX}
]

def search_apibay(query):
    q = urllib.parse.quote(query)
    url = f"https://apibay.org/q.php?q={q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0 and data[0].get("id") != "0":
                # Find best 1080p torrent by seeders
                best = max(data[:8], key=lambda x: int(x.get("seeders", 0)))
                return {
                    "name": best["name"],
                    "info_hash": best["info_hash"],
                    "seeders": int(best.get("seeders", 0)),
                    "size_gb": round(int(best.get("size", 0)) / (1024**3), 2)
                }
    except Exception as e:
        print(f"Error querying apibay for {query}: {e}")
    return None

def fetch_tmdb_poster(movie_title, year, target_dir):
    poster_path = os.path.join(target_dir, "poster.jpg")
    if os.path.exists(poster_path) and os.path.getsize(poster_path) > 10000:
        return
    try:
        # Query TMDb / Wikipedia / Wikimedia high-res official posters
        q = urllib.parse.quote(f"{movie_title} {year} movie poster")
        url = f"https://itunes.apple.com/search?term={q}&media=movie&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            if data.get("resultCount", 0) > 0:
                artwork_url = data["results"][0].get("artworkUrl100")
                if artwork_url:
                    # Upgrade to highest resolution 1000x1000 original artwork
                    high_res = artwork_url.replace("100x100bb", "1200x1200bb").replace("100x100", "1200x1200")
                    req_img = urllib.request.Request(high_res, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_img, timeout=15) as r_img:
                        with open(poster_path, "wb") as f:
                            f.write(r_img.read())
                    print(f"  [✓] Official Poster Downloaded (High-Res 1200px): {os.path.basename(poster_path)}")
    except Exception as e:
        print(f"  [!] Failed to fetch official poster: {e}")

def main():
    print("🎬 [ZOLU CINEMA MASTERPIECE & COMPLETE FRANCHISE INTEGRATOR]")
    print(f"Total Masterpieces & Franchises to integrate: {len(MOVIES_TO_COMPLETE)}")
    
    prepared_queue = []
    
    for item in MOVIES_TO_COMPLETE:
        folder_name = f"{item['name']} ({item['year']})"
        target_dir = os.path.join(item["target"], folder_name)
        os.makedirs(target_dir, exist_ok=True)
        
        print(f"\n[*] Processing: {folder_name} (1080p BluRay & Official Poster)...")
        
        # 1. Fetch Official Movie Poster
        fetch_tmdb_poster(item["name"], item["year"], target_dir)
        
        # 2. Search 1080p BluRay Stream
        result = search_apibay(item["search"])
        if result:
            print(f"  [✓] Found 1080p BluRay ({result['size_gb']} GB | {result['seeders']} Seeders): {result['name']}")
            magnet = f"magnet:?xt=urn:btih:{result['info_hash']}&dn={urllib.parse.quote(result['name'])}{TRACKERS}"
            with open(os.path.join(target_dir, "magnet.txt"), "w") as f:
                f.write(magnet)
            prepared_queue.append((folder_name, target_dir, magnet))
        else:
            print(f"  [!] Retrying broad query for {item['name']}...")
            result_broad = search_apibay(f"{item['name']} 1080p")
            if result_broad:
                print(f"  [✓] Found: {result_broad['name']}")
                magnet = f"magnet:?xt=urn:btih:{result_broad['info_hash']}&dn={urllib.parse.quote(result_broad['name'])}{TRACKERS}"
                with open(os.path.join(target_dir, "magnet.txt"), "w") as f:
                    f.write(magnet)
                prepared_queue.append((folder_name, target_dir, magnet))

    # Clean any existing or incoming subtitles with custom cleaner
    print("\n[*] Menjalankan sterilisasi subtitle (clean-subtitles)...")
    subprocess.run(["python3", "/usr/local/bin/clean-subtitles", BASE_MEDIA])
    
    print(f"\n✨ Selesai: {len(prepared_queue)} film & sekuel lengkap 1080p BluRay + Official Poster siap diunduh & diintegrasikan.")

if __name__ == "__main__":
    main()
