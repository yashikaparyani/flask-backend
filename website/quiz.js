let questions = [
    {
        question: "What will console.log(2 + '2') output in JavaScript?",
        options: ["4", "22", "NaN", "Error"],
        answer: 1
    },
    {
        question: "Which keyword is used to declare a constant variable in JavaScript?",
        options: ["let", "var", "const", "static"],
        answer: 2
    },
    {
        question: "What does the typeof operator return for null?",
        options: ["null", "object", "undefined", "number"],
        answer: 1
    },
    {
        question: "How can you access the last element of an array in JavaScript?",
        options: ["array{last]", "array[-1]", "array[array.length-1]", "array.pop()"],
        answer: 2
    },
    {
        question: "What is the purpose of setTimeout function in JavaScript?",
        options: ["To execute a function immediately", "To execute a function after a delay", "To stop a loop", "To store a variable's value"],
        answer: 1
    }
];

let currentQuestionIndex = 0;
let score = 0;
let timerInterval;
let timeleft = 10;

const questionElement = document.getElementById("question");
const optionsElement = document.getElementById("options");
const nextButton = document.getElementById("next-btn");
const scoreElement = document.getElementById("score");
const quizContainer = document.querySelector(".quiz-container");

function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    showQuestion();
}

function showQuestion() {
    let questionData = questions[currentQuestionIndex];
    questionElement.innerText = questionData.question;
    optionsElement.innerHTML = "";

    questionData.options.forEach((option, index) => {
        const button = document.createElement("button");
        button.innerText = option;
        button.classList.add("btn");
        button.addEventListener("click", () => selectAnswer(index));
        optionsElement.appendChild(button);
    });

    nextButton.classList.add("hide");
    scoreElement.innerText = `Score: ${score}`;
    startTimer();
}

function selectAnswer(index) {
    clearInterval(timerInterval);
    let correctIndex = questions[currentQuestionIndex].answer;

    if (index === correctIndex) {
        score++;
        optionsElement.children[index].classList.add("correct");
    } else {
        optionsElement.children[index].classList.add("wrong");
        optionsElement.children[correctIndex].classList.add("correct");
    }

    disableOptions();
    nextButton.classList.remove("hide");
}

function disableOptions() {
    Array.from(optionsElement.children).forEach(button => {
        button.disabled = true;
    });
}

nextButton.addEventListener("click", () => {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        endQuiz();
    }
});

function endQuiz() {
    clearInterval(timerInterval);
    questionElement.innerText = "Quiz Completed!";
    optionsElement.innerHTML = "";
    nextButton.classList.add("hide");
    scoreElement.innerText = `Final Score: ${score} / ${questions.length}`;

    const leaderboardBtn = document.createElement("button");
    leaderboardBtn.innerText = "View Leaderboard";
    leaderboardBtn.classList.add("btn");
    leaderboardBtn.addEventListener("click", () => {
        saveScore();
        window.location.href = "leaderboard.html";
    });
    quizContainer.appendChild(leaderboardBtn);

    const timerEl = document.getElementById("timer");
    if (timerEl) timerEl.style.display = "none";
}

function startTimer() {
    clearInterval(timerInterval);
    timeleft = 10;
    document.getElementById("time-left").innerText = timeleft;
    timerInterval = setInterval(() => {
        timeleft--;
        document.getElementById("time-left").innerText = timeleft;
        if (timeleft === 0) {
            clearInterval(timerInterval);
            nextQuestion();
        }
    }, 1000);
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        endQuiz();
    }
}

// Setup username if not set
let username = localStorage.getItem("username");
if (!username) {
    username = prompt("Enter your name") || "Guest";
    localStorage.setItem("username", username); // Fixed typo here
}

const BACKEND_URL = 'https://flask-backend-9bjs.onrender.com';

function saveScore() {
    const scoreEntry = { name: username, score: score };
    fetch(`${BACKEND_URL}/leaderboard`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scoreEntry)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Score submitted successfully", data);
    })
    .catch(error => {
        console.error("Failed to submit score:", error);
    });
}

function saveScore() {
    let scores = JSON.parse(localStorage.getItem("leaderboard")) || [];

    let username = localStorage.getItem("username") || "Guest";
    let scoreEntry = { name: username, score: score };

    scores.push(scoreEntry);
    scores.sort((a, b) => b.score - a.score);
    scores = scores.slice(0, 5);
    localStorage.setItem("leaderboard", JSON.stringify(scores));

    // Add this line to push to backend
    submitScore(username, score);
}

document.addEventListener("DOMContentLoaded", () => {
    startQuiz();
});