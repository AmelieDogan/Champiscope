let currentQuestionIndex = 0;
let scores = {};

// Initialiser les scores au chargement
window.onload = function() {
    for (let i = 1; i <= 8; i++) {
        scores[i.toString()] = 0;
    }
};

async function sendAnswer(answer) {
    // Envoyer la réponse et les données d'état au serveur
    const response = await fetch("/next_question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            answer: answer,
            question_index: currentQuestionIndex,
            scores: scores
        })
    });

    const data = await response.json();
    
    // Mettre à jour les scores et l'index côté client
    if (data.scores) {
        scores = data.scores;
    }
    
    if (data.question_index !== undefined) {
        currentQuestionIndex = data.question_index;
    } else {
        currentQuestionIndex++;
    }

    if (data.question) {
        document.getElementById("question-text").innerText = data.question;
        const buttonsDiv = document.getElementById("buttons");
        buttonsDiv.innerHTML = "";

        data.choices.forEach(choice => {
            let btn = document.createElement("button");
            btn.innerText = choice;
            btn.onclick = () => sendAnswer(choice);
            btn.classList.add("answer-button");
            buttonsDiv.appendChild(btn);
        });
    } else {
        document.getElementById("quiz-container").innerHTML = `
            <h2>Ton résultat:</h2>
            <h3>${data.result}</h3>
            <div class="description-container">
                <p>${data.description}</p>
            </div>
            <button class="restart-button" onclick="location.reload()">Refaire le quiz</button>
        `;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour plier/déplier les sections de filtres
    const filterHeaders = document.querySelectorAll('.filtre-section h4');
    
    filterHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const options = this.nextElementSibling;
            options.style.display = options.style.display === 'none' ? 'block' : 'none';
            this.classList.toggle('collapsed');
        });
    });
});