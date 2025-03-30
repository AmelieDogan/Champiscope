from ..app import app, db
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from sqlalchemy import text
from flask_login import current_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import sessionmaker
from ..models.champiscope_db import Referentiel, Surface, Zone, Forme, Couleur, TypeLamelle, ModeInsertion, Milieu, Habitat, MoisPousse, DescriptionChampignon, ObservationHumaine
from ..models.users import User, user_likes

# Récupérer les likes de l'utilisateur
def get_user_likes(user_id):
    result = db.session.execute(
        text("SELECT champi_id FROM user_likes WHERE user_id = :uid"),
        {"uid": user_id}
    ).fetchall()
    return {row.champi_id for row in result}


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
    # Récupération des données de base

    donnees = Referentiel.query.get_or_404(taxref)
    
    nom_champi = donnees.nom

    user_id = session.get("user_id")  # Récupérer l'ID de l'utilisateur connecté
    user_likes = set()
    if user_id:
        rows = db.execute("SELECT champi_id FROM user_likes WHERE user_id = ?", (user_id,))
        user_likes = {row["champi_id"] for row in rows}
    
    return render_template("pages/carte_identite.html", 
        sous_titre = nom_champi, 
        donnees = donnees)

@app.route("/quiz/tous_les_quiz")
def quiz():
    return render_template("pages/quiz/tous_les_quiz.html", sous_titre="Tous les quiz")

@app.route('/utilisateur/profil')
def profil():
    user_likes = get_user_likes(current_user.id)  # Récupérer champis likés pour les afficher sur le profil
    return render_template('pages/utilisateur/profil.html', user_likes=user_likes)

@app.route("/a_propos")
def a_propos():
    return render_template("pages/a_propos.html", sous_titre="A propos")

@app.route("/mentions_legales")
def mentions_legales():
    return render_template("pages/mentions_legales.html", sous_titre="Mentions Légales")

@app.route("/remerciements")
def remerciements():
    return render_template("pages/remerciements.html", sous_titre="Remerciements")

@app.route('/utilisateur/update_profile_image', methods=['GET', 'POST'])
def update_profile_image(): # Changer de photo de profil
    if request.method == 'POST':
        # Récupérer l'image sélectionnée dans le formulaire
        new_image = request.form.get('profile_image')

        if new_image and new_image in ['champi_1.jpg', 'champi_2.jpg', 'champi_3.jpg']:
            # Mettre à jour le nom de l'image de profil dans la base de données
            current_user.profile_image = new_image
            db.session.commit()  # Sauvegarder les changements dans la base de données

            flash("Votre photo de profil a été mise à jour.", "success")
        else:
            flash("Veuillez sélectionner une image valide.", "danger")

        return redirect(url_for('profil'))

    return render_template('pages/utilisateur/update_profile_image.html')

@app.route('/update_password', methods=['POST'])
@login_required
def update_password(): # Changer de mot de passe
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Vérifier si le mot de passe actuel est correct
    if not check_password_hash(current_user.password, current_password):
        flash("Mot de passe actuel incorrect.", "danger")
        return redirect(url_for('profil'))  # Redirection vers la page profil

    # Vérifier si les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        flash("Les nouveaux mots de passe ne correspondent pas.", "danger")
        return redirect(url_for('profil'))

    # Hacher et enregistrer le nouveau mot de passe
    current_user.password = generate_password_hash(new_password)
    db.session.commit()

    flash("Votre mot de passe a été mis à jour avec succès.", "success")
    return redirect(url_for('profil'))


@app.route("/toggle_like", methods=["POST"])
def toggle_like():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Utilisateur non connecté"}), 401

    data = request.get_json()
    champi_id = int(data.get("champi_id"))

    # Vérifier si l'utilisateur a déjà liké ce champignon
    rows = db.execute("SELECT 1 FROM user_likes WHERE user_id = ? AND champi_id = ?", (user_id, champi_id))
    liked = len(rows) > 0

    if liked:
        db.execute("DELETE FROM user_likes WHERE user_id = ? AND champi_id = ?", (user_id, champi_id))
        liked = False
    else:
        db.execute("INSERT INTO user_likes (user_id, champi_id) VALUES (?, ?)", (user_id, champi_id))
        liked = True

    db.commit()
    return jsonify({"liked": liked})

@app.route("/supprimer_compte", methods=["POST"])
@login_required
def supprimer_compte():
    try:
        print(f"Suppression du compte pour l'utilisateur {current_user.id}")
        
        # Suppression des likes associés
        db.session.execute(text("DELETE FROM user_likes WHERE user_id = :uid"), {"uid": current_user.id})

        # Suppression du compte utilisateur
        db.session.execute(text("DELETE FROM user WHERE id = :uid"), {"uid": current_user.id})

        db.session.commit()

        # Déconnexion de l'utilisateur après suppression
        logout_user()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression : {str(e)}")
        return jsonify({"success": False, "error": str(e)})



