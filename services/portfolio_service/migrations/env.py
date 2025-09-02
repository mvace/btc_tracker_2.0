import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from core.settings import settings
from app.database import Base
from app.models import User, Portfolio, Transaction  # ensure all models are imported

# Alembic Config object
config = context.config

# Setup logging from .ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate'
target_metadata = Base.metadata


# ------------------------
# Offline migrations
# ------------------------
def run_migrations_offline():
    """Run migrations in 'offline' mode (no DB connection required)."""
    url = settings.db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------
# Online migrations
# ------------------------
def do_run_migrations(connection: Connection):
    """Synchronous migration logic executed via async connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(settings.db_url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# ------------------------
# Main execution
# ------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
