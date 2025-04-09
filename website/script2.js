document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const name = document.getElementById("username").value.trim();
        const email = document.getElementById("login-email").value.trim();
        const phone = document.getElementById("login-number").value.trim();

        if (!name || !email || !phone) {
            alert("Please fill in all required fields.");
            return;
        }

        localStorage.setItem("username", name);

        fetch("https://flask-backend-9bjs.onrender.com/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, email, phone }),
        })
        .then(response => response.json())
        .then(data => {
            console.log("Login response:", data);
            if (data.message === "Login successful") {
                alert("Login successful!");
                window.location.href = "quiz.html";
            } else {
                alert("Login failed. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error during login:", error);
            alert("An error occurred. Please try again later.");
        });
    });
});