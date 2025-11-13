echo "🔧 Starting Data Engineering Platform..."
docker-compose up -d
echo "⏳ Waiting for services..."
sleep 30
echo "✅ Services started!"
echo "Airflow: http://localhost:8080"
echo "Streamlit: http://localhost:8501"