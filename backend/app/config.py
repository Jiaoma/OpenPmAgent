"""Application configuration management."""
import os
from typing import Optional


class Settings:
    """Application settings."""

    def __init__(self):
        # Database
        self.database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./openpm_local.db')
        self.db_password = os.getenv('DB_PASSWORD', 'openpm_local')

        # Redis
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

        # Security
        self.secret_key = os.getenv('SECRET_KEY', 'local_dev_secret_key_12345678')
        self.algorithm = os.getenv('ALGORITHM', 'HS256')
        self.access_token_expire_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '120'))

        # Nginx
        self.nginx_port = int(os.getenv('NGINX_PORT', '8080'))

        # LLM
        self.llm_type = os.getenv('LLM_TYPE', 'none')
        self.llm_api_url = os.getenv('LLM_API_URL')
        self.llm_api_key = os.getenv('LLM_API_KEY')

        # Environment
        self.env = os.getenv('ENV', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'


# Global settings instance
settings = Settings()
