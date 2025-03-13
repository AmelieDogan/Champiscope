from ..app import app
from flask import render_template
from sqlalchemy import text
from ..models.champiscope_db import Referentiel

@app.route("/")
def accueil():
    return render_template("pages/index.html")

@app.route("/recherche.html")
def recherche():
    donnees = []
    for champi in Referentiel.query.all():
        donnees.append({
            "nom": champi.nom,
            "nom_vernaculaire": champi.nom_vernaculaire,
        })
    return render_template("pages/recherche.html", donnees=donnees, sous_titre="Tous les champignons")

@app.route("/dataviz.html")
def dataviz():
    return render_template("pages/dataviz.html")

@app.route("/quiz.html")
def quiz():
    return render_template("pages/quiz.html")

@app.route("/profil.html")
def profil():
    return render_template("pages/profil.html")

@app.route("/connexion.html")
def connexion():
    return render_template("pages/connexion.html")

@app.route("/a_propos.html")
def a_propos():
    return render_template("pages/a_propos.html")

@app.route("/mention_legale.html")
def mention_legale():
    return render_template("pages/mention_legale.html")

@app.route("/remerciements.html")
def remerciements():
    return render_template("pages/remerciements.html")