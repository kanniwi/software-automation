"""Pure-python entrypoint for container start.

Behavior:
- Read DATABASE_URL from env
- Wait for the DB to be ready (try connecting via SQLAlchemy)
- Run Alembic migrations programmatically (alembic upgrade head)
- Replace the process with gunicorn to serve the Flask app

This avoids using shell scripts and keeps init logic in Python.
"""
import os
import sys
import time
import logging
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("entrypoint")


def normalize_db_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def wait_for_db(url: str, timeout: int = 60):
    start = time.time()
    engine = create_engine(url, future=True)
    last_exc = None
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info("Database is ready: %s", url)
            return
        except Exception as exc:
            last_exc = exc
            if time.time() - start > timeout:
                log.exception("Timed out waiting for database: %s", exc)
                raise
            log.info("Waiting for database to be ready (%s). Sleeping 1s...", exc)
            time.sleep(1)


def run_alembic_upgrade():
    # assume alembic.ini is in the current working directory
    cfg = Config(os.path.join(os.getcwd(), "alembic.ini"))
    # If DATABASE_URL is set, make sure alembic uses it
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        cfg.set_main_option("sqlalchemy.url", db_url)
    log.info("Running alembic upgrade head (alembic.ini=%s)", cfg.config_file_name)
    command.upgrade(cfg, "head")


def main():
    db_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    db_url = normalize_db_url(db_url)

    # Wait for DB only if not sqlite
    if not db_url.startswith("sqlite"):
        log.info("Waiting for DB at %s", db_url)
        wait_for_db(db_url, timeout=120)
    else:
        log.info("Using sqlite, skipping wait")

    # Run migrations (if alembic is available)
    try:
        run_alembic_upgrade()
    except Exception as exc:
        log.warning("Alembic upgrade failed: %s", exc)
        # fallback: try to create tables via SQLAlchemy metadata
        try:
            from app import models
            engine = create_engine(db_url, future=True)
            models.Base.metadata.create_all(bind=engine)
            log.info("Fallback: create_all applied")
        except Exception:
            log.exception("Fallback create_all also failed")

    # Exec gunicorn to serve the app (replaces current process)
    log.info("Starting gunicorn")
    os.execvp("gunicorn", ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "app:create_app()"])


if __name__ == "__main__":
    main()
