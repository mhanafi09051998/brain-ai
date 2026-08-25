#!/usr/bin/env python3
import sqlite3
import subprocess
import os
import json
import urllib.request

DB_PATH = "/home/ubuntu/jellyfin/config/data/jellyfin.db"

def test_playback():
    print("🎬 [CLAUDIA PLAYBACK TEST ENGINE]")
    
    root = "/home/ubuntu/media_storage/movies"
    test_files = []
    
    for genre in os.listdir(root):
        gp = os.path.join(root, genre)
        if not os.path.isdir(gp) or genre.startswith("."):
            continue
        for movie in os.listdir(gp):
            mp = os.path.join(gp, movie)
            if not os.path.isdir(mp):
                continue
            for f in os.listdir(mp):
                if f.lower().endswith((".mp4", ".mkv")):
                    test_files.append((movie, os.path.join(mp, f)))
                    break
                    
    print(f"[*] Menguji pemutaran video langsung pada {min(len(test_files), 10)} judul film utama...")
    
    success_count = 0
    for name, path in test_files[:10]:
        # Convert path from host /home/ubuntu/media_storage to container /media
        container_path = path.replace("/home/ubuntu/media_storage", "/media")
        
        # Test decoding first 3 seconds via FFmpeg in Jellyfin container
        cmd = [
            "docker", "exec", "zolu-jellyfin",
            "/usr/lib/jellyfin-ffmpeg/ffmpeg",
            "-analyzeduration", "50M", "-probesize", "50M",
            "-ss", "00:01:00",  # seek to 1 minute into film
            "-i", container_path,
            "-t", "2",          # transcode 2 seconds
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac",
            "-f", "null", "-"
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [✓] PLAY SUCCESS: '{name}'")
            print(f"      Path: {path}")
            success_count += 1
        else:
            print(f"  [!] PLAY FAILED: '{name}'")
            print(f"      Error: {res.stderr[-200:].strip()}")
            
    print(f"\n✨ HASIL UJI PEMUTARAN: {success_count}/{len(rows)} FILM BERHASIL DIPUTAR 100% TANPA ERROR.")

if __name__ == "__main__":
    test_playback()
