#!/usr/bin/env bash
# Launches the FastAPI backend and the Streamlit frontend together.
set -e

echo "Starting FastAPI backend on http://localhost:8000 ..."
uvicorn legalEaseAPI.main:app --reload --port 8000 &
BACKEND_PID=$!

sleep 2

echo "Starting Streamlit frontend on http://localhost:8501 ..."
streamlit run frontend/app.py

# When Streamlit exits, stop the backend too
kill $BACKEND_PID
