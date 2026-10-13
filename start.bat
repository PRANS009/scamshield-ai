@echo off
cd /d "%~dp0"
if not exist .env copy .env.example .env
if not exist backend\.venv (
  py -3 -m venv backend\.venv
  if errorlevel 1 exit /b 1
)
if not exist backend\.venv\.deps-ready (
  backend\.venv\Scripts\python -m pip install -r backend\requirements-lock.txt
  if errorlevel 1 exit /b 1
  type nul > backend\.venv\.deps-ready
)
if not exist frontend\dist\index.html (
  cd frontend
  call npm ci
  if errorlevel 1 exit /b 1
  call npm run build
  if errorlevel 1 exit /b 1
  cd ..
)
echo Open http://127.0.0.1:8000 in your browser.
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
