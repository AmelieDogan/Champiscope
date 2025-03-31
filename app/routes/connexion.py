from ..app import app, db
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from ..models.users import User
from ..models.formulaires import AjoutUtilisateur, Connexion
from flask_login import login_user, current_user, logout_user

@app.route("/utilisateur/inscription", methods=["GET", "POST"])
def ajout_utilisateur(): # Ajouter un utilisateur

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
            return redirect(url_for("connexion")) # Rediriger vers connexion une fois l'utilisateur créé
        else:
            flash(",".join(donnees), "error")
            return render_template("pages/utilisateur/ajout_utilisateur.html", form=form) # Rediriger vers page ajout utilisateur si cela n'a pas fonctionné
    else:
        return render_template("pages/utilisateur/ajout_utilisateur.html", sous_titre="Inscription", form=form)

@app.route("/utilisateur/connexion", methods=["GET", "POST"])
def connexion():
    form = Connexion()

    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté", "info")
        return redirect(url_for("accueil"))

    if request.method == "POST":
        if form.validate_on_submit():  # Vérifie la validation du formulaire
            utilisateur = User.identification(
                pseudo=request.form.get("pseudo"),
                password=request.form.get("password")
            )

            if utilisateur:
                flash("Connexion effectuée", "success")
                login_user(utilisateur)
                return redirect(url_for("accueil"))
            else:
                flash("Les identifiants n'ont pas été reconnus", "danger") 

        else:
            flash("Erreur de validation du formulaire", "warning")

    return render_template("pages/utilisateur/connexion.html", sous_titre="Connexion", form=form)  # Toujours renvoyer vers la page connexion

    
@app.route("/utilisateur/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté", "info")
    return redirect(url_for("accueil"))
