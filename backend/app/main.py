from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, detection, user
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.models import User
from app.services.detection_service import detection_service
from app.services.llm_service import llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize runtime services after Alembic has prepared the database."""
    if settings.ENVIRONMENT.lower() == "production":
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            raise RuntimeError("SECRET_KEY must be changed in production")
        if not settings.CERTIFICATION_KEY:
            raise RuntimeError("CERTIFICATION_KEY must be set in production")
        if settings.CREATE_DEFAULT_USERS:
            raise RuntimeError("CREATE_DEFAULT_USERS must be disabled in production")

    db = SessionLocal()
    try:
        if settings.CREATE_DEFAULT_USERS:
            admin_user = db.query(User).filter(
                User.email == settings.DEFAULT_ADMIN_EMAIL
            ).first()
            if not admin_user:
                db.add(User(
                    email=settings.DEFAULT_ADMIN_EMAIL,
                    nickname="Admin",
                    hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                    role="admin",
                    is_active=True,
                ))

            regular_user = db.query(User).filter(
                User.email == settings.DEFAULT_USER_EMAIL
            ).first()
            if not regular_user:
                db.add(User(
                    email=settings.DEFAULT_USER_EMAIL,
                    nickname="User",
                    hashed_password=get_password_hash(settings.DEFAULT_USER_PASSWORD),
                    role="user",
                    is_active=True,
                ))
            db.commit()
    finally:
        db.close()

    detection_service.initialize()

    # Load LLM config from DB into the service singleton
    db = SessionLocal()
    try:
        from app.models.models import LLMConfig
        llm_db_config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
        if llm_db_config:
            llm_service.reload_config(llm_db_config)
            print(f"✓ LLM config loaded: provider={llm_db_config.provider} model={llm_db_config.model} enabled={llm_db_config.enabled}")
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
    """Process liveness check."""
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    """Readiness check for dependencies needed to produce detection results."""
    if not detection_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Detection model is unavailable",
        )
    return {"status": "ready", "model_device": detection_service.device}
