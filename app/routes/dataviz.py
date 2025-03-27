from flask import render_template, jsonify
from sqlalchemy import and_, func, cast, Integer
from ..app import app, db
from ..models.champiscope_db import MoisPousse, DescriptionChampignon

@app.route('/dataviz')
def visualisations():
    """Page principale des visualisations"""
    return render_template('pages/dataviz.html', sous_titre = "Dataviz")

@app.route('/api/comestibilite')
def api_comestibilite():
    """API pour les données de comestibilité"""
    # Requête pour compter les champignons comestibles et non comestibles
    comestibles = db.session.query(
        DescriptionChampignon.comestibilite,
        DescriptionChampignon.comestibilite_detail,
        func.count(DescriptionChampignon.taxref_id)
    ).group_by(
        DescriptionChampignon.comestibilite,
        DescriptionChampignon.comestibilite_detail
    ).all()
    
    # Formatage des données pour le graphique
    result = []
    for comestible, detail, count in comestibles:
        # Gestion des valeurs None
        comestible_status = "Comestible" if comestible else "Non comestible"
        detail_status = detail if detail else "Sans précisions"
        
        result.append({
            "comestibilite": comestible_status,
            "detail": detail_status,
            "count": count
        })
    
    return jsonify(result)

@app.route('/api/mois_pousse')
def api_mois_pousse():
    """API pour les données de mois de pousse"""
    # Requête pour compter le nombre de True par mois
    mois_data = db.session.query(
        func.sum(cast(MoisPousse.janvier, Integer)),
        func.sum(cast(MoisPousse.fevrier, Integer)),
        func.sum(cast(MoisPousse.mars, Integer)),
        func.sum(cast(MoisPousse.avril, Integer)),
        func.sum(cast(MoisPousse.mai, Integer)),
        func.sum(cast(MoisPousse.juin, Integer)),
        func.sum(cast(MoisPousse.juillet, Integer)),
        func.sum(cast(MoisPousse.aout, Integer)),
        func.sum(cast(MoisPousse.septembre, Integer)),
        func.sum(cast(MoisPousse.octobre, Integer)),
        func.sum(cast(MoisPousse.novembre, Integer)),
        func.sum(cast(MoisPousse.decembre, Integer))
    ).first()
    
    # Convertir en format pour le graphique radar
    mois_names = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ]
    
    result = [{"axis": mois_names[i], "value": mois_data[i] or 0} for i in range(len(mois_names))]

    return jsonify(result)
