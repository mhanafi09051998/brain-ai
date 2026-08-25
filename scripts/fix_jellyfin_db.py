#!/usr/bin/env python3
"""
Fix Jellyfin database: find all movie/video entries with stale paths
and update them to point to the actual file that exists on disk.
"""
import sqlite3
import os
import glob

DB_PATH = "/home/ubuntu/jellyfin/config/data/jellyfin.db"
MEDIA_ROOT_CONTAINER = "/media"
MEDIA_ROOT_HOST = "/home/ubuntu/media_storage"

def host_path(container_path):
    return container_path.replace(MEDIA_ROOT_CONTAINER, MEDIA_ROOT_HOST, 1)

def find_real_video(folder):
    """Find the largest real (non-symlink) video file in folder."""
    videos = []
    if not os.path.isdir(folder):
        return None
    for f in os.listdir(folder):
        fp = os.path.join(folder, f)
        if f.lower().endswith((".mp4", ".mkv", ".avi")) and not os.path.islink(fp):
            videos.append(fp)
    if not videos:
        return None
    return max(videos, key=os.path.getsize)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get all BaseItems that are Videos/Movies with a path
cur.execute("""
    SELECT Id, Path FROM BaseItems
    WHERE Path IS NOT NULL AND Path LIKE '/media/movies/%'
    ORDER BY Path;
""")
rows = cur.fetchall()
print(f"Found {len(rows)} movie entries in DB.")

stale = 0
fixed = 0
missing = []

for item_id, container_path in rows:
    host_file = host_path(container_path)
    
    # Check if path is valid (either real file or working symlink)
    if os.path.exists(host_file):
        continue
        
    stale += 1
    # File doesn't exist — find what's actually in that folder
    folder = os.path.dirname(host_file)
    
    # Walk up if folder is also missing (nested subfolder case)
    if not os.path.isdir(folder):
        folder = os.path.dirname(folder)
    
    real_video = find_real_video(folder)
    
    if real_video:
        new_container_path = real_video.replace(MEDIA_ROOT_HOST, MEDIA_ROOT_CONTAINER, 1)
        cur.execute("UPDATE BaseItems SET Path = ? WHERE Id = ?", (new_container_path, item_id))
        fixed += 1
        print(f"  [FIX] {os.path.basename(container_path)}")
        print(f"        -> {os.path.basename(real_video)}")
    else:
        missing.append(container_path)
        print(f"  [MISSING] {container_path}")

conn.commit()
conn.close()

print(f"\n=============================")
print(f"Stale paths found : {stale}")
print(f"Auto-fixed        : {fixed}")
print(f"Still missing     : {len(missing)}")
print(f"=============================")
if missing:
    print("\nFilm tanpa file (perlu download ulang):")
    for m in missing:
        parts = m.split("/")
        print(f"  - {parts[-2] if len(parts) >= 2 else m}")
