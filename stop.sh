#!/bin/bash

# Stop Script for Deepfake Detection Platform

set -e

echo "🛑 Stopping Deepfake Detection Platform"
echo "========================================"
echo ""

# Stop Docker Compose services
echo "📦 Stopping backend and database..."
docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "To start again, run: ./start.sh"
echo "To remove all data (including database), run: docker-compose down -v"
