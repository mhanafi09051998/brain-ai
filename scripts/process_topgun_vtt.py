import re, os

srt_path = "D:/Agent_Claudia_Autonomus/goblix/public/subtitles/top-gun-maverick.srt"
vtt_path = "D:/Agent_Claudia_Autonomus/goblix/public/subtitles/top-gun-maverick.vtt"

with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
    srt_text = f.read()

# Replace comma milliseconds with dot milliseconds
vtt_text = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', srt_text)

FORBIDDEN_WORDS = [
    r'\bslot\b', r'\bjudi\b', r'\bgacor\b', r'\bpoker\b', r'\bdeposit\b',
    r'\bbonus\b', r'\b1xbet\b', r'\bsbobet\b', r'\bmaxwin\b', r'\bpragmatic\b',
    r'\bzeus\b', r'link alternatif', r'\bpromo\b', r'\bagen\b', r'official website',
    r't\.me/', r'bit\.ly/'
]

lines = vtt_text.splitlines()
clean_lines = []

for line in lines:
    is_spam = False
    for pat in FORBIDDEN_WORDS:
        if re.search(pat, line, re.IGNORECASE):
            is_spam = True
            break
    if is_spam:
        clean_lines.append("")
    else:
        clean_lines.append(line)

cleaned_vtt = "\n".join(clean_lines)

# Inject opening banner
header = """WEBVTT - Goblix Subtitle Track

1
00:00:02.000 --> 00:00:07.000
GOBLIX NONTON FILM LUAR NEGERI GRATIS

"""

final_vtt = header + cleaned_vtt

with open(vtt_path, "w", encoding="utf-8") as f:
    f.write(final_vtt)

print(f"Successfully converted and sanitized Top Gun VTT ({len(final_vtt)} bytes).")
