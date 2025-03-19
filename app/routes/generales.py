from ..app import app, db
from flask import render_template, request, jsonify
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from ..models.champiscope_db import Referentiel, Surface, Zone, Forme, Couleur, TypeLamelle, ModeInsertion, Milieu, Habitat, MoisPousse, DescriptionChampignon, ObservationHumaine

@app.route("/")
def accueil():
    return render_template("pages/index.html", sous_titre="Accueil")

@app.route('/recherche', methods=['GET', 'POST'])
@app.route('/recherche/<int:page>', methods=['GET', 'POST'])
def recherche(page=1):
    query = request.args.get('q', '')
    sort_order = request.args.get('sort', 'asc')  # 'asc' par défaut

    champignons_query = Referentiel.query.filter(
        Referentiel.rang == 'Espèce',
        Referentiel.est_reference == True
    )

    # Appliquer la recherche textuelle si présente
    if query:
        champignons_query = champignons_query.filter(
            db.or_(
                Referentiel.nom.ilike(f'%{query}%'),
                Referentiel.nom_complet.ilike(f'%{query}%'),
                Referentiel.nom_vernaculaire.ilike(f'%{query}%')
            )
        )

    # Appliquer le tri choisi par l'utilisateur
    if sort_order == 'desc':
        champignons_query = champignons_query.order_by(Referentiel.nom.desc())
    else:
        champignons_query = champignons_query.order_by(Referentiel.nom)

    nb_champi = champignons_query.count()
    champignons = champignons_query.paginate(page=page, per_page=app.config["CHAMPI_PAR_PAGE"])

    return render_template(
        'pages/recherche.html',
        pagination=champignons,
        nb_champi=nb_champi,
        query=query,
        sort_order=sort_order,  # Passer l'info à la template
        sous_titre="Recherche"
    )

@app.route('/api/observations_avec_synonymes/<int:taxref_id>')
def api_observations_avec_synonymes(taxref_id):
    # Récupérer l'espèce de référence
    espece_reference = Referentiel.query.get(taxref_id)
    if not espece_reference:
        return jsonify({})
    
    # Récupérer tous les synonymes (champignons ayant ce taxref_id comme référence)
    synonymes = Referentiel.query.filter_by(reference_id=taxref_id).all()
    
    # Préparer le dictionnaire de résultat
    resultat = {}
    
    # Ajouter l'espèce de référence
    observations_reference = ObservationHumaine.query.filter_by(taxref_id=taxref_id).all()
    observations_list = []
    for obs in observations_reference:
        observations_list.append({
            'id': obs.id,
            'latitude_decimale': obs.latitude_decimale,
            'longitude_decimale': obs.longitude_decimale,
            'jour': obs.jour,
            'mois': obs.mois,
            'annee': obs.annee,
            'identifie_par': obs.identifie_par
        })
    
    resultat[str(taxref_id)] = {
        'nom': espece_reference.nom_complet,
        'observations': observations_list
    }
    
    # Ajouter chaque synonyme
    for synonyme in synonymes:
        observations_synonyme = ObservationHumaine.query.filter_by(taxref_id=synonyme.taxref_id).all()
        observations_list = []
        for obs in observations_synonyme:
            observations_list.append({
                'id': obs.id,
                'latitude_decimale': obs.latitude_decimale,
                'longitude_decimale': obs.longitude_decimale,
                'jour': obs.jour,
                'mois': obs.mois,
                'annee': obs.annee,
                'identifie_par': obs.identifie_par
            })
        
        resultat[str(synonyme.taxref_id)] = {
            'nom': synonyme.nom_complet,
            'observations': observations_list
        }
    
    return jsonify(resultat)

@app.route("/carte_identite/<string:taxref>")
def champi(taxref):
    # Récupération des données de base
    #donnees = Referentiel.query.filter(Referentiel.taxref_id == taxref).first()
    donnees = Referentiel.query.get_or_404(taxref)
    
    nom_champi = donnees.nom
    
    return render_template("pages/carte_identite.html", 
        sous_titre = nom_champi, 
        donnees = donnees)

@app.route("/dataviz")
def dataviz():
    return render_template("pages/dataviz.html", sous_titre="Dataviz")

@app.route("/quiz/tous_les_quiz")
def quiz():
    return render_template("pages/quiz/tous_les_quiz.html", sous_titre="Tous les quiz")

@app.route("/profil")
def profil():
    return render_template("pages/profil.html", sous_titre="Mon profil")

@app.route("/connexion")
def connexion():
    return render_template("pages/connexion.html", sous_titre="Connexion")

@app.route("/a_propos")
def a_propos():
    return render_template("pages/a_propos.html", sous_titre="A propos")

@app.route("/mentions_legales")
def mentions_legales():
    return render_template("pages/mentions_legales.html", sous_titre="Mentions Légales")

@app.route("/remerciements")
def remerciements():
    return render_template("pages/remerciements.html", sous_titre="Remerciements")