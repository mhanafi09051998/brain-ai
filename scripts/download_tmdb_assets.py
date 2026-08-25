import urllib.request, json, os

base_dir = '/home/ubuntu/apps/zolu-movie/public/images'
os.makedirs(os.path.join(base_dir, 'posters'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'backdrops'), exist_ok=True)

# Verified TMDB image URLs
movies_images = {
    "top-gun-maverick": {
        "poster": "https://image.tmdb.org/t/p/w780/62HCnUTziyWcpDaBO2i1DX17ljH.jpg",
        "backdrop": "https://image.tmdb.org/t/p/original/AaV1YIdWKnjAIAOe8UUKBFm327v.jpg"
    },
    "john-wick-chapter-4": {
        "poster": "https://image.tmdb.org/t/p/w780/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg",
        "backdrop": "https://image.tmdb.org/t/p/original/h8gHn0OzBoaefW7AtBqWj0ALTq4.jpg"
    },
    "x-men-first-class": {
        "poster": "https://image.tmdb.org/t/p/w780/vU14YkL93O36O0aG16C1U4m5eH3.jpg",
        "backdrop": "https://image.tmdb.org/t/p/original/gCctDK5RCPRMjgYAoV6yxNE7f93.jpg"
    },
    "glass-onion-a-knives-out-mystery": {
        "poster": "https://image.tmdb.org/t/p/w780/vDGr1YdrlfbU9wxTOdpf3zChmv9.jpg",
        "backdrop": "https://image.tmdb.org/t/p/original/bKxiLRP0Qm2JwBh0PbpTRJKhZy5.jpg"
    }
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for slug, urls in movies_images.items():
    p_dest = os.path.join(base_dir, 'posters', f'{slug}.jpg')
    b_dest = os.path.join(base_dir, 'backdrops', f'{slug}.jpg')

    for img_type, url in urls.items():
        dest = p_dest if img_type == 'poster' else b_dest
        try:
            req = urllib.request.Request(url, headers=headers)
            data = urllib.request.urlopen(req, timeout=20).read()
            with open(dest, 'wb') as f:
                f.write(data)
            print(f"[OK] Saved {slug} {img_type} ({len(data)} bytes)")
        except Exception as e:
            print(f"[FAIL] {slug} {img_type} ({url}): {e}")
