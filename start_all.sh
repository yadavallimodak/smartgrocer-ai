#!/bin/bash

echo "Starting Grocery AI Multi-Agent Backend..."
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
export TAVILY_API_KEY="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"
export GEMINI_API_KEY="AIzaSyAbKwNZ2gkn3kbXdKW6zdVIdWcLfEzik80"
export SPOONACULAR_API_KEY="ac91f8498bd84bdab211378301001e28"
# ── Kroger Store Config ─────────────────────────────────────────────────────
# Change STORE_ID to the Location ID of this physical device's store.
export STORE_ID="01400943"
# ── Kroger API Credentials (get from developer.kroger.com) ─────────────────
# Fill these in to switch from mock data to live Kroger Products + Locations API.
export KROGER_CLIENT_ID="groceryaikioskassistantapp-bbcc4snj"
export KROGER_CLIENT_SECRET="qkQoEw57OoOD1o4wiSwUasG55gstfEemCMsEP-k8"
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
