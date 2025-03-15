from ..app import app
from flask import render_template
from sqlalchemy import text
from ..models.champiscope_db import Referentiel, DescriptionChampignon, Presence, Habitat

@app.route("/")
def accueil():
    return render_template("pages/index.html", sous_titre="Accueil")

@app.route("/carte_identite/<string:taxref>")
def champi(taxref):
    donnees_referentiel = Referentiel.query.filter(Referentiel.taxref_id == taxref).first()
    donnees_description = DescriptionChampignon.query.filter(DescriptionChampignon.taxref_id == taxref).first()
    donnees_presence = Presence.query.filter(Presence.taxref_id == taxref).first()
    nom_champi = donnees_referentiel.nom
    return render_template("pages/carte_identite.html", 
        sous_titre = nom_champi, 
        donnees_referentiel = donnees_referentiel,
        donnees_description = donnees_description,
        donnees_presence = donnees_presence)

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
    return render_template("pages/dataviz.html", sous_titre="Dataviz")

@app.route("/quiz/tous_les_quiz.html")
def quiz():
    return render_template("pages/quiz/tous_les_quiz.html", sous_titre="Tous les quiz")

@app.route("/utilisateur/profil.html")
def profil():
    return render_template("pages/utilisateur/profil.html", sous_titre="Mon profil")

@app.route("/a_propos.html")
def a_propos():
    return render_template("pages/a_propos.html", sous_titre="A propos")

@app.route("/mentions_legales.html")
def mentions_legales():
    return render_template("pages/mentions_legales.html", sous_titre="Mentions Légales")

@app.route("/remerciements.html")
def remerciements():
    return render_template("pages/remerciements.html", sous_titre="Remerciements")