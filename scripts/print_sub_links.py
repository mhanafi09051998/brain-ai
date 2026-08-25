import urllib.request, re

url = 'https://yts-subs.com/subtitles/x-men-first-class-2011-indonesian-yify-88254'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

all_links = re.findall(r'href="([^"]+)"', html)
print("All links on sub page:")
for l in all_links:
    if 'download' in l or 'sub' in l or 'zip' in l:
        print("  ->", l)
