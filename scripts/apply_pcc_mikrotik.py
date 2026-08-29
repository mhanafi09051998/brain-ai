#!/usr/bin/env python3
"""
Apply Production-Grade PCC 2-WAN Load Balancing on MikroTik RouterOS v7
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
    # 1. Routing Tables
    "/routing table add name=to-ISP1 fib",
    "/routing table add name=to-ISP2 fib",

    # 2. NAT Masquerade for both WANs
    "/ip firewall nat add chain=srcnat action=masquerade out-interface=ether2-isp2 comment=\"NAT Masquerade ISP2\"",

    # 3. DNS Drop from WAN2 (Security)
    "/ip firewall filter add chain=input action=drop protocol=udp in-interface=ether2-isp2 dst-port=53 comment=\"drop DNS from WAN2\"",
    "/ip firewall filter add chain=input action=drop protocol=tcp in-interface=ether2-isp2 dst-port=53 comment=\"drop DNS from WAN2\"",

    # 4. Local Address Lists
    "/ip firewall address-list add list=LOCAL-SUBNETS address=192.168.0.0/16 comment=\"Local LAN Subnets\"",
    "/ip firewall address-list add list=LOCAL-SUBNETS address=10.0.0.0/8 comment=\"Private Networks\"",
    "/ip firewall address-list add list=LOCAL-SUBNETS address=172.16.0.0/12 comment=\"Private Networks\"",

    # 5. Mangle Rules (Accept local first)
    "/ip firewall mangle add chain=prerouting dst-address-list=LOCAL-SUBNETS action=accept comment=\"PCC: Bypass Local Subnets\"",

    # 6. Incoming WAN Symmetry
    "/ip firewall mangle add chain=input in-interface=ether1-isp1 connection-state=new action=mark-connection new-connection-mark=ISP1_conn passthrough=yes comment=\"PCC: Inbound ISP1\"",
    "/ip firewall mangle add chain=input in-interface=ether2-isp2 connection-state=new action=mark-connection new-connection-mark=ISP2_conn passthrough=yes comment=\"PCC: Inbound ISP2\"",
    "/ip firewall mangle add chain=output connection-mark=ISP1_conn action=mark-routing new-routing-mark=to-ISP1 passthrough=no comment=\"PCC: Outbound router ISP1\"",
    "/ip firewall mangle add chain=output connection-mark=ISP2_conn action=mark-routing new-routing-mark=to-ISP2 passthrough=no comment=\"PCC: Outbound router ISP2\"",

    # 7. Inbound Forward Symmetry
    "/ip firewall mangle add chain=forward in-interface=ether1-isp1 connection-state=new action=mark-connection new-connection-mark=ISP1_conn passthrough=yes comment=\"PCC: Forward Inbound ISP1\"",
    "/ip firewall mangle add chain=forward in-interface=ether2-isp2 connection-state=new action=mark-connection new-connection-mark=ISP2_conn passthrough=yes comment=\"PCC: Forward Inbound ISP2\"",

    # 8. PCC Classifier (both-addresses-and-ports 2/0 and 2/1)
    "/ip firewall mangle add chain=prerouting in-interface=bridge1 connection-mark=no-mark dst-address-type=!local dst-address-list=!LOCAL-SUBNETS per-connection-classifier=both-addresses-and-ports:2/0 action=mark-connection new-connection-mark=ISP1_conn passthrough=yes comment=\"PCC: Split 2/0 ISP1\"",
    "/ip firewall mangle add chain=prerouting in-interface=bridge1 connection-mark=no-mark dst-address-type=!local dst-address-list=!LOCAL-SUBNETS per-connection-classifier=both-addresses-and-ports:2/1 action=mark-connection new-connection-mark=ISP2_conn passthrough=yes comment=\"PCC: Split 2/1 ISP2\"",

    # 9. Mark Routing for LAN traffic
    "/ip firewall mangle add chain=prerouting in-interface=bridge1 connection-mark=ISP1_conn action=mark-routing new-routing-mark=to-ISP1 passthrough=no comment=\"PCC: Apply to-ISP1 routing mark\"",
    "/ip firewall mangle add chain=prerouting in-interface=bridge1 connection-mark=ISP2_conn action=mark-routing new-routing-mark=to-ISP2 passthrough=no comment=\"PCC: Apply to-ISP2 routing mark\"",

    # 10. Update DHCP Clients default route distances (or set add-default-route=no to use static ping-checked routes)
    "/ip dhcp-client set [find interface=ether1-isp1] default-route-distance=1",
    "/ip dhcp-client set [find interface=ether2-isp2] default-route-distance=2",

    # 11. Static Routes for Dedicated Routing Tables with check-gateway=ping
    "/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.1 routing-table=to-ISP1 check-gateway=ping distance=1 comment=\"PCC Route Table to-ISP1\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=192.168.100.1 routing-table=to-ISP1 check-gateway=ping distance=2 comment=\"PCC Backup Table to-ISP1\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=192.168.100.1 routing-table=to-ISP2 check-gateway=ping distance=1 comment=\"PCC Route Table to-ISP2\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.1 routing-table=to-ISP2 check-gateway=ping distance=2 comment=\"PCC Backup Table to-ISP2\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.1 routing-table=main check-gateway=ping distance=1 comment=\"Main Route ISP1\"",
    "/ip route add dst-address=0.0.0.0/0 gateway=192.168.100.1 routing-table=main check-gateway=ping distance=2 comment=\"Main Route ISP2\""
]

def apply_pcc():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[*] Menghubungkan ke MikroTik {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10, look_for_keys=False, allow_agent=False)
        print("[✓] Terhubung! Mengaplikasikan konfigurasi PCC Multi-WAN...")
        
        for cmd in commands_to_apply:
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', errors='ignore').strip()
            err = stderr.read().decode('utf-8', errors='ignore').strip()
            if err:
                print(f"  [!] CMD: {cmd}\n      WARN/ERR: {err}")
            else:
                print(f"  [✓] {cmd}")
                
        client.close()
        print("\n[SUCCESS] Konfigurasi PCC Multi-WAN berhasil diaplikasikan!")
    except Exception as e:
        print(f"[!] Gagal mengeksekusi: {e}")

if __name__ == "__main__":
    apply_pcc()
