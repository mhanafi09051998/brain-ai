#!/usr/bin/env python3
import subprocess, os, sys, datetime, json

# Force UTF-8 encoding for standard output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = r"D:\Agent_Claudia_Autonomus"
os.chdir(WORKSPACE)

def run_cmd(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def auto_sync():
    print(f"[*] Checking for new learnings in {WORKSPACE}...")
    
    # 1. Update Graphify AST
    subprocess.run("python -m graphify update .", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Check git status
    run_cmd("git add .")
    status_out, _, _ = run_cmd("git status --porcelain")
    
    if not status_out:
        print("[OK] Repository is already up to date. No new changes.")
        return
        
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"learn: auto-sync neural memory and knowledge network ({now})"
    
    run_cmd(f'git commit -m "{commit_msg}"')
    print(f"[COMMIT] {commit_msg}")
    
    # 3. Push to GitHub via VPS Tunnel
    temp_bundle = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "claudia_repo.bundle")
    run_cmd(f'git bundle create "{temp_bundle}" --all')
    
    pscp_cmd = f'& "C:\\Program Files\\PuTTY\\pscp.exe" -i "$env:USERPROFILE\\.ssh\\vps_ubuntu.ppk" "{temp_bundle}" ubuntu@169.58.92.168:/home/ubuntu/claudia_repo.bundle'
    subprocess.run(["powershell", "-Command", pscp_cmd], capture_output=True)
    
    vps_push_cmd = 'ssh vps-ubuntu "cd /home/ubuntu/Agent_Claudia_Autonomus && git pull /home/ubuntu/claudia_repo.bundle main && git push origin main && rm -f /home/ubuntu/claudia_repo.bundle"'
    res_out, res_err, code = run_cmd(vps_push_cmd)
    
    if code == 0:
        print("[SUCCESS] Successfully synced & pushed new learnings to GitHub repository!")
    else:
        print("[NOTICE] Push output:", res_out, res_err)

if __name__ == "__main__":
    auto_sync()
