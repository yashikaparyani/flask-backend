document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const name = document.getElementById("username").value.trim();
        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value.trim();
        const phone = document.getElementById("login-number").value.trim();

        if (!name || !email || !password || !phone) {
            alert("Please fill in all fields.");
            return;
        }

        // Save the username to localStorage for use in quiz.js
        localStorage.setItem("username", name);

        fetch("https://flask-backend-9bjs.onrender.com/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 
                name: username,
                 email:email,
                 phone: phone }), // MATCHING BACKEND
        })
        .then(response => response.json())
        .then(data => {
            console.log("Login response:", data);
            if (data.success) {
                alert("Login successful!");
                window.location.href = "quiz.html";
            } else {
                alert("Login failed: " + (data.error || "Please try again."));
            }
        })
        .catch(error => {
            console.error("Error during login:", error);
            alert("An error occurred. Please try again later.");
        });
    });
});