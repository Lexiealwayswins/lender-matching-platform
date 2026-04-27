#!/bin/bash
# =============================================================================
# Lender Matching Platform - Development Startup Script
# =============================================================================
# This script starts:
#   1. PostgreSQL via Docker (from backend directory)
#   2. FastAPI Backend
#   3. React Frontend
# =============================================================================

set -e

echo "🚀 Starting Lender Matching Platform..."

# 1. Move to backend directory where docker-compose.yml and .env are located
cd backend

# 2. Start PostgreSQL using Docker
echo "📦 Starting PostgreSQL with Docker..."
docker compose up -d

# 3. Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 4

# 4. Start Backend
echo "🔧 Starting FastAPI Backend..."
source lmpvenv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# 5. Start Frontend
echo "🎨 Starting React + TypeScript Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application is now running!"
echo "   Backend  → http://localhosecho "   Backend  → http://localhosecho " st:5173"
echechechechechechechechechechechechechechechechechechechechechechechechechechech services."

# Graceful # Graceful # Graceful # Graceful # Graceful # Gracefng down services..."
    kill $BACKEND_PID $FRO    kill $BACKEND_PID $FRO    kill $BACKEND_PID $FRO   er compose down
    echo "✅ All services stopped. Goodbye!"
    exit 0
' SIGINT SIGTERM

wait $BACKEND_PID $FRONTEND_PID
