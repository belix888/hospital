$ErrorActionPreference = "Stop"

Write-Host "[+] Starting Hospital Web (local)..."
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python not found in PATH. Install Python 3.10+ and retry."
}

if (-not (Test-Path ".venv")) {
  Write-Host "[i] Creating venv in web/.venv"
  python -m venv .venv
}

& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\pip install -r requirements.txt

if (-not (Test-Path ".env")) {
  Write-Host "[i] Creating .env from .env.example"
  Copy-Item ".env.example" ".env"
}

Write-Host "[i] Running migrations..."
& .\.venv\Scripts\python hospital_web\manage.py migrate

Write-Host "[i] Starting dev server at http://127.0.0.1:8000/"
& .\.venv\Scripts\python hospital_web\manage.py runserver

