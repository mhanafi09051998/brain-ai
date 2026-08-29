#!/usr/bin/env python3
"""
MikroTik RouterOS Interactive SSH Client for Claudia
"""

import sys
import paramiko
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HOST = "192.168.2.1"
PORT = 22
USER = "herbacore"
PASSWORD = "herbacore456"

def run_mikrotik_command(commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[*] Menghubungkan ke MikroTik {HOST}:{PORT} sebagai user '{USER}'...")
        client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10, look_for_keys=False, allow_agent=False)
        print("[✓] Terhubung ke MikroTik via SSH!")
        
        results = {}
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', errors='ignore')
            err = stderr.read().decode('utf-8', errors='ignore')
            results[cmd] = out if out else err
            
        client.close()
        return results
    except Exception as e:
        print(f"[!] Gagal terhubung ke MikroTik: {e}")
        return None

if __name__ == "__main__":
    commands = [
        "/system identity print",
        "/system resource print",
        "/system routerboard print",
        "/interface print",
        "/ip address print",
        "/ip route print",
        "/ip pool print",
        "/ip dhcp-server print",
        "/ip firewall nat print",
        "/ip firewall filter print",
        "/queue simple print",
        "/interface wireless print"
    ]
    
    res = run_mikrotik_command(commands)
    if res:
        for cmd, output in res.items():
            print(f"\n=== [ {cmd} ] ===")
            print(output.strip())
