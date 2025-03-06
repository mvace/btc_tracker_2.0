from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    # Add other configuration variables as needed

    class Config:
        env_file = ".env"  # Loads .env file automatically


settings = Settings()
