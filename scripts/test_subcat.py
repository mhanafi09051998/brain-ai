import urllib.request, urllib.parse, re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.subtitlecat.com/index.php?search=' + urllib.parse.quote('Top Gun Maverick')
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf-8')

for m in re.finditer(r'<td[^>]*>(.*?)</td>', html, re.DOTALL):
    text = m.group(1).strip()
    if 'href=' in text:
        print(text[:120])
