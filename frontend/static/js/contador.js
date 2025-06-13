document.addEventListener("DOMContentLoaded", () => {
    const timerContainer = document.getElementById("subscription-timer");
    const countdownElement = document.getElementById("countdown");

    if (timerContainer && countdownElement) {
        // Pega a data de expiração que o backend enviou
        const expiresAtISO = timerContainer.dataset.expiresAt;
        const expirationDate = new Date(expiresAtISO);

        const updateCountdown = () => {
            const now = new Date();
            const timeLeft = expirationDate - now;

            if (timeLeft <= 0) {
                countdownElement.textContent = "Expirado!";
                clearInterval(countdownInterval);
                // Força um recarregamento da página para o backend verificar o status e redirecionar
                setTimeout(() => window.location.reload(), 2000);
                return;
            }

            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            let countdownText = '';
            if (days > 0) countdownText += `${days}d `;
            if (hours > 0 || days > 0) countdownText += `${hours}h `;
            if (minutes > 0 || hours > 0 || days > 0) countdownText += `${minutes}m `;
            countdownText += `${seconds}s`;

            countdownElement.textContent = countdownText;
        };

        const countdownInterval = setInterval(updateCountdown, 1000);
        updateCountdown(); // Chama uma vez imediatamente
    }
});