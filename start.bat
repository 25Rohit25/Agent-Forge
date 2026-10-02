@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo     _                    _   ______                      
echo    / \   __ _  ___ _ __ | |_|  ____|___  _ __ __ _  ___ 
echo   / _ \ / _` |/ _ \ '_ \| __| |__ / _ \| '__/ _` |/ _ \
echo  / ___ \ (_| |  __/ | | | |_|  __| (_) | | | (_| |  __/
echo /_/   \_\__, |\___|_| |_|\__|_|   \___/|_|  \__, |\___|
echo         |___/                               |___/      
echo ==============================================================================
echo        Autonomous Agentic AI Developer Workspace
echo ==============================================================================
echo.

echo Choose startup mode:
echo [1] Docker Compose (Full Stack: Postgres + pgvector, Redis, Backend, Frontend)
echo [2] Local Dev (Backend on 8000 + Frontend Vite on 5173 with SQLite fallback)
echo.

set /p MODE="Enter mode [1 or 2] (Default: 2): "
if "%MODE%"=="" set MODE=2

if "%MODE%"=="1" (
    echo Starting AgentForge via Docker Compose...
    docker compose up --build
    goto end
)

if "%MODE%"=="2" (
    echo Starting AgentForge in Local Development Mode...
    
    REM 1. Activate backend virtualenv and run server
    echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
    start "AgentForge Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"
    
    REM 2. Wait 2 seconds
    timeout /t 2 /nobreak >nul
    
    REM 3. Start frontend dev server
    echo [2/2] Starting React Frontend on http://localhost:5173 ...
    start "AgentForge Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
    
    echo.
    echo ==============================================================================
    echo AgentForge is launching!
    echo Backend API:  http://localhost:8000 (Docs: http://localhost:8000/docs)
    echo Frontend UI:  http://localhost:5173
    echo ==============================================================================
    goto end
)

:end
