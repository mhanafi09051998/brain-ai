const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKSPACE_DIR = path.resolve(__dirname, '..');
let syncTimeout = null;
let isSyncing = false;

console.log(`🚀 [AutoGitSync] Silent Event-Driven Daemon active (windowsHide: true). Watching: ${WORKSPACE_DIR}`);

function runCommandSilent(cmd) {
  try {
    return execSync(cmd, {
      cwd: WORKSPACE_DIR,
      stdio: 'pipe',
      encoding: 'utf8',
      windowsHide: true // CRITICAL: Prevents any black console window from flashing on Windows screen
    }).trim();
  } catch (err) {
    return null;
  }
}

function doSync() {
  if (isSyncing) return;
  isSyncing = true;

  try {
    const status = runCommandSilent('git status --porcelain');
    
    if (status && status.length > 0) {
      console.log(`📦 [AutoGitSync] Changes detected:\n${status}`);
      
      runCommandSilent('git add -A');
      
      const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
      const commitMsg = `auto(sync): update workspace intelligence [${timestamp}]`;
      
      const commitRes = runCommandSilent(`git commit -m "${commitMsg}"`);
      if (commitRes) {
        console.log(`✅ [AutoGitSync] Committed: ${commitMsg}`);
      }

      const pushRes = runCommandSilent('git push origin main');
      if (pushRes !== null) {
        console.log(`🌐 [AutoGitSync] Successfully pushed to origin main.`);
      }
    }
  } catch (err) {
    console.error('Sync error:', err.message);
  } finally {
    isSyncing = false;
  }
}

function triggerDebouncedSync() {
  if (syncTimeout) clearTimeout(syncTimeout);
  syncTimeout = setTimeout(doSync, 3000); // 3-second debounce after file edits
}

// Initial sync on startup
doSync();

// Event-driven watcher on workspace files (ignores node_modules and .git)
try {
  fs.watch(WORKSPACE_DIR, { recursive: true }, (eventType, filename) => {
    if (!filename) return;
    if (filename.includes('.git') || filename.includes('node_modules') || filename.includes('.pm2')) return;
    triggerDebouncedSync();
  });
} catch (e) {
  // Fallback to safe 60s timer if recursive watch not supported
  setInterval(doSync, 60000);
}
