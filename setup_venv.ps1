$ErrorActionPreference = "Stop"

# Create venv if not exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
}

# Upgrade pip and install requirements
Write-Host "Upgrading pip..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip

if (Test-Path "requirements.txt") {
    Write-Host "Installing requirements..."
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

Write-Host "Venv ready. Activate with: .\\.venv\\Scripts\\Activate.ps1"
