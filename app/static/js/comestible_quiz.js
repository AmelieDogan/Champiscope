// Variables globales
let currentQuestionIndex = 0;
let questions = [];
let userAnswers = [];
let score = 0;

// Charger les questions au démarrage
window.onload = async function () {
    try {
        const response = await fetch("/quiz/comestible/data");
        const data = await response.json();
        questions = data.questions;

        // Afficher la première question
        if (questions.length > 0) {
            displayQuestion(currentQuestionIndex);
            updateProgressBar();
        }
    } catch (error) {
        console.error("Erreur lors du chargement des données:", error);
    }
};

// Afficher une question
function displayQuestion(index) {
    const question = questions[index];

    // Mettre à jour les informations du champignon
    document.getElementById("champignon-nom").textContent = question.nom;

    // Afficher le nom vernaculaire s'il existe
    const nomVernaculaireElement = document.getElementById("champignon-nom-vernaculaire");
    if (question.nom_vernaculaire) {
        nomVernaculaireElement.textContent = question.nom_vernaculaire;
        nomVernaculaireElement.style.display = "block";
    } else {
        nomVernaculaireElement.style.display = "none";
    }

    // Afficher l'image
    document.getElementById("question-image").src = question.image_url;

    // Réinitialiser les boutons
    document.getElementById("btn-comestible").className = "answer-button";
    document.getElementById("btn-non-comestible").className = "answer-button";

    // Cacher le feedback
    document.getElementById("feedback").style.display = "none";
}

// Vérifier la réponse
function checkAnswer(isComestible) {
    const question = questions[currentQuestionIndex];
    const correctAnswer = question.comestible;
    const isCorrect = (isComestible === correctAnswer);

    // Stocker la réponse de l'utilisateur
    userAnswers[currentQuestionIndex] = {
        champignon: question.nom,
        userAnswer: isComestible,
        correctAnswer: correctAnswer,
        isCorrect: isCorrect
    };

    // Mettre à jour le score
    if (isCorrect) {
        score++;
    }

    // Afficher le feedback visuel (changer la couleur des boutons)
    const comestibleButton = document.getElementById("btn-comestible");
    const nonComestibleButton = document.getElementById("btn-non-comestible");

    if (isComestible) {
        comestibleButton.className = isCorrect ? "answer-button correct" : "answer-button incorrect";
        nonComestibleButton.className = "answer-button";
    } else {
        nonComestibleButton.className = isCorrect ? "answer-button correct" : "answer-button incorrect";
        comestibleButton.className = "answer-button";
    }

    // Afficher le message de feedback
    const feedbackElement = document.getElementById("feedback");
    const feedbackTextElement = document.getElementById("feedback-text");

    if (isCorrect) {
        feedbackTextElement.textContent = "Bonne réponse !";
    } else {
        feedbackTextElement.textContent = `Réponse incorrecte. Ce champignon ${correctAnswer ? "est" : "n'est pas"} comestible.`;
    }

    feedbackElement.style.display = "block";

    // Désactiver les boutons pour éviter de répondre plusieurs fois
    comestibleButton.disabled = true;
    nonComestibleButton.disabled = true;
}

// Passer à la question suivante
function nextQuestion() {
    currentQuestionIndex++;

    if (currentQuestionIndex < questions.length) {
        // Question suivante
        displayQuestion(currentQuestionIndex);
        updateProgressBar();

        // Réactiver les boutons
        document.getElementById("btn-comestible").disabled = false;
        document.getElementById("btn-non-comestible").disabled = false;
    } else {
        // Fin du quiz
        showResults();
    }
}

// Mettre à jour la barre de progression
function updateProgressBar() {
    const progressPercentage = ((currentQuestionIndex + 1) / questions.length) * 100;
    document.getElementById("progress-fill").style.width = `${progressPercentage}%`;
    document.getElementById("progress-text").textContent = `Question ${currentQuestionIndex + 1}/${questions.length}`;
}

// Afficher les résultats
function showResults() {
    document.getElementById("question-container").style.display = "none";
    document.getElementById("results-container").style.display = "block";

    // Afficher le score
    const scorePercentage = (score / questions.length) * 100;
    document.getElementById("score-text").textContent = `Ton score: ${score}/${questions.length} (${scorePercentage.toFixed(1)}%)`;

    // Générer le résumé des réponses
    const summaryElement = document.getElementById("results-summary");
    summaryElement.innerHTML = "";

    userAnswers.forEach((answer, index) => {
        const answerItem = document.createElement("div");
        answerItem.className = `result-item ${answer.isCorrect ? "correct" : "incorrect"}`;

        answerItem.innerHTML = `
            <p><strong>${index + 1}. ${answer.champignon}</strong></p>
            <p>Ta réponse: ${answer.userAnswer ? "Comestible" : "Non comestible"}</p>
            <p>Réponse correcte: ${answer.correctAnswer ? "Comestible" : "Non comestible"}</p>
        `;

        summaryElement.appendChild(answerItem);
    });

    // Envoyer le score au serveur
    envoyerScore(score, questions.length);
}

// Enregistrer le score dans la base de données
// Récupérer le jeton CSRF depuis la balise <meta>
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

// Fonction pour envoyer le score du quiz
function envoyerScore(userScore, totalQuestions) {
    fetch("/quiz/comestible/save_score", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken  // 🔥 On ajoute le token CSRF ici
        },
        body: JSON.stringify({
            score: userScore,
            totalQuestions: totalQuestions
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Réponse du serveur:", data);
    })
    .catch(error => {
        console.error("Erreur lors de l'envoi du score:", error);
    });
}

// Redémarrer le quiz
function restartQuiz() {
    currentQuestionIndex = 0;
    userAnswers = [];
    score = 0;

    document.getElementById("results-container").style.display = "none";
    document.getElementById("question-container").style.display = "block";

    displayQuestion(currentQuestionIndex);
    updateProgressBar();

    // Réactiver les boutons
    document.getElementById("btn-comestible").disabled = false;
    document.getElementById("btn-non-comestible").disabled = false;
}