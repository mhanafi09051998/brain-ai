import urllib.request
import re
import json

url = "https://www.themoviedb.org/movie/49538-x-men-first-class/images/backdrops"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
paths = re.findall(r'/t/p/[^/]+(/[^"\'\s]+\.jpg)', html)
unique_paths = list(set(paths))
print(f"Total backdrops found: {len(unique_paths)}")
for p in unique_paths[:10]:
    print(f"https://image.tmdb.org/t/p/original{p}")
