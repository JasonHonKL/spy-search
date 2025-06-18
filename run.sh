#!/bin/bash
set -e  # Exit on any error

# Trap SIGINT (Ctrl-C) and SIGTERM to kill child processes
cleanup() {
  echo "Stopping backend and frontend..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

echo "Starting application..."

# Check if uvicorn is installed
if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not found, installing..."
  uv pip install --system uvicorn || { echo "Failed to install uvicorn"; exit 1; }
fi

# Start backend (bind to all interfaces so frontend can reach it)
echo "Starting FastAPI backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..30}; do
  if curl -f http://0.0.0.0:8000/health >/dev/null 2>&1; then
    echo "Backend is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "Backend failed to start within timeout"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
  fi
  sleep 2
done

# Start frontend
echo "Starting frontend..."
(
  cd frontend || { echo "Failed to cd to frontend directory"; exit 1; }
  
  # Install npm dependencies only if node_modules is missing
  if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --legacy-peer-deps || { echo "npm install failed"; exit 1; }
  else
    echo "npm dependencies already installed"
  fi
  
  # Set environment variables for host binding
  export HOST=0.0.0.0
  export PORT=8080
  export BACKEND_URL=http://localhost:8000
  
  # Start frontend with host binding
  npm run dev -- --host 0.0.0.0 --port 8080 2>/dev/null || \
  npm run dev -- -H 0.0.0.0 -p 8080 2>/dev/null || \
  HOST=0.0.0.0 PORT=8080 npm run dev
) &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
for i in {1..30}; do
  if curl -f http://127.0.0.1:8080 >/dev/null 2>&1; then
    echo "Frontend is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "Frontend failed to start within timeout"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
  fi
  sleep 2
done

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend accessible at: http://0.0.0.0:8000"
echo "Frontend accessible at: http://0.0.0.0:8080"

# Wait for both processes to exit
wait $BACKEND_PID $FRONTEND_PID