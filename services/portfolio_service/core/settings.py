# core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # --- App ---
    APP_ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="info")
    PORT: int = Field(default=8001)

    # --- Database (component parts) ---
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="portfolio_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

    # Optional combined DSN; if unset, use the components above
    DATABASE_URL: str | None = None
    DATABASE_URL_TEST: str | None = None

    # --- External services ---
    PRICE_SERVICE_BASE_URL: str = Field(default="http://localhost:8000")

    # --- Security / Auth ---
    SECRET_KEY: str = Field(..., description="JWT signing secret")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRES_MIN: int = Field(default=15)
    REFRESH_TOKEN_EXPIRES_DAYS: int = Field(default=7)

    # pydantic-settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def db_url(self) -> str:
        """
        Prefer DATABASE_URL if provided; otherwise compose from individual parts.
        Example:
          postgresql+asyncpg://user:pass@host:port/dbname
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Instantiate once and import from elsewhere
settings = Settings()
