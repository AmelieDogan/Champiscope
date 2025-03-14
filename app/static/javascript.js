async function sendAnswer(answer) {
    const response = await fetch("/next_question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: answer })
    });

    const data = await response.json();

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
        document.getElementById("quiz-container").innerHTML = `<h2>${data.result}</h2>`;
    }
}