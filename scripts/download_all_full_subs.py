import urllib.request, re, zipfile, io, os, sys

def download_full_sub(imdb_id, output_slug):
    url = f'https://yts-subs.com/movie-imdb/{imdb_id}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error opening {url}:", e)
        return False

    matches = re.findall(r'<tr[^>]*>.*?Indonesian.*?href="(/subtitles/[^"]+)".*?</tr>', html, re.DOTALL | re.IGNORECASE)
    if not matches:
        matches = re.findall(r'href="(/subtitles/[^"]+)"', html)

    print(f'[{imdb_id}] Found {len(matches)} subtitle matches for {output_slug}')
    if not matches:
        return False

    sub_page_url = 'https://yts-subs.com' + matches[0]
    req_sub = urllib.request.Request(sub_page_url, headers={'User-Agent': 'Mozilla/5.0'})
    sub_html = urllib.request.urlopen(req_sub, timeout=15).read().decode('utf-8', errors='ignore')

    zip_match = re.search(r'href="([^"]+\.zip)"', sub_html)
    if not zip_match:
        return False

    zip_url = zip_match.group(1)
    if not zip_url.startswith('http'):
        zip_url = 'https://yts-subs.com' + zip_url

    print(f'[{imdb_id}] Downloading zip: {zip_url}')
    req_zip = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
    zip_bytes = urllib.request.urlopen(req_zip, timeout=30).read()

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

                dest1 = f'/home/ubuntu/apps/zolu-movie/public/subtitles/{output_slug}.vtt'
                dest2 = f'/home/ubuntu/apps/zolu-movie/public/{output_slug}.vtt'
                os.makedirs(os.path.dirname(dest1), exist_ok=True)
                with open(dest1, 'w', encoding='utf-8') as f:
                    f.write(final_vtt)
                with open(dest2, 'w', encoding='utf-8') as f:
                    f.write(final_vtt)
                if output_slug == 'x-men-first-class':
                    with open('/home/ubuntu/apps/zolu-movie/public/sub_indo.vtt', 'w', encoding='utf-8') as f:
                        f.write(final_vtt)
                print(f'SUCCESS! Saved full clean subtitle for {output_slug} ({len(final_vtt)} bytes, {len(clean_lines)} lines)')
                return True
    return False

# Download for all movies in catalog
movies = [
    ("tt1270798", "x-men-first-class"),
    ("tt1745960", "top-gun-maverick"),
    ("tt10366206", "john-wick-chapter-4"),
    ("tt11564570", "glass-onion-a-knives-out-mystery")
]

for imdb_id, slug in movies:
    download_full_sub(imdb_id, slug)
