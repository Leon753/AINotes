from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from alembic import context
from models import Base  # Import your models
from dotenv import load_dotenv
import os

config = context.config
load_dotenv()
# Use Sync Engine for Alembic
SYNC_DATABASE_URL = os.getenv("DATABASE_URL").replace("asyncpg", "psycopg2")

target_metadata = Base.metadata  # Metadata from models

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(url=SYNC_DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode using sync engine."""
    connectable = create_engine(SYNC_DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
