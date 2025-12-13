import pytest
import tempfile
import os
import time
from app import create_app
from app.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@pytest.fixture
def app():
    """Создаем тестовое Flask-приложение"""
    # Используем SQLite в памяти - проще и без файлов
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',  # В памяти, не в файле
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Создаем таблицы
    with app.app_context():
        engine = create_engine(app.config['DATABASE_URL'])
        Base.metadata.create_all(bind=engine)
    
    yield app
    
    # Нет необходимости удалять файлы - БД в памяти

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def session(app):
    """Тестовая сессия БД"""
    with app.app_context():
        engine = create_engine(app.config['DATABASE_URL'])
        with Session(engine) as session:
            yield session