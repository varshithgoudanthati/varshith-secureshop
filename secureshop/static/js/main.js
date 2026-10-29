// SecureShop Client-Side Interactions

document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss standard alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Lab Credential Quick-Filler
    window.fillCredentials = function(username, password) {
        const userInput = document.getElementById("username");
        const passInput = document.getElementById("password");
        if (userInput && passInput) {
            userInput.value = username;
            passInput.value = password;
            // Trigger visual feedback
            userInput.classList.add("is-valid");
            passInput.classList.add("is-valid");
            setTimeout(() => {
                userInput.classList.remove("is-valid");
                passInput.classList.remove("is-valid");
            }, 1500);
        }
    };
});
