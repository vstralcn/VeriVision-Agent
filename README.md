# Deepfake Detection Platform

AI-powered deepfake image detection and traceability system with trusted computing integration.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.10+ (for backend development)

### One-Command Deployment

```bash
# Clone the repository
cd deepfake-detection-platform

# Start backend and database with Docker
docker-compose up -d

# Install and start frontend
cd frontend
npm install
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Default Accounts

### Admin Account
- **Email**: admin@example.com
- **Password**: admin123
- **Access**: Full system access including admin panel

### User Account
- **Email**: user@example.com
- **Password**: user123
- **Access**: Standard user features

## 🏗️ Project Structure

```
deepfake-detection-platform/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── detection.py   # Detection operations
│   │   │   ├── admin.py       # Admin operations
│   │   │   └── user.py        # User operations
│   │   ├── core/              # Core configurations
│   │   │   ├── config.py      # Settings
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT & password hashing
│   │   ├── models/            # SQLAlchemy models
│   │   │   └── models.py      # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   │   └── schemas.py     # Request/response schemas
│   │   ├── services/          # Business logic
│   │   │   ├── detection_service.py  # Detection service
│   │   │   └── llm_service.py        # LLM explanation layer (Claude)
│   │   └── main.py            # FastAPI application
│   ├── alembic/               # Database migrations
│   ├── uploads/               # Uploaded files
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend Docker image
├── frontend/                  # Vue 3 frontend
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── stores/           # Pinia stores
│   │   ├── router/           # Vue Router
│   │   ├── views/            # Page components
│   │   │   ├── user/         # User pages
│   │   │   └── admin/        # Admin pages
│   │   ├── App.vue           # Root component
│   │   └── main.js           # Entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

## 🔧 Detailed Setup

### Backend Setup

#### Using Docker (Recommended)

```bash
# Start PostgreSQL and backend
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

#### Manual Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://deepfake_user:deepfake_pass@localhost:5432/deepfake_db"
export SECRET_KEY="your-secret-key-change-in-production"

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Features

### User Features

1. **Dashboard**
   - System overview
   - Recent detection history
   - Quick access to detection workspace

2. **Detection Workspace**
   - Image upload (drag & drop or file selection)
   - Real-time deepfake detection
   - Visualization heatmap showing manipulation areas
   - Intelligent analysis report with:
     - Verdict (Fake/Real)
     - Confidence score
     - Risk level assessment
     - Detailed analysis metrics
     - Recommendations
   - **LLM Explanation Layer** (powered by Claude):
     - Natural-language description of anomalous regions
     - Forensic reasoning for why the image appears manipulated
     - Risk level rationale
     - Comprehensive analyst-facing summary
   - Trusted certification with:
     - Unique certification ID
     - SHA256 hash
     - Perceptual hash (pHash)
     - Cryptographic signature
     - Signature verification

3. **Traceability Archive**
   - View image fingerprint history
   - Timeline of all operations
   - Certification verification
   - Complete audit trail

4. **Personal Center**
   - Profile management
   - Detection history
   - Statistics overview

### Admin Features

1. **Admin Dashboard**
   - Today's detection count
   - Fake detection ratio
   - User statistics
   - System overview

2. **User Management**
   - View all users
   - Enable/disable user accounts
   - View user detection statistics

3. **Audit Logs**
   - Complete system audit trail
   - Filter by action, status, date range
   - Detailed log inspection
   - Compliance monitoring

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Detection
- `POST /api/detection/upload` - Upload and detect image
- `GET /api/detection/history` - Get detection history
- `GET /api/detection/recent` - Get recent detections
- `GET /api/detection/{id}` - Get detection details
- `GET /api/detection/{id}/trace` - Get trace records
- `POST /api/detection/{id}/verify` - Verify certification

### User
- `GET /api/user/me` - Get user profile
- `PUT /api/user/me` - Update user profile

### Admin (Requires admin role)
- `GET /api/admin/dashboard/stats` - Get dashboard statistics
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/{id}/toggle-active` - Enable/disable user
- `GET /api/admin/audit-logs` - Get audit logs with filters
- `GET /api/admin/audit-logs/{id}` - Get audit log detail

## 🗄️ Database Schema

### Users Table
- User authentication and profile information
- Role-based access control (user/admin)
- Account status management

### Detections Table
- Detection results and metadata
- Image and heatmap paths
- Analysis reports
- Trusted certification data
- Image fingerprints (SHA256, pHash)

### Trace Records Table
- Complete audit trail for each detection
- Action history (uploaded, detected, verified)
- Metadata for each operation

### Audit Logs Table
- System-wide audit logging
- User actions tracking
- Security and compliance monitoring

## 🔐 Security Features

1. **JWT Authentication**
   - Secure token-based authentication
   - Configurable token expiration

2. **Password Hashing**
   - Bcrypt password hashing
   - Secure password storage

3. **Role-Based Access Control**
   - User and admin roles
   - Protected admin endpoints

4. **Trusted Certification**
   - Cryptographic signatures
   - Image fingerprinting (SHA256, pHash)
   - Signature verification

5. **Audit Logging**
   - Complete action tracking
   - Security event monitoring

## 🧪 Testing

### Backend Testing

```bash
# Start the development containers, then run the safety and detection-path tests
docker compose exec backend python -m pytest
```

### Frontend Testing

```bash
cd frontend

# Production build check; frontend unit and E2E tests are not configured yet
npm run build
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Remove volumes (WARNING: deletes database)
docker-compose down -v
```

## 🔧 Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://deepfake_user:deepfake_pass@postgres:5432/deepfake_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CERTIFICATION_KEY=replace-with-an-independent-secret
CREATE_DEFAULT_USERS=true  # development only
```

### Frontend

Frontend uses Vite proxy configuration in `vite.config.js` to connect to backend.

## 📊 Database Initialization

The database is automatically initialized on first startup:

1. Alembic creates or upgrades the schema
2. Demo accounts are created when enabled in development
3. The detection model and optional LLM service are initialized

To reset the database:

```bash
# Stop services
docker-compose down -v

# Start services (will reinitialize)
docker-compose up -d
```

## 🤖 LLM Explanation Layer

After the deepfake model produces a result, the platform passes the detection signals to **Claude** (via the Anthropic API) to generate a structured, analyst-facing explanation.

### Pipeline

```
Image Upload
    │
    ▼
ForensicNet (ML model)
    │  fake_probability  +  heatmap mask
    ▼
LLM Explanation Service  ──►  Claude (claude-haiku-4-5-20251001)
    │
    ▼
Structured JSON stored in detection.llm_explanation
    ├── anomalous_regions   – which spatial areas are suspicious
    ├── why_fake            – forensic reasoning for manipulation signals
    ├── risk_level_reason   – why the risk is classified Low / Medium / High
    └── overall_explanation – cohesive analyst-facing summary
```

### Configuration

After signing in as an administrator, configure the provider, model, and API key on the AI Agent Settings page. Detection still works when this feature is disabled or no key is configured. The current implementation stores the key in the database; production deployments should connect it to a secret manager.

### LLM Input Signals

| Signal | Source |
|---|---|
| `fake_probability` | ForensicNet output |
| `confidence` | Derived from `fake_probability` |
| `risk_level` | Low / Medium / High threshold rules |
| `heatmap_stats` | Spatial statistics derived from mask probability map |

## 🚨 Troubleshooting

### Backend won't start

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps
   ```

2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

3. Verify database connection:
   ```bash
   docker-compose exec postgres psql -U deepfake_user -d deepfake_db
   ```

### Frontend can't connect to backend

1. Verify backend is running on port 8000
2. Check Vite proxy configuration in `vite.config.js`
3. Check browser console for CORS errors

### Database migration issues

The baseline migration can adopt tables created by older releases, so it is
intentionally non-reversible. Back up the database before migration and restore
that backup if a rollback is required. Use `docker compose exec backend alembic
current` to inspect the applied revision.

## 📝 Development Notes

### Detection Model

The detection service loads the ForensicNet checkpoint configured by `MODEL_PATH`. If the model is missing or inference fails, the API returns an explicit error and never generates a random result. Checkpoints are not committed to Git, so deployments must provide one separately and verify its checksum. Training data, reported metrics, and generalization still require independent validation.

### Adding New Features

1. **Backend**: Add new endpoints in `backend/app/api/`
2. **Frontend**: Add new pages in `frontend/src/views/`
3. **Database**: Create Alembic migration for schema changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

## 🔗 Related Documentation

- [MODEL_DEPLOY.md](docs/MODEL_DEPLOY.md) - Model deployment guide
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review API documentation at `/docs`
- Check Docker logs for error messages

---

**Built with ❤️ using FastAPI, Vue 3, and Element Plus**
