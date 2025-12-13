def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.content_type

def test_register_page_get(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200
