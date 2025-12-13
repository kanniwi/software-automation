import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Импортируем Base и модели
from app.models import Base, User, UserType, Owner, Horse, Jockey, Race, Result

# Фикстура для тестовой базы данных
@pytest.fixture
def engine():
    """Создаем тестовую базу в памяти"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine):
    """Тестовая сессия"""
    with Session(engine) as session:
        yield session

def test_user_creation(session):
    """Тест создания пользователя"""
    user = User(login='testuser', password='hashed_password')
    user.type = UserType.PEASANT
    
    session.add(user)
    session.commit()
    
    # Проверяем
    saved_user = session.query(User).filter_by(login='testuser').first()
    assert saved_user is not None
    assert saved_user.login == 'testuser'
    assert saved_user.type == UserType.PEASANT
    assert not saved_user.is_admin

def test_user_password_hashing():
    """Тест хеширования пароля"""
    user = User(login='testuser')
    user.set_password('secret123')
    
    assert user.check_password('secret123') is True
    assert user.check_password('wrong') is False

def test_admin_user():
    """Тест администратора"""
    user = User(login='admin', password='hash')
    user.type = UserType.ADMIN
    
    assert user.is_admin is True
    assert user.type == UserType.ADMIN

def test_owner_creation(session):
    """Тест создания владельца лошади"""
    owner = Owner(name='John Doe', address='123 Street', phone='+1234567890')
    
    session.add(owner)
    session.commit()
    
    saved_owner = session.query(Owner).filter_by(name='John Doe').first()
    assert saved_owner.name == 'John Doe'
    assert saved_owner.address == '123 Street'

def test_horse_creation(session):
    """Тест создания лошади"""
    # Сначала создаем владельца
    owner = Owner(name='Horse Owner')
    session.add(owner)
    session.commit()
    
    # Создаем лошадь
    horse = Horse(name='Lightning', gender='male', age=5, owner_id=owner.id)
    
    session.add(horse)
    session.commit()
    
    saved_horse = session.query(Horse).filter_by(name='Lightning').first()
    assert saved_horse.name == 'Lightning'
    assert saved_horse.gender == 'male'
    assert saved_horse.age == 5
    assert saved_horse.owner_id == owner.id