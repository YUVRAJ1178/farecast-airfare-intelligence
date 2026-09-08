"""
Airfare Intelligence Platform — Database Connection & Initialization
Phase 5: PostgreSQL
"""

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv

from backend.app.models import Base

# Load environment variables from .env if present
load_dotenv()

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Read database URL from environment.
    Supports both DATABASE_URL and individual component env vars.
    Defaults directly to verified local SQLite if no external DB configured.
    """
    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    # Only connect to Postgres if POSTGRES_HOST is explicitly provided
    if os.getenv("POSTGRES_HOST"):
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "airfare_intelligence")
        user = os.getenv("POSTGRES_USER", "airfare_user")
        password = os.getenv("POSTGRES_PASSWORD", "")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    # Default to verified SQLite database
    sqlite_path = Path(__file__).parent.parent.parent / "airfare.db"
    return f"sqlite:///{sqlite_path.as_posix()}"


def create_db_engine(database_url: str = None):
    """Create SQLAlchemy engine with sensible defaults and SQLite fallback."""
    url = database_url or get_database_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})

    try:
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection not reachable ({e}). Falling back to local SQLite.")
        sqlite_path = Path(__file__).parent.parent.parent / "airfare.db"
        return create_engine(f"sqlite:///{sqlite_path.as_posix()}", connect_args={"check_same_thread": False})


# Module-level engine and session factory (created on first use)
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Automatically closes session on completion or error.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database: create all tables if they don't exist.
    Safe to call multiple times (idempotent).
    """
    engine = get_engine()
    try:
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema ready.")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def check_db_connection() -> dict:
    """
    Check database connectivity.
    Returns status dict for the /health and /live-status endpoints.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return {"status": "connected", "error": None}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}
