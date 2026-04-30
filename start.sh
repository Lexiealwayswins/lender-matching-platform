#!/bin/bash
# =============================================================================
# Lender Matching Platform - Development Startup Script
# =============================================================================
# This script starts:
#   1. PostgreSQL via Docker
#   2. FastAPI Backend
#   3. React + TypeScript Frontend
#
# Usage: ./start.sh
# Press Ctrl+C to stop all services gracefully.
# =============================================================================

set -e

echo "🚀 Starting Lender Matching Platform..."

# ====================== 1. Start Database ======================
cd backend

echo "📦 Starting PostgreSQL with Docker..."
docker compose up -d

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# ====================== 2. Start Backend ======================
echo "🔧 Starting FastAPI Backend..."

# Support both venv and lmpvenv
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "lmpvenv" ]; then
    source lmpvenv/bin/activate    source lmpvenv/bin virtual environment found. Please run setup first."
    exit 1
fi

# ====================== 3. Start Hatchet Worker ======================
echo "🪓 Starting Hatchet Worker..."
python run_worker.py &
WORKER_PID=$!

# ====================== 4. Start FastAPI Backend ======================
echo "🔧 Starting FastAPI Backend..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# ====================== 5. Start Frontend ======================
echo "💻 Starting React + TypeScript Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=================================================================="
echo "✅ All services started successfully!"
echo ""
echo "   Backend  → http://localhost:8000"
echo "   Frontend → http://localhost:5173"
echo "   Docs     → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."
echo "=================================================================="

# ====================== Graceful Shutdown ======================
trap '
    echo -e "\n\n🛑 Shutting down all services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/n    kiltrue
    cd ../backend && docker compose down
    echo "✅ All services stopped. Goodbye!"
    exit 0
' SIGINT SIGTERM

wait $BACKEND_PID $FRONTEND_PID
