from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://deepfake_user:deepfake_pass@127.0.0.1:5432/deepfake_db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Model (optional)
    MODEL_NAME: str = "dima806/deepfake_vs_real_image_detection"
    MODEL_CACHE_DIR: str = "models/cache"
    USE_GPU: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
