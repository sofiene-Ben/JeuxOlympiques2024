import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a0f885fbd4ff1cf0f8a4139ed39edbfb12bcaa34d31a')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root@localhost:3306/olympic')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SALT = os.getenv('SALT', 'uvbciyfvbciydbw64375463hdschsdj')

    # Configuration de Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True  # Assurez-vous que c'est True
    MAIL_USE_SSL = False  # Assurez-vous que c'est False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'olympic.studi@gmail.com')