from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import bcrypt

# app/models.py
from app import db
from flask_login import UserMixin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from flask import current_app


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    key = db.Column(db.String(128), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    is_admin = db.Column(db.Boolean, default=False)  # Champ pour administrateurs
    is_staff = db.Column(db.Boolean, default=False)  # Champ pour employer
    tickets = db.relationship('Ticket', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
    
    # def get_reset_password_token(self, expires_in=600):
    #     print(type(current_app.config['SECRET_KEY']))  # Debugging line
    #     print(f"user_id: {self.id}, type: {type(self.id)}")  # Debugging line

    #     s = Serializer(current_app.config['SECRET_KEY'], expires_in)
    #     # s = Serializer(secret_key, expires_in)
    #     return s.dumps({'user_id': self.id})
    
    def get_reset_password_token(self, expires_sec=600):
        s = Serializer(current_app.config['SECRET_KEY'])  # Utilisez current_app
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])  # Utilisez current_app
        try:
            data = s.loads(token, salt='password-reset-salt')
        except Exception as e:
            return None  # Retournez None si le token est invalide ou a expiré
        return User.query.get(data['user_id'])


    


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    stripe_price_id = db.Column(db.String(64), nullable=False)
    # type_id = db.Column(db.Integer, db.ForeignKey('offer_type.id'), nullable=False)
    # type = db.Column(db.Enum('solo', 'duo', 'familiale', name='offer_types'), nullable=False)
    tickets = db.relationship('Ticket', backref='offer', lazy='dynamic')


# class OfferType(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     type = db.Column(db.String(25), nullable=False)
#     price = db.Column(db.Float, nullable=False)
#     offers = db.relationship('Offer', backref='offer_type', lazy='dynamic')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='Pending')
    key1 = db.Column(db.String(64), nullable=False)
    key2 = db.Column(db.String(64), nullable=False)
    final_key = db.Column(db.String(128), nullable=False)
    qr_code = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))