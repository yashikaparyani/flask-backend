
document.getElementById("login-form")?.addEventListener("submit", function(event) {
    event.preventDefault();
    let username =document.getElementById("username").value;
    if (!username.trim()){
        alert("please enter your name");
        return;
    }
    localStorage.setItem("username", username);
    alert("Login successful!");
    window.location.href="quiz.html ";
});

document.getElementById("signup-form")?.addEventListener("submit", function(event) {
    event.preventDefault();
    let username =document.getElementById("username").value;
    if (!username.trim()){
        alert("please enter your name");
        return;
    }
    localStorage.setItem("username", username);
    alert("Sign up successful!");
    window.location.href="quiz.html ";
});