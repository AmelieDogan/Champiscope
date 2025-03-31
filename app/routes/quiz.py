from ..app import app, db
from ..utils import champignons
from flask import Flask, render_template, request, jsonify
from flask_login import current_user, login_required
from ..models.champiscope_db import Referentiel, DescriptionChampignon, Iconographie
from ..models.users import ScoreQuizComestible

import random as rd

questions_mon_champi = [
    {
        "text": "Quel est ton environnement idéal ?",
        "choices": [
            {"answer": "Une forêt profonde et ancienne", "champi": [1, 2]},
            {"answer": "Un marché coloré, gourmand et animé", "champi": [3, 5]},
            {"answer": "Clairière ensoleillée et paisible", "champi": [4, 8]},
            {"answer": "Sentier discret, loin de tout", "champi": [6, 7]}
        ]
    },
    {
        "text": "Quel trait de caractère te définit le mieux ?",
        "choices": [
            {"answer": "Sage et créatif", "champi": [1, 2]},
            {"answer": "Raffiné et discret", "champi": [3, 6]},
            {"answer": "Chaleureux et bienveillant", "champi": [4, 8]},
            {"answer": "Spontané et aventureux", "champi": [5, 7]}
        ]
    },
    {
        "text": "Quelle est ta saison préférée ?",
        "choices": [
            {"answer": "Automne", "champi": [1, 8]},
            {"answer": "Hiver", "champi": [6, 5]},
            {"answer": "Printemps", "champi": [3, 7]},
            {"answer": "Été", "champi": [4, 2]}
        ]
    },
    {
        "text": "Si tu étais un plat, tu serais…",
        "choices": [
            {"answer": "Une poêlée forestière raffinée et savoureuse", "champi": [1, 6]},
            {"answer": "Un plat exotique et surprenant", "champi": [2, 7]},
            {"answer": "Un repas simple mais délicieux", "champi": [4, 5]},
            {"answer": "Un plat classique mais réconfortant", "champi": [8, 3]}
        ]
    },
    {
        "text": "Comment réagis-tu face à l'imprévu ?",
        "choices": [
            {"answer": "J’observe et je réfléchis avant d'agir.", "champi": [1, 6]},
            {"answer": "Je trouve une solution originale.", "champi": [2, 3]},
            {"answer": "Je réagis immédiatement et j’improvise.", "champi": [7, 5]},
            {"answer": "Je protège et rassure mon entourage.", "champi": [8, 4]}
        ]
    },
    {
        "text": "Quel est ton animal totem ?",
        "choices": [
            {"answer": "Un hibou sage et distingué", "champi": [1, 3]},
            {"answer": "Un renard rusé et discret", "champi": [2, 6]},
            {"answer": "Un perroquet joyeux et voyageur", "champi": [4, 7]},
            {"answer": "Un chien protecteur et courageux", "champi": [8, 5]}
        ]
    },
    {
        "text": "Quel genre de musique écoutes-tu le plus ?",
        "choices": [
            {"answer": "Classique et apaisante", "champi": [1, 6]},
            {"answer": "Musique dynamique et imprévisible", "champi": [2, 7]},
            {"answer": "Jazz sophistiqué", "champi": [3, 8]},
            {"answer": "Pop joyeuse et entraînante", "champi": [4, 5]}
        ]
    },
    {
        "text": "Quel serait ton super-pouvoir idéal ?",
        "choices": [
            {"answer": "Changer d’apparence à volonté", "champi": [2, 3]},
            {"answer": "Lire dans les pensées", "champi": [6, 1]},
            {"answer": "Pouvoir me téléporter", "champi": [5, 7]},
            {"answer": "Avoir une force surhumaine", "champi": [8, 4]}
        ]
    },
    {
        "text": "Quelle est la couleur qui t’attire le plus ?",
        "choices": [
            {"answer": "Marron", "champi": [1, 8]},
            {"answer": "Rouge et orange", "champi": [2, 7]},
            {"answer": "Or et jaune éclatant", "champi": [6, 4]},
            {"answer": "Argenté et blanc", "champi": [3, 5]}
        ]
    },
    {
        "text": "Quel type de film préfères-tu ?",
        "choices": [
            {"answer": "Action et thriller", "champi": [5, 6]},
            {"answer": "Fantaisie et aventure", "champi": [2, 7]},
            {"answer": "Film d’époque", "champi": [3, 1]},
            {"answer": "Comédie légère et amitié", "champi": [4, 8]}
        ]
    },
    {
        "text": "Quel est ton passe-temps favori ?",
        "choices": [
            {"answer": "Lire et boire du thé", "champi": [1, 3]},
            {"answer": "Profiter de la vie et passer du temps avec mes proches", "champi": [4, 8]},
            {"answer": "Observer le monde et exprimer mon imagination", "champi": [6, 2]},
            {"answer": "Voyager et faire du sport", "champi": [7, 5]}
        ]
    },
    {
        "text": "Si tu pouvais vivre à une autre époque, laquelle choisirais-tu ?",
        "choices": [
            {"answer": "L’Antiquité, pour sa sagesse et ses philosophies", "champi": [1, 7]},
            {"answer": "Le XIXe siècle, pour la modernité et l’élégance", "champi": [3, 5]},
            {"answer": "Les années 60-70, pour leur insouciance et leur optimisme", "champi": [4, 8]},
            {"answer": "Le Moyen Âge, pour ses mystères et son ambiance unique", "champi": [6, 2]}
        ]
    }
]

@app.route("/quiz/quel_champi_suis_je")
def quel_champi():
    return render_template("pages/quiz/quel_champi_suis_je.html",
                           sous_titre="Quel champignon es-tu ?",
                           question=questions_mon_champi[0]["text"], 
                           choices=[choice["answer"] for choice in questions_mon_champi[0]["choices"]])

@app.route("/next_question", methods=["POST"])
@login_required
def next_question():
    data = request.get_json()
    
    # Récupérer les scores et l'index de question du client
    question_index = data.get("question_index", 0)
    scores = data.get("scores", {})
    
    if not scores:
        scores = {str(i): 0 for i in range(1, 9)}
    
    # Trouver les champignons associés à cette réponse
    current_answer = data["answer"]
    for choice in questions_mon_champi[question_index]["choices"]:
        if choice["answer"] == current_answer:
            # Incrémenter le score de chaque champignon associé
            for champi_id in choice["champi"]:
                scores[str(champi_id)] = scores.get(str(champi_id), 0) + 1
            break
    
    # Incrémenter l'index de question
    question_index += 1
    
    if question_index < len(questions_mon_champi):
        return jsonify({
            "question": questions_mon_champi[question_index]["text"],
            "choices": [choice["answer"] for choice in questions_mon_champi[question_index]["choices"]],
            "question_index": question_index,
            "scores": scores
        })
    else:
        # Trouver le champignon avec le score le plus élevé
        max_score = -1
        winner_id = "1"  # Valeur par défaut
        
        for champi_id, score in scores.items():
            if score > max_score:
                max_score = score
                winner_id = champi_id
        
        winner = champignons[int(winner_id)]

        current_user.champi_id = winner['taxref_id']
        db.session.commit()

        return jsonify({
            "result": f"Tu es {winner['nom']} !",
            "description": winner['description'],
            "taxref_id": winner['taxref_id']
        })

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/quiz/comestible")
def quiz_comestible():
    return render_template("pages/quiz/comestible.html", 
                           sous_titre="Es-tu un expert en comestibilité ?")

@app.route("/quiz/comestible/data")
def get_quiz_data():
    # Sélectionner les champignons qui ont au moins une image et une information de comestibilité
    champignons_avec_images_et_comestibilite = (
        db.session.query(
            Referentiel, DescriptionChampignon, Iconographie
        )
        .join(DescriptionChampignon, Referentiel.taxref_id == DescriptionChampignon.taxref_id)
        .join(Iconographie, Referentiel.taxref_id == Iconographie.taxref_id)
        .filter(DescriptionChampignon.comestibilite != None)
        .all()
    )
    
    # Regrouper par taxref_id pour éviter les doublons dus aux multiples images
    champignons_groupes = {}
    for ref, desc, icon in champignons_avec_images_et_comestibilite:
        if ref.taxref_id not in champignons_groupes:
            champignons_groupes[ref.taxref_id] = {
                "taxref_id": ref.taxref_id,
                "nom": ref.nom,
                "nom_vernaculaire": ref.nom_vernaculaire,
                "comestible": desc.comestibilite,
                "image_url": icon.url_image
            }
    
    # Convertir en liste
    champignons_liste = list(champignons_groupes.values())
    
    # Séparer en comestibles et non comestibles
    comestibles = [c for c in champignons_liste if c["comestible"]]
    non_comestibles = [c for c in champignons_liste if not c["comestible"]]
    
    # Déterminer le nombre de champignons comestibles à inclure (entre 3 et 8)
    nb_comestibles = rd.randint(3, min(8, len(comestibles)))
    nb_non_comestibles = 15 - nb_comestibles
    
    # S'assurer qu'il y a assez de champignons non comestibles
    if len(non_comestibles) < nb_non_comestibles:
        nb_non_comestibles = len(non_comestibles)
        nb_comestibles = 15 - nb_non_comestibles
    
    # Sélectionner aléatoirement les champignons
    selected_comestibles = rd.sample(comestibles, nb_comestibles)
    selected_non_comestibles = rd.sample(non_comestibles, nb_non_comestibles)
    
    # Combiner et mélanger les questions
    questions = selected_comestibles + selected_non_comestibles
    rd.shuffle(questions)
    
    return jsonify({"questions": questions})
    
@app.route("/quiz/comestible/save_score", methods=["POST"])
@login_required
def save_comestible_score():
    try:
        print("Requête reçue pour enregistrer le score")
        data = request.get_json()
        print(f"Données reçues: {data}")
        
        if not data:
            return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400
            
        score_value = data.get("score")
        total_questions = data.get("totalQuestions")
        
        print(f"Score: {score_value}/{total_questions}")
        
        # Calculer le pourcentage de réussite
        score_percentage = (score_value / total_questions) * 100
        
        print(f"Tentative d'enregistrement du score: {score_percentage}%")
        current_user.enregistrer_score(score_percentage)
        db.session.commit()
        print("Score enregistré avec succès")
        
        return jsonify({"success": True, "message": "Score enregistré avec succès!"})
    except Exception as e:
        print(f"Erreur: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erreur lors de l'enregistrement du score: {str(e)}"}), 500