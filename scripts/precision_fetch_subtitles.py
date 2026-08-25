import urllib.request, urllib.parse, re, os

sub_dir = '/home/ubuntu/apps/zolu-movie/public/subtitles'
os.makedirs(sub_dir, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# High precision search queries on SubtitleCat
targets = {
    "top-gun-maverick": "Top Gun Maverick 2022 1080p BluRay",
    "john-wick-chapter-4": "John Wick Chapter 4 2023 1080p BluRay",
    "x-men-first-class": "X-Men First Class 2011 1080p BluRay",
    "glass-onion-a-knives-out-mystery": "Glass Onion A Knives Out Mystery 2022"
}

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

for slug, query in targets.items():
    dest = os.path.join(sub_dir, f"{slug}.vtt")
    print(f"\n========================================================")
    print(f"[SEARCHING] {slug} -> '{query}'")
    print(f"========================================================")
    
    try:
        search_url = f"https://www.subtitlecat.com/index.php?search={urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers=headers)
        search_html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        
        detail_links = re.findall(r'href=[\'"](subs/\d+/[^\'"]+\.html)[\'"]', search_html)
        print(f"  Found {len(detail_links)} release listings.")
        
        saved = False
        for rel_link in detail_links[:5]:
            detail_url = f"https://www.subtitlecat.com/{rel_link}"
            try:
                det_req = urllib.request.Request(detail_url, headers=headers)
                det_html = urllib.request.urlopen(det_req, timeout=15).read().decode('utf-8', errors='ignore')
                
                # Look for indonesian page (-id.html) or direct file (-id.srt)
                id_pages = re.findall(r'href=[\'"](/subs/\d+/[^\'"]*-id\.html)[\'"]', det_html)
                if not id_pages:
                    id_pages = re.findall(r'href=[\'"](/download/\d+/[^\'"]*-id\.srt)[\'"]', det_html)
                
                for id_p in id_pages:
                    target_url = f"https://www.subtitlecat.com{id_p}"
                    print(f"  Visiting language target: {target_url}")
                    
                    if target_url.endswith('.html'):
                        lang_req = urllib.request.Request(target_url, headers=headers)
                        lang_html = urllib.request.urlopen(lang_req, timeout=15).read().decode('utf-8', errors='ignore')
                        # Find download srt link
                        dl_links = re.findall(r'href=[\'"](/subs/\d+/[^\'"]*\.srt|/download/[^\'"]*\.srt)[\'"]', lang_html)
                        if dl_links:
                            raw_file_url = f"https://www.subtitlecat.com{dl_links[0]}"
                        else:
                            # Direct download link fallback
                            raw_file_url = target_url.replace('.html', '.srt')
                    else:
                        raw_file_url = target_url
                    
                    print(f"  Downloading raw subtitle from: {raw_file_url}")
                    file_req = urllib.request.Request(raw_file_url, headers=headers)
                    raw_content = urllib.request.urlopen(file_req, timeout=20).read().decode('utf-8', errors='ignore')
                    
                    clean_vtt, count = sanitize_srt_to_vtt(raw_content)
                    if count > 300:
                        with open(dest, 'wb') as f:
                            f.write(clean_vtt.encode('utf-8'))
                        print(f"  [✓] SUCCESS: {slug}.vtt saved with {count} synchronized cues ({len(clean_vtt)} bytes)!")
                        saved = True
                        break
                
                if saved:
                    break
            except Exception as e_detail:
                print(f"  Error on release: {e_detail}")
        
        if not saved:
            print(f"  [WARN] Failed to fetch full sub for {slug}")
    except Exception as e_search:
        print(f"  Search error: {e_search}")
