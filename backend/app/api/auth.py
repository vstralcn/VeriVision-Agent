from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.models import User, AuditLog
from app.schemas.schemas import Token, LoginRequest, UserCreate, UserResponse
from app.core.config import settings
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        nickname=user_data.nickname,
        hashed_password=hashed_password,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log registration
    audit_log = AuditLog(
        user_id=new_user.id,
        action="register",
        success=True,
        detail={"email": user_data.email},
    )
    db.add(audit_log)
    db.commit()

    return new_user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()

    # Verify credentials
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Log failed login
        audit_log = AuditLog(
            user_id=user.id if user else None,
            action="login",
            success=False,
            detail={"email": login_data.email, "reason": "invalid_credentials"},
        )
        db.add(audit_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Log successful login
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        success=True,
        detail={"email": login_data.email},
    )
    db.add(audit_log)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user
