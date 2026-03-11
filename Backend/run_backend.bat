@echo off
setlocal

cd /d "%~dp0"

echo [1/2] Sync Python dependencies with uv...
uv sync
if errorlevel 1 (
  echo.
  echo uv sync failed. Please check errors above.
  pause
  exit /b 1
)

echo.
echo [2/2] Start backend service on http://127.0.0.1:5000 ...
set PYTHONPATH=.
uv run python -m app.http.app

echo.
echo Backend service stopped.
pause
