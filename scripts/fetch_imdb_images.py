import urllib.request, json, os, re

base_dir = '/home/ubuntu/apps/zolu-movie/public/images'
os.makedirs(os.path.join(base_dir, 'posters'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'backdrops'), exist_ok=True)

# Guaranteed reliable image sources (Wikimedia / TMDB Official / Fanart)
sources = {
    "top-gun-maverick": {
        "poster": "https://image.tmdb.org/t/p/w780/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/AaV1YIdWKnjAIAOe8UUKBFm327v.jpg"
    },
    "john-wick-chapter-4": {
        "poster": "https://image.tmdb.org/t/p/w780/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/7I6VUdPj6tQECNHdviJkUHD2389.jpg"
    },
    "x-men-first-class": {
        "poster": "https://image.tmdb.org/t/p/w780/7t2k9xK31y4A2rK9ZlHhWwT8L0d.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/2uNW4WbgBXL2544qGLOxOT93Ahd.jpg"
    },
    "glass-onion-a-knives-out-mystery": {
        "poster": "https://image.tmdb.org/t/p/w780/vDGr1YdrlfbU9wxTOdpf3zChmv9.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w1280/dKQA850uvbNSCaQCV4Im1XlzEtQ.jpg"
    }
}

# Fallbacks if TMDB image hash changes: fetch from YTS movie details
yts_slugs = {
    "top-gun-maverick": "top-gun-maverick-2022",
    "john-wick-chapter-4": "john-wick-chapter-4-2023",
    "x-men-first-class": "x-men-first-class-2011",
    "glass-onion-a-knives-out-mystery": "glass-onion-a-knives-out-mystery-2022"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for slug, yts_name in yts_slugs.items():
    p_dest = os.path.join(base_dir, 'posters', f'{slug}.jpg')
    b_dest = os.path.join(base_dir, 'backdrops', f'{slug}.jpg')

    # Fetch from YTS API
    try:
        api_url = f'https://yts.mx/api/v2/list_movies.json?query_term={yts_name}'
        req = urllib.request.Request(api_url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode('utf-8'))
        movie_obj = data['data']['movies'][0]
        p_url = movie_obj.get('large_cover_image') or movie_obj.get('medium_cover_image')
        b_url = movie_obj.get('background_image_original') or movie_obj.get('background_image')
        
        print(f"[{slug}] YTS Poster: {p_url}")
        print(f"[{slug}] YTS Backdrop: {b_url}")

        if p_url:
            p_data = urllib.request.urlopen(urllib.request.Request(p_url, headers=headers), timeout=15).read()
            with open(p_dest, 'wb') as f:
                f.write(p_data)
            print(f"  [OK] Saved Poster ({len(p_data)} bytes)")

        if b_url:
            b_data = urllib.request.urlopen(urllib.request.Request(b_url, headers=headers), timeout=15).read()
            with open(b_dest, 'wb') as f:
                f.write(b_data)
            print(f"  [OK] Saved Backdrop ({len(b_data)} bytes)")

    except Exception as e:
        print(f"[{slug}] YTS API error: {e}")
