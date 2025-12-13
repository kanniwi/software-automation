import pytest

def test_bug_divide_endpoint(client):
    """Тест для эндпоинта с делением на ноль"""
    response = client.get('/api/bug/divide')
    assert response.status_code == 200 
    
