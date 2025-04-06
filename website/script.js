// Dark Mode Toggle
const toggleDarkMode = document.querySelector(".toggle-dark-mode");
toggleDarkMode.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    toggleDarkMode.innerHTML = document.body.classList.contains("dark-mode") ? 
        '<i class="ri-sun-line"></i>' : '<i class="ri-moon-line"></i>';
});

// Smooth Scrolling
document.querySelectorAll("a").forEach(anchor => {
    anchor.addEventListener("click", function(event) {
        event.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth" });
        }
    });
});
document.addEventListener("DOMContentLoaded", function () { document.querySelector(".btn-login").addEventListener("click", function () { window.open("login.html","_blank") });

document.querySelector(".btn-signup").addEventListener("click", function () {
    window.open("signup.html","_blank");
});

});