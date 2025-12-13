import pytest

def test_bug_divide_endpoint(client):
    """Тест для эндпоинта с делением на ноль"""
    response = client.get('/api/bug/divide')
    # Этот тест должен упасть с 500 ошибкой
    assert response.status_code == 500  # Internal Server Error
    
