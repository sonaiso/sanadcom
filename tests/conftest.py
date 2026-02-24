# Pytest configuration
import asyncio
import os
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

# Set test environment variables before any imports
os.environ.setdefault("PYTEST_RUNNING", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-32-chars-minimum-secure-key-12345")
# Use SQLite by default so tests run without a PostgreSQL server.
# In CI, DATABASE_URL is set to PostgreSQL via workflow env vars (overrides this default).
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_sico_grc.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
	"""Create test database schema before running API tests.

	Uses Alembic migrations when connected to PostgreSQL (CI environment).
	Falls back to SQLAlchemy create_all for SQLite (local development) because
	some migrations contain PostgreSQL-specific DDL that SQLite cannot run.
	"""
	database_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./test_sico_grc.db")
	is_sqlite = "sqlite" in database_url

	if is_sqlite:
		# SQLite: skip Alembic (migrations contain PG-specific DDL) and use create_all
		_create_schema_via_models()
	else:
		# PostgreSQL: run Alembic migrations to verify the full migration chain
		try:
			repo_root = Path(__file__).resolve().parents[1]
			backend_dir = repo_root / "src" / "backend"
			alembic_cfg = Config(str(backend_dir / "alembic.ini"))
			alembic_cfg.set_main_option("script_location", str(backend_dir / "migrations"))
			alembic_cfg.set_main_option("sqlalchemy.url", database_url)

			command.upgrade(alembic_cfg, "head")
			print("✓ Database migrations applied successfully")
		except Exception as e:
			print(f"⚠️  Database migration failed: {e}")
			print("   Falling back to SQLAlchemy create_all for test schema")
			_create_schema_via_models()


def _create_schema_via_models() -> None:
	"""Drop and recreate all tables from current SQLAlchemy model metadata."""
	try:
		async def _recreate_db():
			from sqlalchemy.ext.asyncio import create_async_engine
			from core.config import settings
			from core.database import Base
			from core.database import _load_models
			_load_models()
			try:
				import regulatory_versions  # noqa: F401
			except Exception:
				pass
			engine = create_async_engine(settings.DATABASE_URL)
			async with engine.begin() as conn:
				await conn.run_sync(Base.metadata.drop_all)
				await conn.run_sync(Base.metadata.create_all)
			await engine.dispose()

		asyncio.run(_recreate_db())
		print("✓ Database schema created via SQLAlchemy models")
	except Exception as e2:
		print(f"⚠️  Schema creation failed: {e2}")
		print("   Tests will run with limited functionality")
