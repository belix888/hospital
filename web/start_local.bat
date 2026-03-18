это @echo off
setlocal ENABLEDELAYEDEXPANSION

cd /d %~dp0
echo [+] Starting Hospital Web (local)...

where python >nul 2>nul
if errorlevel 1 (
  echo [-] Python not found in PATH. Install Python 3.10+ and retry.
  pause
  exit /b 1
)

if not exist ".venv" (
  echo [i] Creating venv in web\.venv
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [i] Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist ".env" (
  echo [i] Creating .env from .env.example
  copy .env.example .env >nul
)

echo [i] Running migrations...
python hospital_web\manage.py migrate

echo [i] Starting dev server at http://127.0.0.1:8000/
python hospital_web\manage.py runserver

endlocal

