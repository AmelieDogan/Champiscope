from ..app import app, db
from flask import render_template, request, jsonify
from ..models.champiscope_db import Referentiel, Surface, Zone, Forme, Couleur, TypeLamelle, ModeInsertion, Milieu, Habitat, MoisPousse, DescriptionChampignon, ObservationHumaine

@app.route("/")
def accueil():
    # Calculer le nombre total d'espèces
    nombre_especes = Referentiel.query.count()
    
    # Calculer le nombre total d'observations
    nombre_observations = ObservationHumaine.query.count()
    
    return render_template(
        'pages/index.html', 
        sous_titre='Accueil',
        nombre_especes=nombre_especes,
        nombre_observations=nombre_observations,
    )

@app.route('/recherche', methods=['GET', 'POST'])
@app.route('/recherche/<int:page>', methods=['GET', 'POST'])
def recherche(page=1):
    # Récupération des paramètres de base
    query = request.args.get('q', '')
    sort_order = request.args.get('sort', 'asc')
    
    # Récupération des filtres
    selected_couleurs = request.args.getlist('couleur')
    selected_formes = request.args.getlist('forme')
    selected_lamelles = request.args.getlist('lamelle')
    selected_milieux = request.args.getlist('milieu')
    selected_mois = request.args.getlist('mois')
    comestible = request.args.get('comestible', '')
    
    # Construction de la requête de base
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
    
    # Appliquer les filtres    
    if selected_couleurs:
        champignons_query = champignons_query.join(
            Couleur, Referentiel.couleurs_associées
        ).filter(Couleur.id.in_(selected_couleurs))
    
    if selected_formes:
        champignons_query = champignons_query.join(
            Forme, Referentiel.formes_associées
        ).filter(Forme.id.in_(selected_formes))
    
    if selected_lamelles:
        champignons_query = champignons_query.join(
            TypeLamelle, Referentiel.types_lamelle_associés
        ).filter(TypeLamelle.id.in_(selected_lamelles))
    
    if selected_milieux:
        champignons_query = champignons_query.join(
            Milieu, Referentiel.milieux_associés
        ).filter(Milieu.id.in_(selected_milieux))
    
    if selected_mois:
        mois_filter_conditions = []
        mois_mapping = {
            '1': 'janvier', '2': 'fevrier', '3': 'mars', '4': 'avril',
            '5': 'mai', '6': 'juin', '7': 'juillet', '8': 'aout',
            '9': 'septembre', '10': 'octobre', '11': 'novembre', '12': 'decembre'
        }
        
        champignons_query = champignons_query.join(MoisPousse)
        
        for mois_id in selected_mois:
            if mois_id in mois_mapping:
                mois_column = getattr(MoisPousse, mois_mapping[mois_id])
                mois_filter_conditions.append(mois_column == True)
        
        if mois_filter_conditions:
            champignons_query = champignons_query.filter(db.or_(*mois_filter_conditions))
    
    if comestible:
        champignons_query = champignons_query.join(DescriptionChampignon)
        is_comestible = comestible.lower() == 'true'
        champignons_query = champignons_query.filter(DescriptionChampignon.comestibilite == is_comestible)
    
    # Appliquer le tri
    if sort_order == 'desc':
        champignons_query = champignons_query.order_by(Referentiel.nom.desc())
    else:
        champignons_query = champignons_query.order_by(Referentiel.nom)
    
    # Éliminer les doublons potentiels dus aux jointures multiples
    champignons_query = champignons_query.distinct()
    
    # Obtenir le nombre total de champignons correspondant aux critères
    nb_champi = champignons_query.count()
    
    # Paginer les résultats
    champignons = champignons_query.paginate(page=page, per_page=app.config["CHAMPI_PAR_PAGE"])
    
    # Récupérer toutes les options de filtres pour l'affichage
    couleurs = Couleur.query.order_by(Couleur.couleur).all()
    formes = Forme.query.order_by(Forme.forme).all()
    types_lamelle = TypeLamelle.query.order_by(TypeLamelle.type_lamelle).all()
    milieux = Milieu.query.order_by(Milieu.milieu).all()
    
    # Liste des mois pour le filtre saisonnier
    mois_liste = [
        {'id': '1', 'nom': 'Janvier'}, {'id': '2', 'nom': 'Février'}, 
        {'id': '3', 'nom': 'Mars'}, {'id': '4', 'nom': 'Avril'},
        {'id': '5', 'nom': 'Mai'}, {'id': '6', 'nom': 'Juin'},
        {'id': '7', 'nom': 'Juillet'}, {'id': '8', 'nom': 'Août'},
        {'id': '9', 'nom': 'Septembre'}, {'id': '10', 'nom': 'Octobre'},
        {'id': '11', 'nom': 'Novembre'}, {'id': '12', 'nom': 'Décembre'}
    ]
    
    # Enregistrer les filtres sélectionnés pour le template
    selected_filters = {
        'couleurs': selected_couleurs,
        'formes': selected_formes,
        'lamelles': selected_lamelles,
        'milieux': selected_milieux,
        'mois': selected_mois,
        'comestible': comestible
    }
    
    return render_template(
        'pages/recherche.html',
        pagination=champignons,
        nb_champi=nb_champi,
        query=query,
        sort_order=sort_order,
        couleurs=couleurs,
        formes=formes,
        types_lamelle=types_lamelle,
        milieux=milieux,
        mois_liste=mois_liste,
        selected_filters=selected_filters,
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

    donnees = Referentiel.query.get_or_404(taxref)
    
    nom_champi = donnees.nom
    
    return render_template("pages/carte_identite.html", 
        sous_titre = nom_champi, 
        donnees = donnees)

@app.route("/quiz/tous_les_quiz")
def quiz():
    return render_template("pages/quiz/tous_les_quiz.html", sous_titre="Tous les quiz")

@app.route("/utilisateur/profil.html")
def profil():
    return render_template("pages/utilisateur/profil.html", sous_titre="Mon profil")

@app.route("/a_propos")
def a_propos():
    return render_template("pages/a_propos.html", sous_titre="A propos")

@app.route("/mentions_legales")
def mentions_legales():
    return render_template("pages/mentions_legales.html", sous_titre="Mentions Légales")

@app.route("/remerciements")
def remerciements():
    return render_template("pages/remerciements.html", sous_titre="Remerciements")