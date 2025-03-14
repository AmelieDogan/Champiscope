from ..app import app
from flask import Flask, render_template, request, session, jsonify

questions = [
    {"text": "Quel est ton environnement idéal ?", "choices": ["Forêt ancienne", "Marché gourmand", "Clairière ensoleillée", "Sentier discret"]},
    {"text": "Comment tes amis te décriraient-ils ?", "choices": ["Excentrique", "Élégant", "Jovial", "Secret"]},
    {"text": "Quel est ton plat préféré ?", "choices": ["Risotto aux truffes", "Plat familial", "Salade colorée", "Plat traditionnel"]},
]

results = {
    "Forêt ancienne": "Amanite tue-mouches (Le Rêveur Fantaisiste)",
    "Marché gourmand": "Cèpe de Bordeaux (L’Indémodable Gourmet)",
    "Clairière ensoleillée": "Girolle (L’Optimiste Lumineux)",
    "Sentier discret": "Morille (L’Exclusif Mystérieux)"
}

@app.route("/quiz/quel_champi_suis_je.html")
def quel_champi():
    session["answers"] = []
    return render_template("pages/quiz/quel_champi_suis_je.html", question=questions[0]["text"], choices=questions[0]["choices"])

@app.route("/next_question", methods=["POST"])
def next_question():
    data = request.get_json()
    session["answers"].append(data["answer"])

    question_index = len(session["answers"])
    
    if question_index < len(questions):
        return jsonify({
            "question": questions[question_index]["text"],
            "choices": questions[question_index]["choices"]
        })
    else:
        most_common_answer = max(set(session["answers"]), key=session["answers"].count)
        result = results.get(most_common_answer, "Mousseron de la Saint-Georges (Le Fidèle Traditionnel)")
        return jsonify({"result": f"Tu es {result} !"})

if __name__ == "__main__":
    app.run(debug=True)