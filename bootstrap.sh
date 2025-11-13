#!/bin/bash
set -e
echo "🚀 Learning Data Engineering - Bootstrap"
if ! docker system info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi
echo "🐳 Building and starting services..."
docker-compose up --build -d
echo "⏳ Waiting for services..."
sleep 30
echo "🎉 Setup Complete!"
echo "Airflow: http://localhost:8080"
echo "Streamlit: http://localhost:8501"