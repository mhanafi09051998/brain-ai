#!/usr/bin/env python3
import os
import re

ROOT = "/home/ubuntu/media_storage/movies"
created_links = 0

SUBFOLDER_SUFFIXES = [
    "[1080p]",
    "[720p]",
    "[1080p] [BluRay] [5.1] [YTS.MX]",
    "[720p] [BluRay] [YTS.MX]",
    "[1080p] [WEBRip] [5.1] [YTS.MX]",
    "[720p] [WEBRip] [YTS.MX]",
    "[1080p] [BluRay] [5.1] [YTS.GG - YTS.BZ]",
    "[720p] [BluRay] [YTS.GG - YTS.BZ]",
    "[1080p] [WEBRip] [5.1] [YTS.GG - YTS.BZ]",
    "[720p] [WEBRip] [YTS.GG - YTS.BZ]",
    "[1080p] [BluRay] [5.1] [YTS.BZ]",
    "[720p] [BluRay] [YTS.BZ]",
    "[1080p] [WEBRip] [5.1] [YTS.BZ]",
    "[720p] [WEBRip] [YTS.BZ]",
    "[1080p] [BluRay] [YTS.LT]",
    "[720p] [BluRay] [YTS.LT]",
    "[1080p] [YTS.AG]",
    "[720p] [YTS.AG]",
]

for genre in os.listdir(ROOT):
    genre_path = os.path.join(ROOT, genre)
    if not os.path.isdir(genre_path) or genre.startswith("."):
        continue
    for movie in os.listdir(genre_path):
        movie_path = os.path.join(genre_path, movie)
        if not os.path.isdir(movie_path):
            continue
        
        # Clean folder name (e.g. "Terminator 3 - Rise of the Machines (2003)" -> variations)
        base_name = movie
        alt_name = movie.replace(" - ", " ")
        
        candidates = [base_name, alt_name]
        
        # Also check existing mp4/mkv files to infer original download folder names
        for f in os.listdir(movie_path):
            if f.endswith((".mp4", ".mkv")) and not os.path.islink(os.path.join(movie_path, f)):
                # extract stem
                stem = os.path.splitext(f)[0]
                # replace dots with spaces
                spaced = stem.replace(".", " ")
                candidates.append(spaced)
                
        for cand in set(candidates):
            for suffix in SUBFOLDER_SUFFIXES:
                dir_alias = f"{cand} {suffix}"
                target_alias_path = os.path.join(movie_path, dir_alias)
                if not os.path.exists(target_alias_path):
                    try:
                        os.symlink(".", target_alias_path)
                        created_links += 1
                    except: pass

print(f"Total directory compatibility aliases created: {created_links}")
