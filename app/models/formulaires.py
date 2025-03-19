from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, PasswordField

class AjoutUtilisateur(FlaskForm):
    pseudo = StringField("pseudo")
    password = PasswordField("mot de passe")
    mail = StringField("mail")

class Connexion(FlaskForm):
    pseudo = StringField("pseudo")
    password = PasswordField("mot de passe")
    #mail = StringField("mail")