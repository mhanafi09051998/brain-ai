import os, re, glob, urllib.request, json

SUBTITLE_DIR = '/home/ubuntu/apps/zolu-movie/public/subtitles'
STREAM_DIR = '/home/ubuntu/apps/zolu-movie/public/stream'

# 50+ Exhaustive Anti-Judol, Anti-Slot, Anti-Promo Filters
FORBIDDEN_KEYWORDS = [
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

compiled_filters = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_KEYWORDS]

def sanitize_and_resync_vtt(file_path):
    print(f"\n[PROCESSING] {file_path}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines()
    clean_lines = []
    
    cue_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}[\.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[\.,]\d{3})')
    
    i = 0
    removed_spam = 0
    valid_cues = []
    
    current_cue = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line is timing cue
        match = cue_pattern.search(line)
        if match:
            start_t, end_t = match.group(1).replace(',', '.'), match.group(2).replace(',', '.')
            cue_text_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '':
                cue_text_lines.append(lines[i].strip())
                i += 1
            
            cue_text = '\n'.join(cue_text_lines)
            
            # Check for spam in cue text
            is_spam = any(filt.search(cue_text) for filt in compiled_filters)
            
            # Also filter if cue text contains website links or telegram
            if re.search(r'(https?://|\.com|\.net|\.org|\.id|\.xyz|\.vip|t\.me)', cue_text, re.IGNORECASE):
                is_spam = True

            if is_spam:
                removed_spam += 1
            else:
                valid_cues.append({
                    'start': start_t,
                    'end': end_t,
                    'text': cue_text
                })
        else:
            i += 1

    # Reconstruct clean WebVTT
    out_lines = [
        "WEBVTT - Goblix Cinema Subtitle Track",
        "",
        "1",
        "00:00:02.000 --> 00:00:07.000",
        "GOBLIX NONTON FILM LUAR NEGERI GRATIS",
        ""
    ]

    for idx, cue in enumerate(valid_cues, start=2):
        out_lines.append(str(idx))
        out_lines.append(f"{cue['start']} --> {cue['end']}")
        out_lines.append(cue['text'])
        out_lines.append("")

    new_content = '\n'.join(out_lines)
    with open(file_path, 'wb') as f:
        f.write(new_content.encode('utf-8'))

    print(f"  [✓] Sanitized {os.path.basename(file_path)}: {len(valid_cues)} valid cues preserved, {removed_spam} spam cues removed.")

def run():
    vtt_files = glob.glob(f"{SUBTITLE_DIR}/*.vtt") + glob.glob('/home/ubuntu/apps/zolu-movie/public/*.vtt')
    for vtt in set(vtt_files):
        sanitize_and_resync_vtt(vtt)

if __name__ == '__main__':
    run()
