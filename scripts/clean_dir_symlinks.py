#!/usr/bin/env python3
import os
ROOT = '/home/ubuntu/media_storage/movies'
cleaned = 0
VALID_EXTS = ('.mp4', '.mkv', '.srt', '.id.srt', '.en.srt', '.ass', '.vtt', '.nfo', '.jpg', '.png', '.txt')
for genre in os.listdir(ROOT):
    gp = os.path.join(ROOT, genre)
    if not os.path.isdir(gp) or genre.startswith('.'):
        continue
    for movie in os.listdir(gp):
        mp = os.path.join(gp, movie)
        if not os.path.isdir(mp):
            continue
        for item in os.listdir(mp):
            fp = os.path.join(mp, item)
            if os.path.islink(fp) and not any(item.endswith(e) for e in VALID_EXTS):
                os.unlink(fp)
                cleaned += 1
print(f'Cleaned {cleaned} stray directory symlinks across all movie folders.')
