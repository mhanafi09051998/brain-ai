import urllib.request, re, zipfile, io, os

url = 'https://yts-subs.com/movie-imdb/tt1745960'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

matches = re.findall(r'<tr[^>]*>.*?Indonesian.*?href="(/subtitles/[^"]+)".*?</tr>', html, re.DOTALL | re.IGNORECASE)
if not matches:
    matches = re.findall(r'href="(/subtitles/[^"]+)"', html)

print(f'Found {len(matches)} subtitle matches')
if matches:
    sub_page_url = 'https://yts-subs.com' + matches[0]
    req_sub = urllib.request.Request(sub_page_url, headers={'User-Agent': 'Mozilla/5.0'})
    sub_html = urllib.request.urlopen(req_sub).read().decode('utf-8', errors='ignore')

    zip_match = re.search(r'href="([^"]+\.zip)"', sub_html)
    if zip_match:
        zip_url = zip_match.group(1)
        if not zip_url.startswith('http'):
            zip_url = 'https://yts-subs.com' + zip_url

        print(f'Downloading zip from: {zip_url}')
        req_zip = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
        zip_bytes = urllib.request.urlopen(req_zip).read()

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for fname in z.namelist():
                if fname.endswith('.srt') or fname.endswith('.vtt'):
                    print(f'Extracting: {fname}')
                    srt_content = z.read(fname).decode('utf-8', errors='ignore')

                    # Convert to VTT format
                    vtt_text = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', srt_content)

                    FORBIDDEN_WORDS = [
                        r'\bslot\b', r'\bjudi\b', r'\bgacor\b', r'\bpoker\b', r'\bdeposit\b',
                        r'\bbonus\b', r'\b1xbet\b', r'\bsbobet\b', r'\bmaxwin\b', r'\bpragmatic\b',
                        r'\bzeus\b', r'link alternatif', r'\bpromo\b', r'\bagen\b', r'official website',
                        r't\.me/', r'bit\.ly/'
                    ]

                    lines = vtt_text.splitlines()
                    clean_lines = []
                    for line in lines:
                        is_spam = any(re.search(pat, line, re.IGNORECASE) for pat in FORBIDDEN_WORDS)
                        clean_lines.append('' if is_spam else line)

                    header = 'WEBVTT - Goblix Subtitle Track\n\n1\n00:00:02.000 --> 00:00:07.000\nGOBLIX NONTON FILM LUAR NEGERI GRATIS\n\n'
                    final_vtt = header + '\n'.join(clean_lines)

                    dest = '/home/ubuntu/apps/zolu-movie/public/subtitles/top-gun-maverick.vtt'
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(dest, 'w', encoding='utf-8') as f:
                        f.write(final_vtt)
                    print(f'SUCCESS! SAVED CLEAN FULL VTT TO: {dest} (Length: {len(final_vtt)} bytes)')
                    break
