import os
from pydantic_settings import BaseSettings
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

class Settings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postulaciones_db")
    
    _database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres.ckoqbcmnvpmpbjmdgbug:DataBasePassword2208@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
    )
    
    # Force IPv4 by adding sslmode and other parameters
   #DATABASE_URL: str = f"{_database_url}?sslmode=require" if "supabase.co" in _database_url else _database_url
    DATABASE_URL: str = _database_url
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    CORS_ORIGINS: list = ["*"]
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development" or os.getenv("ENABLE_SWAGGER", "false").lower() == "true"
    SWAGGER_ALWAYS_ON: bool = os.getenv("ENABLE_SWAGGER", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True



settings = Settings()