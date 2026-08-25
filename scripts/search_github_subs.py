import urllib.request, json, os, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Search GitHub repositories for Indonesian subtitles
queries = {
    "top-gun-maverick": "Top Gun Maverick Indonesian extension:srt",
    "john-wick-chapter-4": "John Wick Chapter 4 Indonesian extension:srt",
    "x-men-first-class": "X-Men First Class Indonesian extension:srt",
    "glass-onion-a-knives-out-mystery": "Glass Onion Indonesian extension:srt"
}

for slug, q in queries.items():
    url = f"https://api.github.com/search/code?q={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode('utf-8'))
        items = data.get('items', [])
        print(f"[{slug}] Found {len(items)} files on GitHub")
        for item in items[:3]:
            raw_url = item.get('html_url', '').replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
            print(f"  Candidate: {raw_url}")
    except Exception as e:
        print(f"[{slug}] Search error: {e}")
