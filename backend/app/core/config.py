from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://deepfake_user:deepfake_pass@127.0.0.1:5432/deepfake_db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    CERTIFICATION_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Development bootstrap accounts
    CREATE_DEFAULT_USERS: bool = True
    DEFAULT_ADMIN_EMAIL: str = "admin@example.com"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_USER_EMAIL: str = "user@example.com"
    DEFAULT_USER_PASSWORD: str = "user123"

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_PIXELS: int = 40_000_000

    # Model
    MODEL_NAME: str = "dima806/deepfake_vs_real_image_detection"
    MODEL_CACHE_DIR: str = "models/cache"
    MODEL_PATH: str = "app/ml_models/weights/best.pt"
    USE_GPU: bool = False

settings = Settings()
