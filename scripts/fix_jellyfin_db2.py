#!/usr/bin/env python3
"""
Fix stale DB entries where path is /media/movies/<title> (missing genre subfolder).
Find the actual file under /home/ubuntu/media_storage/movies/<any_genre>/<title>/
and update DB path accordingly.
"""
import sqlite3
import os

DB_PATH = "/home/ubuntu/jellyfin/config/data/jellyfin.db"
MEDIA_ROOT_CONTAINER = "/media"
MEDIA_ROOT_HOST = "/home/ubuntu/media_storage"

def find_real_video(folder):
    if not os.path.isdir(folder):
        return None
    videos = []
    for f in os.listdir(folder):
        fp = os.path.join(folder, f)
        if f.lower().endswith((".mp4", ".mkv", ".avi")) and not os.path.islink(fp):
            videos.append(fp)
    return max(videos, key=os.path.getsize) if videos else None

def host_path(p):
    return p.replace(MEDIA_ROOT_CONTAINER, MEDIA_ROOT_HOST, 1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT Id, Path FROM BaseItems WHERE Path IS NOT NULL AND Path LIKE '/media/movies/%';")
rows = cur.fetchall()

fixed = 0
still_missing = []

for item_id, container_path in rows:
    host_file = host_path(container_path)
    if os.path.exists(host_file):
        continue  # already valid
    
    # Extract the movie title from path
    parts = container_path.split("/")
    # /media/movies/[genre?]/[title]/file.mp4  OR /media/movies/[title]/file.mp4
    # Find any genre folder that has this title
    movie_root = os.path.join(MEDIA_ROOT_HOST, "movies")
    title_fragment = None
    
    # Get what we expect: last meaningful folder name or filename
    filename = parts[-1]  # could be a folder name or filename
    
    # Search across all genres
    found_path = None
    for genre in os.listdir(movie_root):
        genre_path = os.path.join(movie_root, genre)
        if not os.path.isdir(genre_path):
            continue
        for movie_dir in os.listdir(genre_path):
            movie_path = os.path.join(genre_path, movie_dir)
            if not os.path.isdir(movie_path):
                continue
            # Check if filename exists directly here
            candidate = os.path.join(movie_path, filename)
            if os.path.exists(candidate):
                found_path = candidate
                break
            # Check if movie_dir matches fragment from path (fuzzy)
            if len(parts) >= 3:
                # match on movie folder name
                path_movie_dir = parts[2] if len(parts) <= 3 else parts[3] if len(parts) == 4 else parts[2]
                if movie_dir.lower() == path_movie_dir.lower():
                    real_video = find_real_video(movie_path)
                    if real_video:
                        found_path = real_video
                        break
        if found_path:
            break
    
    if found_path:
        new_container_path = found_path.replace(MEDIA_ROOT_HOST, MEDIA_ROOT_CONTAINER, 1)
        cur.execute("UPDATE BaseItems SET Path = ? WHERE Id = ?", (new_container_path, item_id))
        fixed += 1
        print(f"  [FIX] {os.path.basename(container_path)}")
        print(f"        -> {new_container_path}")
    else:
        still_missing.append(container_path)

conn.commit()
conn.close()

print(f"\n=== PHASE 2 DB FIX ===")
print(f"Fixed in this pass : {fixed}")
print(f"Still unresolved   : {len(still_missing)}")
for m in still_missing:
    print(f"  [MISSING] {m}")
