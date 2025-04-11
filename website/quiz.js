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

const questionElement = document.getElementById("question");
const optionsElement = document.getElementById("options");
const nextButton = document.getElementById("next-btn");
const scoreElement = document.getElementById("score");
const quizContainer = document.querySelector(".quiz-container");

const BACKEND_URL = "https://flask-backend-9bjs.onrender.com";

function startQuiz() {
  currentQuestionIndex = 0;
  score = 0;
  showQuestion();
}

function showQuestion() {
  const questionData = questions[currentQuestionIndex];
  questionElement.innerText = questionData.question;
  optionsElement.innerHTML = "";

  questionData.options.forEach((option, index) => {
      const button = document.createElement("button");
      button.innerText = option;
      button.classList.add("btn");
      button.addEventListener("click", () => selectAnswer(index));
      button.addEventListener("click", () => {
        fetch('https://flask-backend-9bjs.onrender.com/submit-option', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: currentQuestionIndex,
                option_index: index
            })
        })
        .then(() => {
            // Get updated percentages
            fetch(`https://flask-backend-9bjs.onrender.com/get-percentages/${currentQuestionIndex}`)
                .then(res => res.json())
                .then(percentages => {
                    const buttons = optionsElement.querySelectorAll('button');
                    percentages.forEach((percent, idx) => {
                        buttons[idx].innerText =` ${questions[currentQuestionIndex].options[idx]} (${percent}%)`;
                    });
                });
        });
    });
      optionsElement.appendChild(button);
  });

  nextButton.classList.add("hide");
  scoreElement.innerText = `Score: ${score}`;
  startTimer();
}

function selectAnswer(index) {
  clearInterval(timerInterval);
  const correctIndex = questions[currentQuestionIndex].answer;
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
  questionElement.innerText = "Quiz Completed!";
  optionsElement.innerHTML = "";
  nextButton.classList.add("hide");
  scoreElement.classList.remove("hide");
  scoreElement.innerText = `Final Score: ${score} / ${questions.length}`;

  // Auto submit the score
  saveToBackend();

  // Add leaderboard button (still optional)
  const leaderboardBtn = document.createElement("button");
  leaderboardBtn.innerText = "View Leaderboard";
  leaderboardBtn.classList.add("btn");
  leaderboardBtn.addEventListener("click", () => {
      window.location.href = "leaderboard.html";
  });
  quizContainer.appendChild(leaderboardBtn);

  const timerElement = document.getElementById("timer");
  if (timerElement) {
      timerElement.style.display = "none";
  }
}

function saveToBackend() {
  const username = localStorage.getItem("username") || "Guest";
  console.log("Submitting score to backend:", username, score);

  fetch(`${BACKEND_URL}/leaderboard`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({
          name: username,
          score: score
      })
  })
  .then(res => res.json())
  .then(data => {
      console.log("Score saved:", data);
  })
  .catch(err => {
      console.error("Failed to save score:", err);
  });
}

let timeleft = 10;
function startTimer() {
  clearInterval(timerInterval);
  timeleft = 10;
  document.getElementById("time-left").innerText = timeleft;
  timerInterval = setInterval(() => {
      timeleft--;
      document.getElementById("time-left").innerText = timeleft;
      if (timeleft === 0) {
          clearInterval(timerInterval);
          nextButton.click();
      }
  }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
  const username = localStorage.getItem("username") || prompt("Enter your name") || "Guest";
  localStorage.setItem("username", username);
  startQuiz();
});