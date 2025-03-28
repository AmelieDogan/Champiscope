from ..app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..models.champiscope_db import Referentiel, user_likes

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(250))
    mail = db.Column(db.String(25), unique=True)
    profile_image = db.Column(db.String(120), default="champi_1.jpg") 
    #Relation avec user_likes
    likes = db.relationship('Referentiel', secondary=user_likes, backref=db.backref('user_likers', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % (self.id)
    
    @staticmethod
    def ajout(pseudo, password, mail): # Ajouter un nouvel utilisateur
        erreurs = []
        print(f"Vérification des données : {pseudo}, {password},{mail}")
        if not pseudo:
            erreurs.append("Le prénom est vide")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court")
        if not mail:
            erreurs.append("Le mail est vide")

        unique = User.query.filter(db.or_(User.pseudo == pseudo)).count()
        if unique > 0:
            erreurs.append("Le pseudo existe déjà")
        if len(erreurs):
            return False, erreurs
        

        utilisateur = User(pseudo=pseudo, password=generate_password_hash(password), mail=mail)

        try:
            db.session.add(utilisateur)
            db.session.commit()
            return True, utilisateur
        except Exception as erreur:
            db.session.rollback()  # Annuler la transaction en cas d'erreur
            print(f"Erreur SQL lors de l'insertion de l'utilisateur : {erreur}")
            return False, [f"Erreur lors de l'insertion : {erreur}"]
        
    def get_id(self):
        return self.id
    
    @login.user_loader
    def get_user_by_id(id):
        return User.query.get(int(id))
    
    @staticmethod
    def identification(pseudo, password): # Identifier l'utilisateur via son pseudo et son mot de passe
        utilisateur = User.query.filter(User.pseudo == pseudo).first()
        if not utilisateur:
            print("Utilisateur introuvable")
            return None
        if not check_password_hash(utilisateur.password, password):
            print("Mot de passe incorrect")
            return None
        print(f"Utilisateur authentifié : {utilisateur.pseudo}")
        return utilisateur
