@echo off
title NyayaSim Multi-Agent Backend (Ren'Py Bridge)
echo =======================================================
echo Starting NyayaSim Multi-Agent Backend Server...
echo API endpoints: http://127.0.0.1:8000 or http://127.0.0.1:8001
echo Press Ctrl+C to stop the backend.
echo =======================================================
py -3.11 -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
if %ERRORLEVEL% NEQ 0 (
    echo Port 8000 in use, starting on port 8001...
    py -3.11 -m uvicorn backend.server:app --host 127.0.0.1 --port 8001
)
pause

