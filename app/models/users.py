from ..app import app, db, login
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..models.champiscope_db import Referentiel

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(250))
    mail = db.Column(db.String(25), unique=True)
    profile_image = db.Column(db.String(120), default="champi_1.jpg")
    champi_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'))

    quiz_comestible_scores = db.relationship("ScoreQuizComestible", backref="quiz_comestibles_scores", lazy=True)

    liked = db.relationship(
        'UserLikes',
        foreign_keys='UserLikes.user_id',
        backref='users', lazy='dynamic')

    def like_champi(self, champi):
        if not self.has_liked_champi(champi):
            like = UserLikes(user_id=self.id, champi_id=champi.taxref_id)
            db.session.add(like)

    def unlike_champi(self, champi):
        if self.has_liked_champi(champi):
            UserLikes.query.filter_by(
                user_id=self.id,
                champi_id=champi.taxref_id).delete()

    def has_liked_champi(self, champi):
        return UserLikes.query.filter(
            UserLikes.user_id == self.id,
            UserLikes.champi_id == champi.taxref_id).count() > 0
    
    def get_liked_champi_objects(self):
        return Referentiel.query.filter(Referentiel.taxref_id.in_([like.champi_id for like in self.liked])).all()
    
    def enregistrer_score(self, score):
        score_quiz = ScoreQuizComestible(user_id=self.id, score=score)
        db.session.add(score_quiz)
    
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
    
class ScoreQuizComestible(db.Model):
    __tablename__ = "score_quiz_comestible"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Float)
    date_quiz = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return '<User %r>' % (self.id)

class UserLikes(db.Model):
    __tablename__ = 'user_likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    champi_id = db.Column(db.Integer, db.ForeignKey('referentiel.taxref_id'), primary_key=True)

    def __repr__(self):
        return '<User %r>' % (self.id)