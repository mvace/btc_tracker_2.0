from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None  # e.g., full Railway URL
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = "localhost"
    postgres_port: Optional[int] = 5432

    class Config:
        env_file = ".env"

    def get_sync_url(self):
        """Return sync URL for psycopg2 (used by import_csv_data.py)"""
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    def get_async_url(self):
        """Return async URL for async engine (used by FastAPI async calls)"""
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace(
                    "postgresql://", "postgresql+asyncpg://"
                )
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()

SYNC_DATABASE_URL = settings.get_sync_url()
ASYNC_DATABASE_URL = settings.get_async_url()
