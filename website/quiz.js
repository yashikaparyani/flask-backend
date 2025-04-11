const questions = [
    {
      question: "What does HTML stand for?",
      options: ["Hyper Text Markup Language", "Home Tool Markup Language", "Hyperlinks and Text Markup Language", "Hyper Tool Multi Language"],
      correctAnswer: 0
    },
    {
      question: "What is the capital of France?",
      options: ["London", "Berlin", "Paris", "Madrid"],
      correctAnswer: 2
    },
    {
      question: "What is the square root of 64?",
      options: ["6", "7", "8", "9"],
      correctAnswer: 2
    }
  ];
  
  let currentQuestion = 0;
  let score = 0;
  let timer;
  let userAnswers = [];
  
  function startTimer() {
    let timeLeft = 15;
    document.getElementById("timer").textContent = timeLeft;
    timer = setInterval(() => {
      timeLeft--;
      document.getElementById("timer").textContent = timeLeft;
      if (timeLeft <= 0) {
        clearInterval(timer);
        submitAnswer(-1); // auto-skip
      }
    }, 1000);
  }
  
  function showQuestion() {
    const q = questions[currentQuestion];
    document.getElementById("question").textContent = q.question;
    const optionsDiv = document.getElementById("options");
    optionsDiv.innerHTML = "";
    q.options.forEach((option, index) => {
      const btn = document.createElement("button");
      btn.textContent = option;
      btn.className = "option-button";
      btn.onclick = () => submitAnswer(index);
      optionsDiv.appendChild(btn);
    });
    startTimer();
  }
  
  function submitAnswer(selectedOption) {
    clearInterval(timer);
  
    const correct = questions[currentQuestion].correctAnswer;
    if (selectedOption === correct) score++;
  
    userAnswers.push({
      question_id: currentQuestion,
      selected_option: selectedOption
    });
  
    currentQuestion++;
    if (currentQuestion < questions.length) {
      showQuestion();
    } else {
      finishQuiz();
    }
  }
  
  function finishQuiz() {
    document.getElementById("quiz-container").innerHTML = `
      <h2>Quiz Completed!</h2>
      <p>Your Score: ${score}/${questions.length}</p>
      <button onclick="submitScore()">Submit Score</button>
      <button onclick="window.location.href='leaderboard.html'">View Leaderboard</button>
      <div id="stats-container"></div>
    `;
    sendAnswersToBackend();
  }
  
  function submitScore() {
    const name = localStorage.getItem("name") || "Anonymous";
    fetch("https://flask-backend-9bjs.onrender.com/submit-score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, score })
    })
      .then(res => res.json())
      .then(data => {
        alert("Score submitted!");
      })
      .catch(err => {
        alert("Error submitting score.");
        console.error(err);
      });
  }
  
  function sendAnswersToBackend() {
    fetch("https://flask-backend-9bjs.onrender.com/submit-answers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers: userAnswers })
    })
      .then(res => res.json())
      .then(() => {
        getQuestionStats();
      })
      .catch(err => console.error("Error saving answers:", err));
  }
  
  function getQuestionStats() {
    fetch("https://flask-backend-9bjs.onrender.com/question-stats")
      .then(res => res.json())
      .then(stats => {
        const container = document.getElementById("stats-container");
        container.innerHTML = "<h3>Question Stats:</h3>";
  
        questions.forEach((q, i) => {
          const qStats = stats[i] || {};
          const total = Object.values(qStats).reduce((a, b) => a + b, 0) || 1;
  
          const statDiv = document.createElement("div");
          statDiv.innerHTML = <strong>${q.question}</strong>;
          q.options.forEach((opt, idx) => {
            const count = qStats[idx] || 0;
            const percent = ((count / total) * 100).toFixed(1);
            const line = document.createElement("p");
            line.textContent = `${opt}: ${percent}% (${count})`;
            statDiv.appendChild(line);
          });
          container.appendChild(statDiv);
          container.appendChild(document.createElement("hr"));
        });
      })
      .catch(err => console.error("Error fetching stats:", err));
  }
  
  document.addEventListener("DOMContentLoaded", showQuestion);