document.addEventListener("DOMContentLoaded", () => {
    let leaderboard = JSON.parse(localStorage.getItem("leaderboard")) || [];
    const leaderboardContainer = document.getElementById("leaderboard");
    console.log("leaderboard", leaderboardContainer);

    if (leaderboard.length === 0) {
        leaderboardContainer.innerHTML = "<p>No scores yet!</p>";
    } else {
        leaderboardContainer.innerHTML = leaderboard.map((entry, index) => 
            `<p><strong>#${index + 1}</strong> ${entry.username} - ${entry.score}</p>`
        ).join("");
    }
});
function resetLeaderboard() {
    localStorage.removeItem("leaderboard"); // Removes stored scores
    document.getElementById("leaderboard").innerHTML = "<p>Leaderboard Cleared!</p>"; // UI update
}