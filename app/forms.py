from flask_wtf import FlaskForm
from wtforms import StringField,DecimalField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User



class RegistrationForm(FlaskForm):
    firstname = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=64)])
    lastname = StringField('Nom', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8),
        # Ajoutez d'autres validateurs si nécessaire
    ])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre.')
    ])
    submit = SubmitField('S\'inscrire')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà enregistré.')



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
    submit = SubmitField('Create Offer')

class OfferEditForm(FlaskForm):
    name = StringField('Nom de l\'offre', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    # type = SelectField('Type', choices=[('type1', 'Type 1'), ('type2', 'Type 2')], validators=[DataRequired()])
    submit = SubmitField('Create Offer')
class UserEditForm(FlaskForm):
    firstname = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=64)])
    lastname = StringField('Nom', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Adresse e-mail', validators=[DataRequired(), Email(), Length(max=120)])
    is_admin = BooleanField('Administrateur')
    submit = SubmitField('Mettre à jour')    


