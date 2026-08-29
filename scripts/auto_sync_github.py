#!/usr/bin/env python3
import subprocess, os, sys, datetime, tempfile

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    
    # 3. Direct Git Push to GitHub
    push_out, push_err, push_code = run_cmd("git push origin main")
    if push_code == 0:
        print("[SUKSES] Berhasil push langsung ke GitHub repository main!")
    else:
        print(f"[INFO] Direct push status: {push_out} {push_err}")
    
    # 4. Optional Push to VPS via Tunnel if configured
    temp_bundle = os.path.join(tempfile.gettempdir(), "claudia_repo.bundle")
    if os.path.exists(temp_bundle):
        try: os.remove(temp_bundle)
        except: pass

    run_cmd(f'git bundle create "{temp_bundle}" --all')
    
    try:
        scp_res = subprocess.run(["scp", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", temp_bundle, "vps_claudia:/home/ubuntu/claudia_repo.bundle"], capture_output=True, text=True, timeout=10)
        if scp_res.returncode == 0:
            vps_sync_cmd = '(cd /home/ubuntu/claudia-ultra 2>/dev/null || cd /home/ubuntu/Agent_Claudia_Autonomus) && git pull /home/ubuntu/claudia_repo.bundle main --no-edit && git push origin main && rm -f /home/ubuntu/claudia_repo.bundle'
            res = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "vps_claudia", vps_sync_cmd], capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                print("[SUKSES] Berhasil sinkronisasi dan push ke VPS!")
    except Exception as e:
        pass

if __name__ == "__main__":
    auto_sync()