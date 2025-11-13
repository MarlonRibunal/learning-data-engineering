SERVICE=${1:-airflow-webserver}
echo "📋 Showing logs for: $SERVICE"
docker-compose logs -f $SERVICE