from flask_wtf import FlaskForm
from wtforms import StringField,DecimalField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models import User
from flask_login import current_user
# from app.models import OfferType



class RegistrationForm(FlaskForm):
    firstname = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=64)])
    lastname = StringField('Nom', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$',
            message=("Le mot de passe doit contenir au moins : une lettre majuscule, "
                     "une lettre minuscule, un chiffre, et un caractère spécial.")
        ),
        # Ajoutez d'autres validateurs si nécessaire
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre.')
    ])
    accept_terms = BooleanField('J\'accepte les Conditions d\'utilisation', validators=[])
    submit = SubmitField('S\'inscrire')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà enregistré.')

class UpdateProfileForm(FlaskForm):
    firstname = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=64)])
    lastname = StringField('Nom', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Enregistrer')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Cet email est déjà enregistré.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$',
            message=("Le mot de passe doit contenir au moins : une lettre majuscule, "
                     "une lettre minuscule, un chiffre, et un caractère spécial.")
        ),
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('new_password', message='Les mots de passe doivent correspondre.')
    ])
    submit = SubmitField('Changer mot de passe')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Réinitialiser le mot de passe')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères.')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('new_password', message='Les mots de passe doivent correspondre.')
    ])
    submit = SubmitField('Réinitialiser le mot de passe')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class AdminLoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=2, max=64)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class OfferForm(FlaskForm):
    name = StringField('Nom de l\'offre', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    # type = SelectField('Type', choices=[('type1', 'Type 1'), ('type2', 'Type 2')], validators=[DataRequired()])
    # offer_type = SelectField('Type', choices=[], validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    stripe_price_id = StringField('Stripe Price ID', validators=[DataRequired()])
    submit = SubmitField('Create Offer')

    # def __init__(self, *args, **kwargs):
    #     super(OfferForm, self).__init__(*args, **kwargs)
    #     # Récupère les types depuis la base de données pour les offrir comme choix
    #     self.offer_type.choices = [(str(o.id), o.type) for o in OfferType.query.all()]

class OfferEditForm(FlaskForm):
    name = StringField('Nom de l\'offre', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    # type = SelectField('Type', choices=[('type1', 'Type 1'), ('type2', 'Type 2')], validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired()])
    stripe_price_id = StringField('Stripe Price ID', validators=[DataRequired()])
    submit = SubmitField('Create Offer')
class UserEditForm(FlaskForm):
    firstname = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=64)])
    lastname = StringField('Nom', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email(), Length(max=120)])
    is_staff = BooleanField('Staff')
    submit = SubmitField('Mettre à jour')    


