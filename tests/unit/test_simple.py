"""Простые тесты для быстрого покрытия кода"""

def test_user_type_enum():
    """Тест enum UserType"""
    from app.models import UserType
    
    assert UserType.ADMIN.value == 'admin'
    assert UserType.PEASANT.value == 'peasant'
    assert str(UserType.ADMIN) == 'UserType.ADMIN'

def test_base_class():
    """Тест базового класса моделей"""
    from app.models import Base
    assert Base.__name__ == 'Base'

def test_models_have_tablename():
    """Тест что у всех моделей есть __tablename__"""
    from app.models import User, Owner, Horse, Jockey, Race, Result
    
    assert User.__tablename__ == 'users'
    assert Owner.__tablename__ == 'owners'
    assert Horse.__tablename__ == 'horses'
    assert Jockey.__tablename__ == 'jockeys'
    assert Race.__tablename__ == 'races'
    assert Result.__tablename__ == 'results'

def test_model_relationships():
    """Тест связей между моделями"""
    from app.models import Owner, Horse
    
    # Проверяем что связь определена
    assert hasattr(Owner, 'horses')
    assert hasattr(Horse, 'owner')
    
    # Проверяем типы полей
    from sqlalchemy.orm import RelationshipProperty
    assert isinstance(Owner.horses.property, RelationshipProperty)
    assert isinstance(Horse.owner.property, RelationshipProperty)

def test_user_mixin():
    """Тест что User использует UserMixin"""
    from app.models import User
    from flask_login import UserMixin
    
    user = User(login='test')
    # Проверяем методы UserMixin
    assert hasattr(user, 'is_active')
    assert hasattr(user, 'is_authenticated')
    assert hasattr(user, 'is_anonymous')
    assert hasattr(user, 'get_id')