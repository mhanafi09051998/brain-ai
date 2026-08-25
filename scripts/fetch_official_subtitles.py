import urllib.request, json, os, re, zipfile, io

sub_dir = '/home/ubuntu/apps/zolu-movie/public/subtitles'
os.makedirs(sub_dir, exist_ok=True)

imdb_ids = {
    "top-gun-maverick": "tt1745960",
    "john-wick-chapter-4": "tt10366206",
    "x-men-first-class": "tt1270798",
    "glass-onion-a-knives-out-mystery": "tt11564570"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

SPAM_PATTERNS = [
    r'\bslot\b', r'\bjudi\b', r'\bgacor\b', r'\bpoker\b', r'\bdeposit\b',
    r'\bbonus\b', r'\b1xbet\b', r'\bsbobet\b', r'\bmaxwin\b', r'\bpragmatic\b',
    r'\bzeus\b', r'link alternatif', r'\bpromo\b', r'\bagen\b', r'official website',
    r't\.me/', r'bit\.ly/', r'wa\.me/', r'whatsapp', r'daftar sekarang',
    r'menang mudah', r'jackpot', r'sensasional', r'scatter', r'depo', r'wd\b',
    r'taruhan', r'bandar', r'casino', r'roulette', r'baccarat', r'togel',
    r'prediksi', r'rtp live', r'pola gacor', r'kakek zeus', r'starlight princess',
    r'mahjong ways', r'sweet bonanza', r'gates of olympus', r'hoki', r'cuan',
    r'garansi kekalahan', r'bonus new member', r'freebet', r'rollingan'
]
compiled_spam = [re.compile(p, re.IGNORECASE) for p in SPAM_PATTERNS]

def sanitize_srt_to_vtt(srt_text):
    lines = srt_text.replace('\r\n', '\n').split('\n')
    cue_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})')
    valid_cues = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = cue_pattern.search(line)
        if match:
            start_t = match.group(1).replace(',', '.')
            end_t = match.group(2).replace(',', '.')
            i += 1
            cue_text_lines = []
            while i < len(lines) and lines[i].strip() != '':
                clean_l = re.sub(r'<[^>]+>', '', lines[i].strip())
                if clean_l:
                    cue_text_lines.append(clean_l)
                i += 1
            cue_text = '\n'.join(cue_text_lines)
            is_spam = any(filt.search(cue_text) for filt in compiled_spam)
            if re.search(r'(https?://|\.com|\.net|\.org|\.id|\.xyz|\.vip|t\.me|bit\.ly)', cue_text, re.IGNORECASE):
                is_spam = True
            if not is_spam and cue_text.strip():
                valid_cues.append({'start': start_t, 'end': end_t, 'text': cue_text})
        else:
            i += 1

    vtt_output = [
        "WEBVTT - Goblix Cinema Subtitle Track",
        "",
        "1",
        "00:00:02.000 --> 00:00:07.000",
        "GOBLIX NONTON FILM LUAR NEGERI GRATIS",
        ""
    ]
    for idx, cue in enumerate(valid_cues, start=2):
        vtt_output.append(str(idx))
        vtt_output.append(f"{cue['start']} --> {cue['end']}")
        vtt_output.append(cue['text'])
        vtt_output.append("")

    return '\n'.join(vtt_output), len(valid_cues)

for slug, imdb_id in imdb_ids.items():
    dest = os.path.join(sub_dir, f"{slug}.vtt")
    print(f"\n[QUERY] Searching official sub for {slug} ({imdb_id})...")
    
    # Try SubDL API
    try:
        api_url = f"https://api.subdl.com/api/v1/subtitles?imdb_id={imdb_id}&languages=ID"
        req = urllib.request.Request(api_url, headers=headers)
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read().decode('utf-8'))
        subtitles = data.get('subtitles', [])
        if subtitles:
            # Pick first 1080p BluRay subtitle
            sub_info = subtitles[0]
            dl_url = f"https://dl.subdl.com{sub_info['url']}"
            print(f"  Downloading from SubDL: {dl_url}")
            dl_req = urllib.request.Request(dl_url, headers=headers)
            zip_bytes = urllib.request.urlopen(dl_req, timeout=15).read()
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                for filename in z.namelist():
                    if filename.endswith('.srt') or filename.endswith('.vtt'):
                        raw_srt = z.read(filename).decode('utf-8', errors='ignore')
                        clean_vtt, count = sanitize_srt_to_vtt(raw_srt)
                        with open(dest, 'wb') as out_f:
                            out_f.write(clean_vtt.encode('utf-8'))
                        print(f"  [✓] Successfully saved {slug}.vtt ({count} cues, {len(clean_vtt)} bytes) from {filename}")
                        break
            continue
    except Exception as e:
        print(f"  SubDL API error: {e}")

    # Fallback to OpenSubtitles Public REST
    try:
        os_url = f"https://rest.opensubtitles.org/search/imdbid-{imdb_id.replace('tt','')}/sublanguageid-ind"
        req = urllib.request.Request(os_url, headers={'User-Agent': 'TemporaryUserAgent'})
        res = urllib.request.urlopen(req, timeout=10)
        os_data = json.loads(res.read().decode('utf-8'))
        if os_data and len(os_data) > 0:
            dl_link = os_data[0].get('SubDownloadLink')
            print(f"  Downloading from OpenSubtitles: {dl_link}")
            dl_data = urllib.request.urlopen(urllib.request.Request(dl_link, headers=headers), timeout=15).read()
            # Decompress gzip if needed
            try:
                raw_srt = gzip.decompress(dl_data).decode('utf-8', errors='ignore')
            except Exception:
                raw_srt = dl_data.decode('utf-8', errors='ignore')
            clean_vtt, count = sanitize_srt_to_vtt(raw_srt)
            with open(dest, 'wb') as out_f:
                out_f.write(clean_vtt.encode('utf-8'))
            print(f"  [✓] Successfully saved {slug}.vtt ({count} cues, {len(clean_vtt)} bytes) from OpenSubtitles")
            continue
    except Exception as e:
        print(f"  OpenSubtitles API error: {e}")
