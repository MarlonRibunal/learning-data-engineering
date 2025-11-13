echo "💥 DESTROYING ALL DATA..."
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down -v --rmi all --remove-orphans
    echo "✅ Complete destruction finished"
fi