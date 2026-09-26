Write-Host "ProofSec Evaluation Platform Installer" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$pythonCmd = "python"
try {
    $out = Invoke-Expression "$pythonCmd --version" 2>$null
    if (-not $?) {
        Write-Error "Python is required but not found."
        exit 1
    }
} catch {
    Write-Error "Python is required but not found."
    exit 1
}

$venvDir = Join-Path $HOME ".proofsec-env"

Write-Host "1. Creating Python virtual environment in $venvDir..."
Invoke-Expression "$pythonCmd -m venv $venvDir"

Write-Host "2. Installing ProofSec..."
$pipCmd = Join-Path $venvDir "Scripts\pip.exe"
Invoke-Expression "$pipCmd install --upgrade pip"
Invoke-Expression "$pipCmd install git+https://github.com/proofsec/proofsec.git"

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Please add $($venvDir)\Scripts to your PATH to run proofsec." -ForegroundColor Yellow
