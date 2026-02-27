#!/bin/bash

echo "Starting Grocery AI Multi-Agent Backend..."
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
# ── API Keys & Credentials ────────────────────────────────────────────────
if [ -f ../.env ]; then
  export $(grep -v '^#' ../.env | xargs)
elif [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "WARNING: .env file missing. Add your API keys there!"
fi
# ────────────────────────────────────────────────────────────────────────────
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "Starting Tablet Kiosk Frontend..."
cd frontend-tablet
npm run dev -- --port 5173 &
TABLET_PID=$!
cd ..

echo "Starting Management Dashboard Frontend..."
cd frontend-dashboard
npm run dev -- --port 5174 &
DASHBOARD_PID=$!
cd ..

echo "All services started!"
echo "- Backend API: http://localhost:8000"
echo "- Tablet Kiosk: http://localhost:5173"
echo "- Management Dashboard: http://localhost:5174"
echo ""
echo "Press Ctrl+C to stop all services."

# Trap SIGINT to kill all background processes
trap "echo 'Stopping all services...'; kill $BACKEND_PID; kill $TABLET_PID; kill $DASHBOARD_PID; exit" INT

wait
