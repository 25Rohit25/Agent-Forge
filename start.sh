#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "    _                    _   ______                      "
echo "   / \   __ _  ___ _ __ | |_|  ____|___  _ __ __ _  ___ "
echo "  / _ \ / _` |/ _ \ '_ \| __| |__ / _ \| '__/ _` |/ _ \ "
echo " / ___ \ (_| |  __/ | | | |_|  __| (_) | | | (_| |  __/ "
echo "/_/   \_\__, |\___|_| |_|\__|_|   \___/|_|  \__, |\___| "
echo "        |___/                               |___/      "
echo "=============================================================================="
echo "       Autonomous Agentic AI Developer Workspace"
echo "=============================================================================="
echo ""

echo "Choose startup mode:"
echo "[1] Docker Compose (Full Stack: Postgres + pgvector, Redis, Backend, Frontend)"
echo "[2] Local Dev (Backend on 8000 + Frontend Vite on 5173 with SQLite fallback)"
echo ""

read -p "Enter mode [1 or 2] (Default: 2): " MODE
MODE=${MODE:-2}

if [ "$MODE" = "1" ]; then
    echo "Starting AgentForge via Docker Compose..."
    docker compose up --build
elif [ "$MODE" = "2" ]; then
    echo "Starting AgentForge in Local Development Mode..."
    
    # Check if virtualenv exists
    if [ ! -d "backend/venv" ]; then
        echo "Creating backend virtualenv..."
        python3 -m venv backend/venv
        backend/venv/bin/pip install -r backend/requirements.txt
    fi
    
    # 1. Start Backend in background
    echo "[1/2] Starting FastAPI Backend on http://localhost:8000 ..."
    (cd backend && ./venv/bin/uvicorn app.main:app --reload --port 8000) &
    BACKEND_PID=$!
    
    # 2. Start Frontend
    echo "[2/2] Starting React Frontend on http://localhost:5173 ..."
    (cd frontend && npm run dev) &
    FRONTEND_PID=$!
    
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    
    echo ""
    echo "=============================================================================="
    echo "AgentForge is running!"
    echo "Backend API:  http://localhost:8000 (Docs: http://localhost:8000/docs)"
    echo "Frontend UI:  http://localhost:5173"
    echo "Press Ctrl+C to terminate both servers."
    echo "=============================================================================="
    
    wait
fi
