document.addEventListener('DOMContentLoaded', () => {
    const leaderboardList = document.getElementById('leaderboard-list');

    fetch('https://flask-backend-9bjs.onrender.com/leaderboard')  // Use your backend URL here
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch leaderboard data');
            }
            return response.json();
        })
        .then(data => {
            leaderboardList.innerHTML = '';

            data.forEach((entry, index) => {
                const li = document.createElement('li');
                li.textContent = `${index + 1}. ${entry.name} - ${entry.score}`;
                leaderboardList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading leaderboard:', error);
        });
});