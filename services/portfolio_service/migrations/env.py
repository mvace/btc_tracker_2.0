# ==============================================================================
# 1. PATH SETUP
# This is the most important part. It adds your project's root directory
# to Python's path, so Alembic can find your 'app' and 'core' modules.
# ==============================================================================
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ==============================================================================

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ==============================================================================
# 2. MODEL AND SETTINGS IMPORTS
# Import your Base object and settings. We also explicitly import the models
# to ensure they are registered with SQLAlchemy's metadata.
# ==============================================================================
from core.settings import settings
from app.models import Base, User, Portfolio, Transaction

# ==============================================================================

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ==============================================================================
# 3. TARGET METADATA
# This is the key for 'autogenerate' to work. We point it to your Base's
# metadata, so Alembic knows what your models should look like.
# ==============================================================================
target_metadata = Base.metadata
# ==============================================================================


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    This is the synchronous function that contains the core migration logic.
    """
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    This is the async "wrapper" function. It connects to the database
    using your application's secure settings and then calls the synchronous
    function above to do the actual work.
    """
    connectable = create_async_engine(
        settings.db_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
