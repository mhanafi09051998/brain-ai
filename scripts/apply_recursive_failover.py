#!/usr/bin/env python3
"""
Deploy Recursive Failover with PCC Multi-WAN on MikroTik RouterOS v7
"""

import sys
import paramiko

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HOST = "192.168.2.1"
PORT = 22
USER = "herbacore"
PASSWORD = "herbacore456"

commands_to_apply = [
    # 1. Disable DHCP client default route creation to avoid conflicts with recursive routes
    "/ip dhcp-client set [find interface=ether1-isp1] add-default-route=no",
    "/ip dhcp-client set [find interface=ether2-isp2] add-default-route=no",

    # 2. Remove previous static routes (clean state)
    "/ip route remove [find comment~\"Main Route|PCC Route|PCC Backup|Host Check|Recursive\"]",

    # 3. Host Check Routes (Direct gateway ping to Internet public targets)
    "/ip route add dst-address=1.1.1.1/32 gateway=192.168.1.1 scope=10 check-gateway=ping comment=\"Host Check ISP1 Cloudflare\"",
    "/ip route add dst-address=1.0.0.1/32 gateway=192.168.100.1 scope=10 check-gateway=ping comment=\"Host Check ISP2 Cloudflare\"",

    # 4. Table to-ISP1 (Recursive routes)
    "/ip route add dst-address=0.0.0.0/0 gateway=1.1.1.1 routing-table=to-ISP1 distance=1 target-scope=30 comment=\"Recursive Table to-ISP1 (Primary)\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=1.0.0.1 routing-table=to-ISP1 distance=2 target-scope=30 comment=\"Recursive Table to-ISP1 (Backup to ISP2)\"",

    # 5. Table to-ISP2 (Recursive routes)
    "/ip route add dst-address=0.0.0.0/0 gateway=1.0.0.1 routing-table=to-ISP2 distance=1 target-scope=30 comment=\"Recursive Table to-ISP2 (Primary)\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=1.1.1.1 routing-table=to-ISP2 distance=2 target-scope=30 comment=\"Recursive Table to-ISP2 (Backup to ISP1)\"",

    # 6. Table main (Recursive default routes for router and unclassified traffic)
    "/ip route add dst-address=0.0.0.0/0 gateway=1.1.1.1 routing-table=main distance=1 target-scope=30 comment=\"Recursive Default ISP1 (Main)\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=1.0.0.1 routing-table=main distance=2 target-scope=30 comment=\"Recursive Default ISP2 (Main)\""
]

def apply_recursive_failover():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[*] Menghubungkan ke MikroTik {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10, look_for_keys=False, allow_agent=False)
        print("[✓] Terhubung! Mengaplikasikan Recursive Failover untuk PCC...")
        
        for cmd in commands_to_apply:
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', errors='ignore').strip()
            err = stderr.read().decode('utf-8', errors='ignore').strip()
            if err:
                print(f"  [!] CMD: {cmd}\n      WARN/ERR: {err}")
            else:
                print(f"  [✓] {cmd}")
                
        client.close()
        print("\n[SUCCESS] Recursive Failover + PCC berhasil diaplikasikan!")
    except Exception as e:
        print(f"[!] Gagal mengeksekusi: {e}")

if __name__ == "__main__":
    apply_recursive_failover()
