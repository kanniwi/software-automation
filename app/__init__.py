from flask import Flask
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from dotenv import load_dotenv
import logging

# load .env if present
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Basic config
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Database setup: use DATABASE_URL env var or fallback to sqlite file
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

    # Normalize common Heroku-style URL (postgres://) to SQLAlchemy expected scheme
    if isinstance(DATABASE_URL, str) and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Enable pool_pre_ping to avoid stale connection errors with Postgres
    engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)

    # Session factory attached to app for use in routes
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    app.db_engine = engine
    app.db_session = SessionLocal

    # Quick connection test (will raise/ log on failure)
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        app.logger.info("Database connected: %s", DATABASE_URL)
    except Exception as exc:
        app.logger.warning("Could not connect to database: %s", exc)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)

    # user loader uses a fresh session to load the user by primary key
    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            # import here to avoid circular import at module import time
            from app.models import User
            session = SessionLocal()
            user = session.get(User, int(user_id))
            session.close()
            return user
        except Exception:
            return None

    # Import models and create tables if they don't exist (safe for development)
    try:
        from app import models
        models.Base.metadata.create_all(bind=engine)
    except Exception:
        # if models can't be imported or creation fails, continue without crashing here
        pass

    # Подключаем роуты
    from app.routes import main
    app.register_blueprint(main)

    return app
