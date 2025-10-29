param(
    [Parameter(Mandatory=$false)]
    [string]$DataDir = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found. Run .\\setup_venv.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"
$env:PYTHONUNBUFFERED = "1"

if ($DataDir -and $DataDir.Trim().Length -gt 0) {
    python .\main.py $DataDir
} else {
    python .\main.py
}
