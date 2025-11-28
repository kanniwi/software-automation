from flask import Flask
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()


class EnvConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

def create_app(config_object=None):
    app = Flask(__name__)
    
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(EnvConfig)

    # Basic config
    app.secret_key = app.config["SECRET_KEY"]

    # Database setup: use DATABASE_URL env var or fallback to sqlite file
    DATABASE_URL = app.config.get("DATABASE_URL", "sqlite:///dev.db")
    if isinstance(DATABASE_URL, str) and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    app.db_engine = engine
    app.db_session = SessionLocal

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            from app.models import User
            session = SessionLocal()
            user = session.get(User, int(user_id))
            session.close()
            return user
        except Exception:
            return None

    # Import models and create tables in development (convenience)
    try:
        from app import models
        models.Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    # Подключаем роуты
    from app.routes import main
    app.register_blueprint(main)

    return app
