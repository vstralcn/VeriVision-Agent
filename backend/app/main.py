from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.models import User
from app.api import auth, detection, admin, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and create default users on startup."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create default users
    db = SessionLocal()
    try:
        # Check if admin exists
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                nickname="Admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            print("✓ Created default admin user: admin@example.com / admin123")

        # Check if regular user exists
        regular_user = db.query(User).filter(User.email == "user@example.com").first()
        if not regular_user:
            regular_user = User(
                email="user@example.com",
                nickname="User",
                hashed_password=get_password_hash("user123"),
                role="user",
                is_active=True,
            )
            db.add(regular_user)
            print("✓ Created default user: user@example.com / user123")

        db.commit()
    finally:
        db.close()

    yield


app = FastAPI(
    title="Deepfake Detection Platform API",
    description="AI-powered deepfake image detection and traceability system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(detection.router, prefix="/api/detection", tags=["Detection"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Deepfake Detection Platform API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
