const BACKEND_URL = 'https://flask-backend-9bjs.onrender.com'; // Replace with your actual backend URL

document.addEventListener("DOMContentLoaded", () => {
    fetch(`${BACKEND_URL}/leaderboard`)
        .then(response => response.json())
        .then(data => {
            const leaderboardList = document.getElementById("leaderboard");
            leaderboardList.innerHTML = "";

            data.forEach(entry => {
                const listItem = document.createElement("li");
                listItem.textContent = `${entry.name}: ${entry.score}`;
                leaderboardList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("Error fetching leaderboard:", error);
        });
});