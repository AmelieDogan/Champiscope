from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

db = SQLAlchemy(app) # Initialisation de la base de données

login = LoginManager(app) # Initialiser le loginmanager de sqlalchemy
csrf = CSRFProtect(app)  # Activer la protection CSRF

from .routes import generales, quiz, connexion, dataviz