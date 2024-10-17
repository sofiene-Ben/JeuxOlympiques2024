import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()  # Appel de la fonction create_app() pour récupérer l'application Flask
    # app.config['TESTING'] = True  # Active le mode test
    with app.test_client() as client:
        yield client  # Retourne le client de test

def test_add(client):
    response = client.get('/add/3/5')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == '8'

def test_add_2(client):
    response = client.get('/add/7/5')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == '12'