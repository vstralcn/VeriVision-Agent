#!/bin/bash

# Quick Start Script for Deepfake Detection Platform
# This script helps you get the platform up and running quickly

set -e

echo "🚀 Deepfake Detection Platform - Quick Start"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Start backend and database
echo "📦 Starting backend and database with Docker Compose..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Backend and database are running"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "=============================================="
echo "✅ Backend Setup Complete!"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Default Accounts:"
echo "  Admin: admin@example.com / admin123"
echo "  User:  user@example.com / user123"
echo ""
echo "=============================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed."
    echo "   Please install Node.js 18+ to run the frontend."
    echo ""
    echo "To start frontend manually:"
    echo "  cd frontend"
    echo "  npm install"
    echo "  npm run dev"
    exit 0
fi

echo "✅ Node.js is installed"
echo ""

# Ask if user wants to start frontend
read -p "Do you want to start the frontend now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend

    if [ ! -d "node_modules" ]; then
        npm install
    else
        echo "✅ Dependencies already installed"
    fi

    echo ""
    echo "🚀 Starting frontend development server..."
    echo ""
    echo "Frontend will be available at: http://localhost:5173"
    echo ""
    echo "Press Ctrl+C to stop the frontend server"
    echo ""

    npm run dev
else
    echo ""
    echo "To start the frontend later, run:"
    echo "  cd frontend"
    echo "  npm install"
    echo "  npm run dev"
    echo ""
    echo "Frontend will be available at: http://localhost:5173"
fi

echo ""
echo "=============================================="
echo "🎉 Setup Complete!"
echo "=============================================="
