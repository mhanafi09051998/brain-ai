import urllib.request, os

base_dir = '/home/ubuntu/apps/zolu-movie/public/images'

mirrors = {
    'posters/x-men-first-class.jpg': [
        'https://m.media-amazon.com/images/M/MV5BMTg5OTMxNzk4Nl5BMl5BanBnXkFtZTcwOTk1MjAwNQ@@._V1_FMjpg_UX1000_.jpg',
        'https://upload.wikimedia.org/wikipedia/en/5/55/X-MenFirstClassEnglishPoster.jpg'
    ],
    'backdrops/john-wick-chapter-4.jpg': [
        'https://image.tmdb.org/t/p/w1280/7I6VUdPj6tQECNHdviJkUHD2389.jpg',
        'https://image.tmdb.org/t/p/original/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg',
        'https://wallpapers.com/images/hd/john-wick-chapter-4-sunset-art-982h9q3gq92k0e79.jpg'
    ],
    'backdrops/glass-onion-a-knives-out-mystery.jpg': [
        'https://image.tmdb.org/t/p/w1280/dKQA850uvbNSCaQCV4Im1XlzEtQ.jpg',
        'https://image.tmdb.org/t/p/original/vDGr1YdrlfbU9wxTOdpf3zChmv9.jpg',
        'https://wallpapers.com/images/hd/glass-onion-a-knives-out-mystery-daniel-craig-poolside-k9f0m7j1e4e2v0f7.jpg'
    ]
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

for rel_path, url_list in mirrors.items():
    dest = os.path.join(base_dir, rel_path)
    for url in url_list:
        try:
            req = urllib.request.Request(url, headers=headers)
            data = urllib.request.urlopen(req, timeout=15).read()
            if len(data) > 5000:
                with open(dest, 'wb') as f:
                    f.write(data)
                print(f"[OK] Downloaded {rel_path} from {url} ({len(data)} bytes)")
                break
        except Exception as e:
            print(f"[RETRY] {rel_path} failed on {url}: {e}")
