import urllib.request, urllib.parse, re, os

sub_dir = '/home/ubuntu/apps/zolu-movie/public/subtitles'
os.makedirs(sub_dir, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

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
    print(f"[SEARCHING] {slug} (query: {query})")
    print(f"========================================================")
    try:
        search_url = f"https://www.subtitlecat.com/index.php?search={urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers=headers)
        search_html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        
        # Find detail page links
        detail_links = re.findall(r'href=[\'"](subs/\d+/[^\'"]+\.html)[\'"]', search_html)
        if not detail_links:
            print(f"  [!] No detail links found for {query}")
            continue

        print(f"  Found {len(detail_links)} candidate releases. Checking top candidates...")
        
        saved = False
        for rel_link in detail_links[:4]:
            detail_url = f"https://www.subtitlecat.com/{rel_link}"
            try:
                det_req = urllib.request.Request(detail_url, headers=headers)
                det_html = urllib.request.urlopen(det_req, timeout=15).read().decode('utf-8', errors='ignore')
                
                # Find direct download link for Indonesian (-id.srt)
                dl_matches = re.findall(r'href=[\'"](/download/\d+/\d+/[^\'"]*-id\.srt)[\'"]', det_html)
                if not dl_matches:
                    dl_matches = re.findall(r'href=[\'"](/download/\d+/\d+/[^\'"]*)[\'"]', det_html)
                
                if dl_matches:
                    dl_url = f"https://www.subtitlecat.com{dl_matches[0]}"
                    print(f"  Downloading: {dl_url}")
                    dl_req = urllib.request.Request(dl_url, headers=headers)
                    raw_content = urllib.request.urlopen(dl_req, timeout=20).read().decode('utf-8', errors='ignore')
                    
                    clean_vtt, cue_count = sanitize_srt_to_vtt(raw_content)
                    if cue_count > 500:
                        with open(dest, 'wb') as f:
                            f.write(clean_vtt.encode('utf-8'))
                        print(f"  [✓] SUCCESS: Saved {slug}.vtt with {cue_count} synchronized cues ({len(clean_vtt)} bytes)!")
                        saved = True
                        break
                    else:
                        print(f"  [!] Cue count too low ({cue_count}), checking next candidate...")
            except Exception as sub_err:
                print(f"  Candidate error: {sub_err}")
        
        if not saved:
            print(f"  [WARN] Could not find >500 cue subtitle for {slug}")

    except Exception as e:
        print(f"  Search error for {slug}: {e}")
