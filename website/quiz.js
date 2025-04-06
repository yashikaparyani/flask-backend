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
        question: "how can you access the last element of an array in JavaScript?",
        options: ["array{last]", "array[-1]", "array[array.length-1]", "array.pop()"],
        answer: 2
    },{
        question: "what is the purpose of setTimeout function in JavaScript",
        options: ["To execute a function immediately", "To execute a function after a delay", "To stop a loop", "To store a variable's value"],
        answer: 1
    }
];

let currentQuestionIndex = 0;
let score = 0;

const questionElement = document.getElementById("question");
const optionsElement = document.getElementById("options");
const nextButton = document.getElementById("next-btn");
const scoreElement = document.getElementById("score");
const quizContainer = document.querySelector(".quiz-container");
    
    if (!quizContainer) {
        console.error("quiz-container not found!");
    } else {
        console.log("quiz-container loaded successfully.");
    }

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
let username = localStorage.getItem("username");
if(!username){
    username = prompt("enter your name")|| "guest";
localStorage.setItem("usename",username);
}
function saveScore() {
    let scores = JSON.parse(localStorage.getItem("leaderboard")) || [];

    let username = localStorage.getItem("username") || "Guest";  // Ensure username is stored
    let scoreEntry = { username: username, score: score };

    scores.push(scoreEntry);
    scores.sort((a, b) => b.score - a.score); // Highest score first
    scores = scores.slice(0, 5); // Only top 5 scores

    localStorage.setItem("leaderboard", JSON.stringify(scores));
}

function endQuiz() {
    console.log("endfunction executed");
    questionElement.innerText = "Quiz Completed!";
    optionsElement.innerHTML = "";
    nextButton.classList.add("hide");
    scoreElement.classList.remove("hide"); // Remove the "hide" class
    scoreElement.innerText = `Final Score: ${score} / ${questions.length}`;
    let leaderboardBtn= document.createElement("button");
    leaderboardBtn.innerText="View leaderboard";
    leaderboardBtn.classList.add("btn");
    leaderboardBtn.addEventListener("click" , () => {
        saveScore();
        window.location.href = "leaderboard.html";
    });
    quizContainer.appendChild(leaderboardBtn);
    let timerElement = document.getElementById("timer");
        if (timerElement) {
            timerElement.style.display="none";
        }
}
let timeleft=10;
let timerInterval;
function startTimer(){
    clearInterval(timerInterval)
   timeleft = 10;
document.getElementById("time-left").innerText = timeleft;
timerInterval = setInterval(() => {
    timeleft--;
document.getElementById("time-left").innerText = timeleft;
if(timeleft==0){
    clearInterval(timerInterval);
    nextQuestion();
}
},1000);

}
function nextQuestion(){
    currentQuestionIndex++;
    if (currentQuestionIndex< questions.length){
        showQuestion();
    }else{
        endQuiz();
    }
}
let leaderboard =[];
fetch("http://127.0.0.1:5501/leaderboard")
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        console.log("Fetched Data:", data);  
        updateLeaderboardUI(data);  // Is function se UI update hoga
    })
    .catch((error) => console.error("Error fetching leaderboard:", error));
fetch('http://127.0.0.1:5501/leaderboard')
    .then(response => response.json())
    .then(data => {
        // Display leaderboard data in UI
        console.log(data);
    })
    .catch(error => console.error('Error:', error));

    fetch('http://127.0.0.1:5501/stats')
    .then(response => response.json())
    .then(data => {
        // Display percentage data in UI
        console.log(data);
    })
    .catch(error => console.error('Error:', error));
  



document.addEventListener("DOMContentLoaded", () => {
    

    startQuiz();
});
