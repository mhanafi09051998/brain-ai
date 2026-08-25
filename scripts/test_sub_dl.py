import urllib.request, re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.subtitlecat.com/subs/1379/Top.Gun.Maverick.2022.1080p.BluRay.x264.AAC5.1-%5BYTS.MX%5D.html'
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf-8')

for m in re.finditer(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', html):
    href, text = m.group(1), m.group(2)
    if 'indonesian' in text.lower() or 'download' in href.lower() or 'id.srt' in href.lower() or 'indonesian' in href.lower():
        print(href, '-->', text)
