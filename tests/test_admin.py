import pytest
from app import create_app, db
import re
from app.models import User, Ticket, Offer
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
        existing_user = User.query.filter_by(email='admin@example.com').first()
        if existing_user:
            return existing_user  # Retourne l'utilisateur existant
        
        hashed_pw = generate_password_hash('AdminPassword123@') # Hachage du mot de passe
        user = User(
            email='admin@example.com',
            password_hash=hashed_pw,
            firstname='Admin',
            lastname='User',
            is_admin=True,
            is_staff=True,
            )  
        db.session.add(user)
        db.session.commit()
        return user
    

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
    
def login(client, email, password):
    csrf_token = get_csrf_token(client)  # Obtenir le token CSRF

    response = client.post('/auth/login', data={
        'email': email,
        'password': password,
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Vérifier que la connexion a réussi
    assert response.status_code == 200, f"Login failed with status code: {response.status_code}"

    return response

def test_dasboard(client, user):

    # Étape 1 : Se connecter
    login(client, 'admin@example.com', 'AdminPassword123@')

    response_dashboard = client.get('/admin/dashboard')
    assert response_dashboard.status_code == 200, f"Expected status code 200 but got {response_dashboard.status_code}"
    # html_dashboard = response_dashboard.data.decode('utf-8')
    # assert '<h1>Tableau de bord</h1>' in html_dashboard

    # Récupérer tous les tickets de la base de données
    tickets = Ticket.query.all()

    # Vérifier que le nombre de tickets dans la base de données correspond à celui affiché
    for ticket in tickets:
        assert f"{ticket.id}" in response_dashboard.data.decode('utf-8'), f"Ticket {ticket.id} not found in dashboard"

    # Vérifier les e-mails des propriétaires et les dates de création
    for ticket in tickets:
        assert ticket.owner.email in response_dashboard.data.decode('utf-8'), f"Owner email for ticket {ticket.id} not found in dashboard"
        assert str(ticket.created_at) in response_dashboard.data.decode('utf-8'), f"Creation date for ticket {ticket.id} not found in dashboard"





def test_manage_offers(client):

     # Étape 1 : Se connecter
    login(client, 'admin@example.com', 'AdminPassword123@')

    response_manage_offer = client.get('/admin/admin/manage_offers')
    
    assert response_manage_offer.status_code == 200, f"Expected status code 200 but got {response_manage_offer.status_code}"

    # Étape 2 : Récupérer toutes les offres de la base de données
    offers = Offer.query.all()

    # Vérifier que chaque offre de la base de données est présente dans la réponse
    for offer in offers:
        assert f"{offer.id}" in response_manage_offer.data.decode('utf-8'), f"Offer {offer.id} not found in manage offers page"
        assert offer.name in response_manage_offer.data.decode('utf-8'), f"Offer name '{offer.name}' not found in manage offers page"
        # assert offer.description in response_manage_offer.data.decode('utf-8'), f"Offer description '{offer.description}' not found in manage offers page"
        assert str(offer.price) in response_manage_offer.data.decode('utf-8'), f"Offer price '{offer.price}' not found in manage offers page"
        assert offer.stripe_price_id in response_manage_offer.data.decode('utf-8'), f"Stripe price ID '{offer.stripe_price_id}' not found in manage offers page"


def test_create_update_delete_offer(client):

    csrf_token = get_csrf_token(client)  # Obtenir le token CSRF

    # Étape 1 : Se connecter
    login(client, 'admin@example.com', 'AdminPassword123@')

    # Étape 2 : Accéder à la page de gestion des offres
    response_manage_offer = client.get('/admin/admin/create_offer')
    assert response_manage_offer.status_code == 200, f"Expected status code 200 but got {response_manage_offer.status_code}"

    # Étape 3 : Ajouter une nouvelle offre
    new_offer_data = {
        'name': 'offre_test',
        'description': 'Ceci est une description de test pour une nouvelle offre.',
        'price': '99.99',
        'stock': 12,
        'stripe_price_id': 'price_test_12345',
        'csrf_token': get_csrf_token(client)  # Obtenez le token CSRF
    }
    response_add_offer = client.post('/admin/admin/create_offer', data=new_offer_data, follow_redirects=True)

    # Vérifier que la création de l'offre a réussi
    assert response_add_offer.status_code == 200, f"Expected status code 200 but got {response_add_offer.status_code}"
    print(response_add_offer.data)
    assert b'Gestion des offres' in response_add_offer.data, "Offer creation flash message not found."

    # Étape 4 : Vérifier que l'offre a été ajoutée en consultant la base de données
    added_offer = Offer.query.filter_by(name='offre_test').first()
    assert added_offer is not None, "Offer was not added to the database"
    assert added_offer.description == 'Ceci est une description de test pour une nouvelle offre.'
    assert str(added_offer.price) == '99.99'
    assert added_offer.stripe_price_id == 'price_test_12345'

    # Étape 5 : Vérifier que la nouvelle offre est visible sur la page de gestion des offres
    response_after_add = client.get('/admin/admin/manage_offers')
    assert response_after_add.status_code == 200, f"Expected status code 200 but got {response_after_add.status_code}"
    assert 'offre_test' in response_after_add.data.decode('utf-8'), "New offer name not found on the manage offers page"
    assert '99.99' in response_after_add.data.decode('utf-8'), "New offer price not found on the manage offers page"

# Modif offre------------------

    # Étape 4 : Accéder à la page de modification de l'offre
    edit_url = f'/admin/edit_offer/{added_offer.id}'
    response_edit_offer_page = client.get(edit_url)
    assert response_edit_offer_page.status_code == 200, f"Expected status code 200 but got {response_edit_offer_page.status_code}"
    
    # Étape 5 : Modifier les informations de l'offre
    updated_offer_data = {
        'name': 'offre_test_modifiee',
        'description': 'Ceci est une description modifiée.',
        'price': '149.99',
        'stock': 10,
        'stripe_price_id': 'price_test_54321',
        'csrf_token': get_csrf_token(client)  # Obtenez le token CSRF
    }
    response_edit_offer = client.post(edit_url, data=updated_offer_data, follow_redirects=True)
    assert response_edit_offer.status_code == 200, f"Expected status code 200 but got {response_edit_offer.status_code}"
    assert b'Gestion des offres' in response_edit_offer.data, "Offer modification flash message not found."

    # Étape 6 : Vérifier que les modifications sont reflétées dans la base de données
    modified_offer = Offer.query.get(added_offer.id)
    assert modified_offer.name == 'offre_test_modifiee', "Offer name was not updated in the database"
    assert modified_offer.description == 'Ceci est une description modifiée.', "Offer description was not updated in the database"
    assert str(modified_offer.price) == '149.99', "Offer price was not updated in the database"
    assert modified_offer.stripe_price_id == 'price_test_54321', "Stripe price ID was not updated in the database"
    assert modified_offer.stock == 10, "Offer stock was not updated in the database"

    # Étape 7 : Vérifier que l'offre modifiée est visible sur la page de gestion des offres
    response_after_edit = client.get('/admin/admin/manage_offers')
    assert response_after_edit.status_code == 200, f"Expected status code 200 but got {response_after_edit.status_code}"
    assert 'offre_test_modifiee' in response_after_edit.data.decode('utf-8'), "Updated offer name not found on the manage offers page"
    assert '149.99' in response_after_edit.data.decode('utf-8'), "Updated offer price not found on the manage offers page"

    # Delete offer------------ 

    # Étape 5 : Supprimer l'offre
    delete_url = f'/admin/delete_offer/{added_offer.id}'
    response_delete_offer = client.post(delete_url, data={'csrf_token': csrf_token}, follow_redirects=True)
    assert response_delete_offer.status_code == 200, f"Expected status code 200 but got {response_delete_offer.status_code}"
    assert b'Gestion des offres' in response_delete_offer.data, "Offer deletion flash message not found."

    # Étape 6 : Vérifier que l'offre a été supprimée de la base de données
    deleted_offer = Offer.query.filter_by(name='offre_test_modifiee').first()
    assert deleted_offer is None, "Offer was not deleted from the database"

    # Étape 7 : Vérifier que l'offre n'est plus visible sur la page de gestion des offres
    response_after_delete = client.get('/admin/admin/manage_offers')
    assert response_after_delete.status_code == 200, f"Expected status code 200 but got {response_after_delete.status_code}"
    assert 'offre_test_modifiee' not in response_after_delete.data.decode('utf-8'), "Deleted offer name still found on the manage offers page"




def test_manage_users(client):

     # Étape 1 : Se connecter
    login(client, 'admin@example.com', 'AdminPassword123@')

    #  user
    response_users = client.get('/admin/users')
    assert response_users.status_code == 200, f"Expected status code 200 but got {response_users.status_code}"

    # Récupérer tous les utilisateurs de la base de données
    users = User.query.all()

    # Vérifier que chaque adresse e-mail est présente dans la réponse
    for user in users:
        assert user.email in response_users.data.decode('utf-8'), f"Email '{user.email}' not found in users page"



def test_edit_user(client):

    csrf_token = get_csrf_token(client)  # Obtenir le token CSRF

    # Étape 1 : Se connecter en tant qu'administrateur
    login(client, 'admin@example.com', 'AdminPassword123@')

    # Étape 2 : Récupérer l'utilisateur ayant l'ID 2
    test_user = User.query.get(2)
    assert test_user is not None, "L'utilisateur avec l'ID 2 n'existe pas dans la base de données."

    # Étape 3 : Accéder à la page de modification de l'utilisateur (méthode GET)
    edit_url = f'/admin/edit_user/{test_user.id}'
    response_get = client.get(edit_url)
    assert response_get.status_code == 200, f"Expected status code 200 but got {response_get.status_code}"
    assert f"Modifier l'utilisateur {test_user.firstname} {test_user.lastname}" in response_get.data.decode('utf-8'), "Edit user form not found on the page with the expected user name"

    # Étape 4 : Modifier les informations de l'utilisateur (méthode POST)
    updated_user_data = {
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'jane.smith@example.com',
        'is_staff': True,
        'csrf_token': csrf_token # Obtenez le token CSRF
    }
    response_post = client.post(edit_url, data=updated_user_data, follow_redirects=True)

    # Vérifier que la modification a réussi
    assert response_post.status_code == 200, f"Expected status code 200 but got {response_post.status_code}"
    assert b'Liste des utilisateurs' in response_post.data, "Success flash message not found"

    # Étape 5 : Vérifier que les modifications sont appliquées en base de données
    modified_user = User.query.get(test_user.id)
    assert modified_user.firstname == 'Jane', "User's first name was not updated in the database"
    assert modified_user.lastname == 'Smith', "User's last name was not updated in the database"
    assert modified_user.email == 'jane.smith@example.com', "User's email was not updated in the database"
    assert modified_user.is_staff is True, "User's staff status was not updated in the database"

    # Étape 6 : Vérifier que l'utilisateur modifié est visible sur la page de gestion des utilisateurs
    response_after_edit = client.get('/admin/users')
    assert response_after_edit.status_code == 200, f"Expected status code 200 but got {response_after_edit.status_code}"
    assert 'Jane' in response_after_edit.data.decode('utf-8'), "Updated user first name not found on the manage users page"
    assert 'Smith' in response_after_edit.data.decode('utf-8'), "Updated user last name not found on the manage users page"


def test_init_edit_user(client):

    csrf_token = get_csrf_token(client)  # Obtenir le token CSRF

    # Étape 1 : Se connecter en tant qu'administrateur
    login(client, 'admin@example.com', 'AdminPassword123@')

    # Étape 2 : Récupérer l'utilisateur ayant l'ID 2
    test_user = User.query.get(2)
    assert test_user is not None, "L'utilisateur avec l'ID 2 n'existe pas dans la base de données."

    # Étape 3 : Accéder à la page de modification de l'utilisateur (méthode GET)
    edit_url = f'/admin/edit_user/{test_user.id}'
    response_get = client.get(edit_url)
    assert response_get.status_code == 200, f"Expected status code 200 but got {response_get.status_code}"
    assert f"Modifier l'utilisateur {test_user.firstname} {test_user.lastname}" in response_get.data.decode('utf-8'), "Edit user form not found on the page with the expected user name"

    # Étape 4 : Modifier les informations de l'utilisateur (méthode POST)
    updated_user_data = {
        'firstname': 'Sofiene',
        'lastname': 'Ben',
        'email': 'sofiene@gmail.com',
        'is_staff': '',
        'csrf_token': csrf_token # Obtenez le token CSRF
    }
    response_post = client.post(edit_url, data=updated_user_data, follow_redirects=True)

    # Vérifier que la modification a réussi
    assert response_post.status_code == 200, f"Expected status code 200 but got {response_post.status_code}"
    assert b'Liste des utilisateurs' in response_post.data, "Success flash message not found"

    # Étape 5 : Vérifier que les modifications sont appliquées en base de données
    modified_user = User.query.get(test_user.id)
    assert modified_user.firstname == 'Sofiene', "User's first name was not updated in the database"
    assert modified_user.lastname == 'Ben', "User's last name was not updated in the database"
    assert modified_user.email == 'sofiene@gmail.com', "User's email was not updated in the database"
    assert modified_user.is_staff is False, "User's staff status was not updated in the database"

    # Étape 6 : Vérifier que l'utilisateur modifié est visible sur la page de gestion des utilisateurs
    response_after_edit = client.get('/admin/users')
    assert response_after_edit.status_code == 200, f"Expected status code 200 but got {response_after_edit.status_code}"
    assert 'Sofiene' in response_after_edit.data.decode('utf-8'), "Updated user first name not found on the manage users page"
    assert 'Ben' in response_after_edit.data.decode('utf-8'), "Updated user last name not found on the manage users page"



