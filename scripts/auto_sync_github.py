#!/usr/bin/env python3
import subprocess, os, sys, datetime, tempfile

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = r"D:\Agent_Claudia_Autonomus"
os.chdir(WORKSPACE)

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8", errors="ignore", timeout=60)
        return res.stdout.strip(), res.stderr.strip(), res.returncode
    except Exception as e:
        return "", str(e), 1

def auto_sync():
    print(f"[*] Memeriksa pembaruan pembelajaran di {WORKSPACE}...")
    
    # 0. Clean stale git locks if any
    lock_file = os.path.join(WORKSPACE, ".git", "index.lock")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except:
            pass

    # 1. Update Graphify AST
    subprocess.run("python -m graphify update .", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Check git status
    run_cmd("git add .")
    status_out, _, _ = run_cmd("git status --porcelain")
    
    if not status_out:
        print("[OK] Repositori sudah bersih dan up-to-date. Tidak ada perubahan baru.")
        return
        
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"belajar: sinkronisasi otomatis memori neuron dan pengetahuan ({now})"
    
    run_cmd(f'git commit -m "{commit_msg}"')
    print(f"[COMMIT] {commit_msg}")
    
    # 3. Push to GitHub via VPS Tunnel
    temp_bundle = os.path.join(tempfile.gettempdir(), "claudia_repo.bundle")
    if os.path.exists(temp_bundle):
        try: os.remove(temp_bundle)
        except: pass

    run_cmd(f'git bundle create "{temp_bundle}" --all')
    
    pscp_cmd = f'& "C:\\Program Files\\PuTTY\\pscp.exe" -i "$env:USERPROFILE\\.ssh\\vps_ubuntu.ppk" "{temp_bundle}" ubuntu@169.58.92.168:/home/ubuntu/claudia_repo.bundle'
    subprocess.run(["powershell", "-Command", pscp_cmd], capture_output=True, timeout=60)
    
    vps_push_cmd = 'ssh vps-ubuntu "cd /home/ubuntu/Agent_Claudia_Autonomus && (git pull /home/ubuntu/claudia_repo.bundle main || git reset --hard origin/main) && git push origin main && rm -f /home/ubuntu/claudia_repo.bundle"'
    res_out, res_err, code = run_cmd(vps_push_cmd)
    
    if code == 0:
        print("[SUKSES] Berhasil sinkronisasi dan push pembelajaran ke repositori GitHub!")
    else:
        print("[CATATAN] Output push:", res_out, res_err)

if __name__ == "__main__":
    auto_sync()