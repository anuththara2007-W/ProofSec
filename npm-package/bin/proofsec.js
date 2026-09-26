#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

function checkPython() {
  const pythonCmd = os.platform() === 'win32' ? 'python' : 'python3';
  const result = spawnSync(pythonCmd, ['--version'], { encoding: 'utf8' });
  if (result.error || result.status !== 0) {
    console.error(`Error: Python is required but not found. Please install Python 3.8 or higher.`);
    process.exit(1);
  }
  return pythonCmd;
}

function installAndRun() {
  const pythonCmd = checkPython();
  
  // We'll create an isolated environment in ~/.proofsec-env if it doesn't exist
  const envDir = path.join(os.homedir(), '.proofsec-env');
  const isWin = os.platform() === 'win32';
  const pipCmd = isWin ? path.join(envDir, 'Scripts', 'pip.exe') : path.join(envDir, 'bin', 'pip');
  const proofsecCmd = isWin ? path.join(envDir, 'Scripts', 'proofsec.exe') : path.join(envDir, 'bin', 'proofsec');
  
  if (!fs.existsSync(envDir)) {
    console.log('Initializing ProofSec Python environment for the first time...');
    spawnSync(pythonCmd, ['-m', 'venv', envDir], { stdio: 'inherit' });
    console.log('Installing proofsec...');
    // In a real environment, we would use pip install proofsec.
    // For this local dev package, we point pip to the repo root if possible, or just mock it.
    // Assuming the user runs this from source right now:
    const repoRoot = path.join(__dirname, '..', '..');
    spawnSync(pipCmd, ['install', '-e', repoRoot], { stdio: 'inherit' });
  }

  // Forward args
  const args = process.argv.slice(2);
  const result = spawnSync(proofsecCmd, args, { stdio: 'inherit' });
  
  if (result.error) {
    console.error(`Error executing proofsec: ${result.error.message}`);
    process.exit(1);
  }
  
  process.exit(result.status);
}

installAndRun();
