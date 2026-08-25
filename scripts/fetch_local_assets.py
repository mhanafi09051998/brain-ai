import urllib.request, os

base_dir = '/home/ubuntu/apps/zolu-movie/public/images'
os.makedirs(os.path.join(base_dir, 'posters'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'backdrops'), exist_ok=True)

images = {
    'posters/top-gun-maverick.jpg': 'https://image.tmdb.org/t/p/w780/62HCnUTziyWcpDaBO2i1DX17ljH.jpg',
    'backdrops/top-gun-maverick.jpg': 'https://image.tmdb.org/t/p/original/7mWHXEmksbrkMhtkFeClzNKu7mk.jpg',
    'posters/john-wick-chapter-4.jpg': 'https://image.tmdb.org/t/p/w780/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg',
    'backdrops/john-wick-chapter-4.jpg': 'https://image.tmdb.org/t/p/original/h8gHn0OzBoaefW7AtBqWj0ALTq4.jpg',
    'posters/x-men-first-class.jpg': 'https://image.tmdb.org/t/p/w780/vU14YkL93O36O0aG16C1U4m5eH3.jpg',
    'backdrops/x-men-first-class.jpg': 'https://image.tmdb.org/t/p/original/gCctDK5RCPRMjgYAoV6yxNE7f93.jpg',
    'posters/glass-onion-a-knives-out-mystery.jpg': 'https://image.tmdb.org/t/p/w780/vDGr1YdrlfbU9wxTOdpf3zChmv9.jpg',
    'backdrops/glass-onion-a-knives-out-mystery.jpg': 'https://image.tmdb.org/t/p/original/bKxiLRP0Qm2JwBh0PbpTRJKhZy5.jpg'
}

for rel_path, url in images.items():
    dest = os.path.join(base_dir, rel_path)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        data = urllib.request.urlopen(req, timeout=15).read()
        with open(dest, 'wb') as f:
            f.write(data)
        print(f"[OK] Downloaded {rel_path} ({len(data)} bytes)")
    except Exception as e:
        print(f"[FAIL] {rel_path}: {e}")
