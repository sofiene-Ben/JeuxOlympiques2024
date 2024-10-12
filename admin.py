from app import db, create_app
from app.models import User
import uuid

# Créer une instance de l'application
app = create_app()

with app.app_context():
    # Vérifier si un administrateur existe déjà
    admin = User.query.filter_by(email="admin@example.com").first()
    
    if not admin:
        # Créer un nouvel administrateur
        admin = User(
            firstname="Admin",
            lastname="User",
            email="admin@example.com",
            key=uuid.uuid4().hex,
            is_admin=True  # Définir l'utilisateur comme administrateur
        )
        admin.set_password("AdminPassword123")
        db.session.add(admin)
        db.session.commit()
        print("Administrateur créé avec succès.")
    else:
        print("Administrateur déjà existant.")
