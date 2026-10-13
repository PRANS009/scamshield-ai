#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo 'Install Python 3.12, then run bash start.sh again.'; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required; 3.12 recommended"'
if [ ! -f .env ]; then cp .env.example .env; echo 'Created .env. Add your SerpApi key there for live research; restart after editing.'; fi
if [ ! -d backend/.venv ]; then python3 -m venv backend/.venv; fi
if [ ! -f backend/.venv/.deps-ready ]; then
  backend/.venv/bin/python -m pip install -r backend/requirements-lock.txt
  touch backend/.venv/.deps-ready
fi
if [ ! -f frontend/dist/index.html ]; then
  command -v npm >/dev/null || { echo 'Install Node.js 20+ to build the frontend.'; exit 1; }
  (cd frontend && npm ci && npm run build)
fi
printf '\nOpen http://127.0.0.1:8000 in your browser. Stop with Ctrl+C.\n\n'
cd backend
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
