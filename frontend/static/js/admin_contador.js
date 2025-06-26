document.addEventListener("DOMContentLoaded", () => {
    // Seleciona todas as células da tabela que têm o atributo 'data-expires-at'
    const timerElements = document.querySelectorAll("td[data-expires-at]");

    timerElements.forEach(element => {
        const expiresAtISO = element.dataset.expiresAt;
        
        // Se não houver data de expiração, não faz nada
        if (!expiresAtISO) {
            return;
        }

        const expirationDate = new Date(expiresAtISO);
        const userId = element.id.split('-')[1]; // Pega o ID do usuário a partir do ID do elemento (ex: "timer-123")
        const statusElement = document.getElementById(`status-${userId}`);

        const updateCountdown = () => {
            const now = new Date();
            const timeLeft = expirationDate - now;

            if (timeLeft <= 0) {
                element.textContent = "Expirado";
                if (statusElement) {
                    statusElement.textContent = "Desativado";
                    statusElement.classList.remove("bg-success");
                    statusElement.classList.add("bg-danger");
                }
                // Para o intervalo para este elemento específico
                clearInterval(countdownInterval);
                return;
            }

            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));

            // Monta a string de tempo restante
            let countdownText = '';
            if (days > 0) countdownText += `${days}d `;
            if (hours > 0 || days > 0) countdownText += `${hours}h `;
            // Mostra minutos apenas se o tempo for menor que 1 dia
            if (days === 0) countdownText += `${minutes}m`;
            
            element.textContent = countdownText.trim();
        };

        // Inicia um intervalo de atualização para cada timer individualmente
        const countdownInterval = setInterval(updateCountdown, 60000); // Atualiza a cada minuto para não sobrecarregar
        updateCountdown(); // Chama uma vez imediatamente para mostrar o valor correto no carregamento
    });
});