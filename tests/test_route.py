import pytest
from app import create_app, db
import re
from unittest.mock import patch
from app.models import User, Ticket
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app = create_app()  # Appel de la fonction create_app() pour récupérer l'application Flask
    # app.config['TESTING'] = True  # Active le mode test
    with app.test_client() as client:
        yield client  # Retourne le client de test

@pytest.fixture
def user():
    app = create_app()  # Appel de la fonction create_app() pour récupérer l'application Flask
    with app.app_context():  # Crée un contexte d'application
                # Vérifie si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email='test@gmail.com').first()
        if existing_user:
            return existing_user  # Retourne l'utilisateur existant
        
        hashed_pw = generate_password_hash('Sofiene1234@!') # Hachage du mot de passe
        user = User(
            email='test@gmail.com',
            password_hash=hashed_pw,
            firstname='sofiene',
            lastname='ben',
            is_admin=False,
            is_staff=False,
            )  # Utilise le nom correct de l'attribut
        db.session.add(user)
        db.session.commit()
        return user
    

@pytest.fixture
def setup_database():
    app = create_app()
    with app.app_context():
        yield db  # Rend la base de données accessible pour les tests

def test_drop_ticket(setup_database):
    # Supposons que l'utilisateur avec ID 5 existe déjà et qu'il a des tickets
    tickets = Ticket.query.filter_by(user_id=5).all()
    
    # Compter le nombre de tickets existants avant suppression
    initial_count = len(tickets)
    
    # Vérifier qu'il y a des tickets à supprimer
    if initial_count > 0:
        for ticket in tickets:
            db.session.delete(ticket)
        db.session.commit()
    
        # Vérifie que tous les tickets ont été supprimés
        tickets_after = Ticket.query.filter_by(user_id=5).all()
        assert len(tickets_after) == 0
    else:
        print("Aucun ticket à supprimer pour l'utilisateur avec ID 5.")



def get_csrf_token(client):
    response = client.get('/offers')  # ou toute autre page contenant le token
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')

    # Recherche du token dans le contenu HTML
    match = re.search(r'name="csrf_token" value="(.+?)"', html_content)
    if match:
        return match.group(1)
    else:
        raise ValueError("CSRF token not found in the response.")


def test_route_home(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert ' <h1 class="title-home">Bienvenue aux Jeux Olympiques de 2024 à Paris!</h1>' in html

def test_cart(client):
    csrf_token = get_csrf_token(client)
    
    response = client.post('/add_to_cart/1', data={'csrf_token': csrf_token})
    assert response.status_code == 200
    assert response.get_json() == {'success': True, 'message': 'Offre ajoutée au panier !'}
    
    # Vérification du contenu du panier après le 1er ajout
    response_panier = client.get('/panier')
    assert response_panier.status_code == 200, f"Expected status code 200 but got {response_panier.status_code}"
    html_response_panier = response_panier.data.decode('utf-8')
    assert b'solo' in response_panier.data
    assert b'30.0' in response_panier.data  # Vérifie le prix
    assert '<td><span id="quantite-1">1</span></td>' in html_response_panier
    assert '<td><span id="total-1">30.0 </span>€</td>' in html_response_panier
    assert '<h3>Total : 30.0 €</h3>' in html_response_panier

    # Ajout de l'offre une deuxième fois
    response_second_add = client.post('/add_to_cart/1', data={'csrf_token': csrf_token})
    assert response_second_add.status_code == 200
    assert response_second_add.get_json() == {'success': True, 'message': 'Offre ajoutée au panier !'}

    # Vérification du contenu du panier après le deuxième ajout
    response_panier_after_second_add = client.get('/panier')
    assert response_panier_after_second_add.status_code == 200
    html_response_panier_after_second_add = response_panier_after_second_add.data.decode('utf-8')
    assert '<td><span id="quantite-1">2</span></td>' in html_response_panier_after_second_add
    assert '<td><span id="total-1">60.0 </span>€</td>' in html_response_panier_after_second_add
    assert '<h3>Total : 60.0 €</h3>' in html_response_panier_after_second_add


    response_delete = client.post('/remove_from_panier/1', data={'csrf_token': csrf_token})
    assert response_delete.status_code == 302

    # Vérifier que l'utilisateur est redirigé vers la page du panier
    response_panier_after_delete = client.get('/panier')
    assert response_panier_after_delete.status_code == 200

    # Vérifie que le message indiquant qu'il n'y a pas d'offres est présent
    htm_panier_after_delete = response_panier_after_delete.data.decode('utf-8')
    assert '<p>Aucune offre dans le panier pour le moment.</p>' in htm_panier_after_delete

    # Test avec un ID d'offre invalide (ex: 999)
    response_false_id = client.post('/add_to_cart/999', data={'csrf_token': csrf_token})
    assert response_false_id.status_code == 404
    assert response_false_id.get_json() == {'success': False, 'message': 'Offre introuvable.'}



def test_ticket(client):

    csrf_token = get_csrf_token(client)

    response_ticket = client.get('/ticket', data={'csrf_token': csrf_token}, follow_redirects=True)
    assert response_ticket.status_code == 200, f"Expected status code 200 but got {response_ticket.status_code}"
    assert b"Please log in to access this page." in response_ticket.data

    # assert b"Aucun ticket disponible." in response_ticket.data

    

def test_full_purchase_flow(client, user):

    csrf_token = get_csrf_token(client)

    # Étape 1 : Se connecter
    response = client.post('auth/login', data={
        'email': 'test@gmail.com',
        'password': 'Sofiene1234@!',  # Le mot de passe en clair si ton test est en mode test
        'csrf_token': csrf_token  # Inclure le token CSR
    }, follow_redirects=True)
    # print(response.data)  # Ajoute ce débogage pour voir le contenu de la réponse
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"  # Assure-toi que l'utilisateur est redirigé
    html_auth = response.data.decode('utf-8')
    assert ' <h1 class="title-home">Bienvenue aux Jeux Olympiques de 2024 à Paris!</h1>' in html_auth # Assure-toi d'avoir un message de confirmation de connexion

    # Vérifier que l'utilisateur ne possede pas de ticket
    response_ticket = client.get('/ticket', data={'csrf_token': csrf_token}, follow_redirects=True)
    assert response_ticket.status_code == 200, f"Expected status code 200 but got {response_ticket.status_code}"
    assert b"Aucun ticket disponible." in response_ticket.data
    
    # Étape 2 : Ajouter un article au panier
    response_add_to_cart = client.post(f'/add_to_cart/1', data={'csrf_token': get_csrf_token(client)})
    assert response_add_to_cart.status_code == 200
    assert response_add_to_cart.get_json() == {'success': True, 'message': 'Offre ajoutée au panier !'}

    # Étape 3 : Récupérer et vérifier le panier
    response_panier = client.get('/panier')
    assert response_panier.status_code == 200
    assert b"solo" in response_panier.data  # Assure-toi que l'article ajouté apparaît bien

    # Étape 4 : Initier le paiement
    with patch('stripe.checkout.Session.create') as mock_create_session:
        mock_create_session.return_value.url = 'https://checkout.stripe.com/test_session'
        
        # Effectuer la requête de paiement
        response_purchase = client.get('/purchase')
        assert response_purchase.status_code in (302, 303)
        print("Purchase Response Headers:", response_purchase.headers)  # Affiche les headers pour le débogage
        assert response_purchase.headers['Location'] == 'https://checkout.stripe.com/test_session'

        # Étape 5 : Simuler le succès du paiement
        with patch('stripe.checkout.Session.retrieve') as mock_retrieve_session:
            mock_retrieve_session.return_value = {
                'id': 'test_session',
                'payment_status': 'paid'
            }
            
            response_success = client.get('/success?session_id=test_session')
            assert response_success.status_code == 200, f"Expected status code 200 but got {response_success.status_code}"
            print(response_success.data)
            assert b"We appreciate your business! If you have any questions, please email" in response_success.data
        
        # Vérifier que le ticket s'est bien enregistrer
        response_ticket_after = client.get('/ticket', data={'csrf_token': csrf_token}, follow_redirects=True)
        assert response_ticket_after.status_code == 200, f"Expected status code 200 but got {response_ticket.status_code}"
        html_ticket = response_ticket_after.data.decode('utf-8')
        ticket = Ticket.query.filter_by(user_id=5).all()
        assert len(ticket) == 1

        # Récupérer l'ID du ticket
        ticket_id = ticket[0].id  # Supposons que vous avez un seul ticket

        # Vérifier que la chaîne "QR Code Ticket" suivie de l'ID du ticket est présente dans la réponse HTML
        assert f"QR Code Ticket {ticket_id}" in html_ticket


