#!/bin/bash

# Development Helper Script
# Provides common development commands

set -e

show_help() {
    echo "Deepfake Detection Platform - Development Helper"
    echo "================================================"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start          - Start all services"
    echo "  stop           - Stop all services"
    echo "  restart        - Restart all services"
    echo "  logs           - View backend logs"
    echo "  logs-db        - View database logs"
    echo "  shell          - Open backend shell"
    echo "  db-shell       - Open database shell"
    echo "  migrate        - Run database migrations"
    echo "  reset-db       - Reset database (WARNING: deletes all data)"
    echo "  test-backend   - Run backend tests"
    echo "  lint-backend   - Lint backend code"
    echo "  frontend       - Start frontend dev server"
    echo "  build-frontend - Build frontend for production"
    echo "  clean          - Clean up containers and volumes"
    echo "  status         - Show service status"
    echo "  help           - Show this help message"
    echo ""
}

case "$1" in
    start)
        echo "🚀 Starting services..."
        docker-compose up -d
        echo "✅ Services started"
        docker-compose ps
        ;;

    stop)
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Services stopped"
        ;;

    restart)
        echo "🔄 Restarting services..."
        docker-compose restart
        echo "✅ Services restarted"
        docker-compose ps
        ;;

    logs)
        echo "📋 Backend logs (Ctrl+C to exit):"
        docker-compose logs -f backend
        ;;

    logs-db)
        echo "📋 Database logs (Ctrl+C to exit):"
        docker-compose logs -f postgres
        ;;

    shell)
        echo "🐚 Opening backend shell..."
        docker-compose exec backend bash
        ;;

    db-shell)
        echo "🐚 Opening database shell..."
        docker-compose exec postgres psql -U deepfake_user -d deepfake_db
        ;;

    migrate)
        echo "🔄 Running database migrations..."
        docker-compose exec backend alembic upgrade head
        echo "✅ Migrations complete"
        ;;

    reset-db)
        read -p "⚠️  This will delete ALL data. Are you sure? (yes/no) " -r
        echo ""
        if [[ $REPLY == "yes" ]]; then
            echo "🗑️  Resetting database..."
            docker-compose down -v
            docker-compose up -d
            echo "✅ Database reset complete"
        else
            echo "❌ Cancelled"
        fi
        ;;

    test-backend)
        echo "🧪 Running backend tests..."
        docker-compose exec backend pytest
        ;;

    lint-backend)
        echo "🔍 Linting backend code..."
        docker-compose exec backend flake8 app/
        ;;

    frontend)
        echo "🚀 Starting frontend dev server..."
        cd frontend
        npm run dev
        ;;

    build-frontend)
        echo "📦 Building frontend..."
        cd frontend
        npm run build
        echo "✅ Frontend built to frontend/dist/"
        ;;

    clean)
        read -p "⚠️  This will remove all containers and volumes. Continue? (yes/no) " -r
        echo ""
        if [[ $REPLY == "yes" ]]; then
            echo "🧹 Cleaning up..."
            docker-compose down -v
            rm -rf backend/uploads/images/*
            rm -rf backend/uploads/heatmaps/*
            echo "✅ Cleanup complete"
        else
            echo "❌ Cancelled"
        fi
        ;;

    status)
        echo "📊 Service Status:"
        docker-compose ps
        echo ""
        echo "🌐 Endpoints:"
        echo "  Backend API: http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        echo "  Frontend: http://localhost:5173"
        echo ""
        echo "👤 Default Accounts:"
        echo "  Admin: admin@example.com / admin123"
        echo "  User:  user@example.com / user123"
        ;;

    help|"")
        show_help
        ;;

    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
