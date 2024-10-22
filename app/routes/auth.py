from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User, db
from flask_login import login_user, logout_user, login_required
from app.forms import RegistrationForm, LoginForm
# from wtforms import StringField, PasswordField, SubmitField
# from werkzeug.security import generate_password_hash
# import os
import uuid
# from flask_wtf import FlaskForm
# from wtforms.validators import DataRequired, Email, Length
import time 
auth_bp = Blueprint('auth', __name__)





@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if not form.accept_terms.data:
            flash("Vous devez accepter les conditions d'utilisation pour continuer.", 'danger')
            return redirect(url_for('auth.register'))
        
        print("Formulaire validé")  # Débogage
        user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            key=uuid.uuid4().hex
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            print('Votre compte a été créé ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'ajout de l'utilisateur: {e}")  # Débogage
            print('Une erreur est survenue. Veuillez réessayer.', 'danger')
    else:
        print("Validation échouée")  # Débogage
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erreur dans le champ '{field}': {error}")  # Débogage
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        time.sleep(2)
        print("Formulaire de connexion validé")  # Débogage
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print(f"Utilisateur trouvé : {user.email}")  # Débogage
            if user.check_password(form.password.data):
                login_user(user)
                flash('Connexion réussie !', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Mot de passe ou Adresse e-mail incorrect.', 'danger')
        else:
            flash('Mot de passe ou Adresse e-mail incorrect.', 'danger')
    else:
        form.email.data = request.form.get('email')
        print("Validation échouée lors de la connexion")  # Débogage
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erreur dans le champ '{field}': {error}")  # Débogage
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('auth.login'))
