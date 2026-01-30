# Quick Start Guide

## 🚀 One-Command Start

```bash
./start.sh
```

This script will:
1. Start backend and database with Docker
2. Wait for services to be ready
3. Optionally install and start the frontend

## 📋 Manual Setup

### Backend + Database

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 👤 Default Login Credentials

### Admin Account
- Email: `admin@example.com`
- Password: `admin123`

### User Account
- Email: `user@example.com`
- Password: `user123`

## 🛠️ Development Commands

Use the `dev.sh` helper script:

```bash
./dev.sh help           # Show all commands
./dev.sh start          # Start services
./dev.sh stop           # Stop services
./dev.sh logs           # View backend logs
./dev.sh shell          # Open backend shell
./dev.sh db-shell       # Open database shell
./dev.sh status         # Show service status
```

## 🧪 Testing the Platform

1. **Login**: Use admin or user credentials
2. **Upload Image**: Go to Detection workspace
3. **View Results**: See heatmap, analysis report, and certification
4. **Check Traceability**: View the image's audit trail
5. **Admin Panel**: Login as admin to access admin features

## 🐛 Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
```

### Database connection issues
```bash
docker-compose ps
docker-compose restart postgres
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## 📚 More Information

- See [README.md](../README.md) for full documentation
- See [MODEL_DEPLOY.md](MODEL_DEPLOY.md) for model integration
- See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details
