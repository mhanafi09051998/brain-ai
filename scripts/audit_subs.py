#!/usr/bin/env python3
"""
Audit all movies in media_storage for Indonesian subtitle (.id.srt) presence.
Then invoke fetch-subs2.py for those missing.
"""
import os
import json
import subprocess
import sys

ROOT = "/home/ubuntu/media_storage/movies"
KEY = os.environ.get("OS_KEY", "")

missing_sub = []
has_sub = []

for genre in os.listdir(ROOT):
    gp = os.path.join(ROOT, genre)
    if not os.path.isdir(gp) or genre.startswith(".") or genre == "_salah":
        continue
    for movie in os.listdir(gp):
        mp = os.path.join(gp, movie)
        if not os.path.isdir(mp):
            continue
        # Find video file
        has_video = any(
            f.lower().endswith((".mp4", ".mkv")) and not os.path.islink(os.path.join(mp, f))
            for f in os.listdir(mp)
        )
        if not has_video:
            continue
        # Check for id sub
        has_id_sub = any(
            (f.lower().endswith(".id.srt") or ".indonesian." in f.lower() or ".ind." in f.lower())
            and not os.path.islink(os.path.join(mp, f))
            for f in os.listdir(mp)
        )
        if has_id_sub:
            has_sub.append(movie)
        else:
            missing_sub.append((movie, mp))

print(f"Total film dengan video: {len(has_sub) + len(missing_sub)}")
print(f"Sudah ada sub Indonesia: {len(has_sub)}")
print(f"Belum ada sub Indonesia: {len(missing_sub)}")
print()
if missing_sub:
    print("Film yang belum ada sub Indonesia:")
    for m, p in sorted(missing_sub):
        print(f"  - {m}")
