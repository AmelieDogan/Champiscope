// Variables globales
let currentQuestionIndex = 0;
let questions = [];
let userAnswers = [];
let score = 0;

// Charger les questions au démarrage
window.onload = async function() {
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
    saveScore(score, questions.length);
}

// Fonction pour enregistrer le score dans la base de données
async function saveScore(scoreValue, totalQuestions) {
    try {
        const response = await fetch("/quiz/comestible/save_score", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                score: scoreValue,
                totalQuestions: totalQuestions
            })
        });
        
        // Vérifier si l'utilisateur a été redirigé vers la page de connexion
        if (response.redirected || !response.ok) {
            console.log("Utilisateur non connecté ou erreur. Score non enregistré.");
            
            // Informer l'utilisateur qu'il doit se connecter pour enregistrer son score
            const loginMessage = document.createElement("div");
            loginMessage.className = "login-required-message";
            loginMessage.innerHTML = "Connecte-toi pour enregistrer tes scores! <a href='/utilisateur/connexion'>Se connecter</a>";
            document.getElementById("results-container").appendChild(loginMessage);
            return;
        }
        
        // S'assurer que la réponse est bien du JSON avant de la parser
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            console.error("La réponse n'est pas au format JSON");
            return;
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Afficher un message de confirmation
            const savedMessage = document.createElement("div");
            savedMessage.className = "score-saved-message";
            savedMessage.textContent = "Score enregistré!";
            document.getElementById("results-container").appendChild(savedMessage);
        } else {
            console.error("Erreur lors de l'enregistrement du score:", result.message);
        }
    } catch (error) {
        console.error("Erreur lors de la communication avec le serveur:", error);
        
        // Afficher un message d'erreur pour l'utilisateur
        const errorMessage = document.createElement("div");
        errorMessage.className = "error-message";
        errorMessage.textContent = "Impossible d'enregistrer le score. Vérifie ta connexion.";
        document.getElementById("results-container").appendChild(errorMessage);
    }
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