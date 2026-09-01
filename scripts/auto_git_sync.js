const { execSync } = require('child_process');
const path = require('path');

const WORKSPACE_DIR = path.resolve(__dirname, '..');
const CHECK_INTERVAL_MS = 30000; // Check every 30 seconds

console.log(`🚀 [AutoGitSync] Daemon active. Watching workspace: ${WORKSPACE_DIR}`);

function runCommand(cmd) {
  try {
    return execSync(cmd, { cwd: WORKSPACE_DIR, stdio: 'pipe', encoding: 'utf8' }).trim();
  } catch (err) {
    return null;
  }
}

function syncWorkspace() {
  const status = runCommand('git status --porcelain');
  
  if (status && status.length > 0) {
    console.log(`📦 [AutoGitSync] Detected workspace changes:\n${status}`);
    
    // Stage all tracked/untracked changes matching .gitignore
    runCommand('git add -A');
    
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const commitMsg = `auto(sync): update workspace intelligence [${timestamp}]`;
    
    const commitRes = runCommand(`git commit -m "${commitMsg}"`);
    if (commitRes) {
      console.log(`✅ [AutoGitSync] Committed: ${commitMsg}`);
    }

    const pushRes = runCommand('git push origin main');
    if (pushRes !== null) {
      console.log(`🌐 [AutoGitSync] Successfully pushed to origin main.`);
    } else {
      console.warn(`⚠️ [AutoGitSync] Push failed or remote unreachable. Will retry next cycle.`);
    }
  }
}

// Initial sync
syncWorkspace();

// Periodic sync loop
setInterval(syncWorkspace, CHECK_INTERVAL_MS);
