from ..app import app, db
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from ..models.users import User
from ..models.formulaires import AjoutUtilisateur, Connexion
from flask_login import login_user, current_user, logout_user

@app.route("/utilisateur/inscription", methods=["GET", "POST"])
def ajout_utilisateur():

    form = AjoutUtilisateur()

    if form.validate_on_submit():
        print("Données reçues :", request.form)
        statut, donnees = User.ajout(
            pseudo=(request.form.get("pseudo", None)),
            password=(request.form.get("password", None)),
            mail=request.form.get("mail", None)
        )
        if statut is True:
            flash("Ajout effectué", "success")
            return redirect(url_for("connexion"))
        else:
            flash(",".join(donnees), "error")
            return render_template("pages/utilisateur/ajout_utilisateur.html", form=form)
    else:
        return render_template("pages/utilisateur/ajout_utilisateur.html", form=form)

@app.route("/utilisateur/connexion", methods= ["GET", "POST"])
#@staticmethod
def connexion():

    form = Connexion()

    if current_user.is_authenticated is True:
            flash("Vous êtes déjà connecté", "info")
            return redirect(url_for("accueil"))

    if form.validate_on_submit():
        utilisateur = User.identification(
        pseudo=(request.form.get("pseudo", None)),
        password=(request.form.get("password", None))
            )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect(url_for("accueil"))
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")
            return render_template("pages/utilisateur/connexion.html", form=form)

    else:
            return render_template("pages/utilisateur/connexion.html", form=form)
    
@app.route("/utilisateur/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté", "info")
    return redirect(url_for("accueil"))

#login.login_view = 'connexion'