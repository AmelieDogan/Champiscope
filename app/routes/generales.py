from ..app import app, db
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from sqlalchemy import text
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import sessionmaker
from ..models.champiscope_db import Referentiel, Surface, Zone, Forme, Couleur, TypeLamelle, ModeInsertion, Milieu, Habitat, MoisPousse, DescriptionChampignon, ObservationHumaine
from ..models.users import User, user_likes

# Récupérer les likes de l'utilisateur
def get_user_likes(user_id):
    # Récupère l'utilisateur avec son id et ses likes
    user = User.query.get(user_id)
    return user.likes

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

@app.route("/dataviz")
def dataviz():
    return render_template("pages/dataviz.html", sous_titre="Dataviz")

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
