from sqlalchemy import create_engine
from alembic import context
from app.database import DATABASE_URL
from app.models import Base
from core.settings import settings

# Ensure Alembic uses a synchronous database connection
DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

# Create a synchronous engine
engine = create_engine(DATABASE_URL)

# Add target_metadata
target_metadata = Base.metadata


def run_migrations_online():
    """Run migrations in 'online' mode."""
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
