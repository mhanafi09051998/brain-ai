#!/usr/bin/env python3
import os

ROOT = "/home/ubuntu/media_storage/movies"
linked_count = 0

for genre in os.listdir(ROOT):
    genre_path = os.path.join(ROOT, genre)
    if not os.path.isdir(genre_path) or genre.startswith("."):
        continue
    for movie in os.listdir(genre_path):
        movie_path = os.path.join(genre_path, movie)
        if not os.path.isdir(movie_path):
            continue
        
        videos = []
        for f in os.listdir(movie_path):
            full_f = os.path.join(movie_path, f)
            if f.lower().endswith((".mp4", ".mkv", ".avi", ".webm")) and not os.path.islink(full_f):
                videos.append(f)
                
        if not videos:
            continue
            
        primary_vid = max(videos, key=lambda v: os.path.getsize(os.path.join(movie_path, v)))
        ext = os.path.splitext(primary_vid)[1]
        
        # 1. Standard movie name: "{movie_folder_name}.mp4"
        std_name = f"{movie}{ext}"
        std_path = os.path.join(movie_path, std_name)
        if not os.path.exists(std_path) and std_name != primary_vid:
            try:
                os.symlink(primary_vid, std_path)
                linked_count += 1
            except: pass
            
        # 2. Check for old 720p or YTS name patterns that might be cached
        for f in os.listdir(movie_path):
            if ("720p" in f or "BluRay" in f or "WEBRip" in f) and (f.endswith(".srt") or f.endswith(".id.srt")):
                target_vid = f.replace(".id.srt", ext).replace(".srt", ext)
                target_path = os.path.join(movie_path, target_vid)
                if not os.path.exists(target_path) and target_vid != primary_vid:
                    try:
                        os.symlink(primary_vid, target_path)
                        linked_count += 1
                    except: pass

print(f"Successfully created {linked_count} backward-compatibility symlinks.")
