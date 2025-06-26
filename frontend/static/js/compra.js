document.addEventListener("DOMContentLoaded", () => {
    const buyButtons = document.querySelectorAll(".buy-btn");
    const plansArea = document.getElementById("plans-area");
    const paymentArea = document.getElementById("payment-area");
    const successArea = document.getElementById("success-area"); // <-- Pega a nova área
    const successPlanMessage = document.getElementById("success-plan-message"); // <-- Pega o parágrafo da mensagem
    const qrCodeImage = document.getElementById("qrCodeImage");
    const pixCodeText = document.getElementById("pixCodeText");
    const copyPixCodeBtn = document.getElementById("copyPixCodeBtn");
    const errorMessageDiv = document.getElementById('error-message');
    const paymentTimerDiv = document.getElementById('payment-timer');

    let paymentPollingInterval = null;
    let paymentTimeoutInterval = null;
    let selectedPlanType = null; // <-- Variável para guardar o plano escolhido

    const stopAllTimers = () => {
        if (paymentPollingInterval) clearInterval(paymentPollingInterval);
        if (paymentTimeoutInterval) clearInterval(paymentTimeoutInterval);
    };

    const checkPaymentStatus = async (paymentId) => {
        try {
            const response = await fetch(`/api/payment/status/${paymentId}`);
            if (!response.ok) return;

            const result = await response.json();
            if (result.status === 'approved') {
                stopAllTimers();
                
                // LÓGICA ATUALIZADA AQUI
                paymentArea.style.display = 'none'; // Esconde a área de pagamento
                successArea.style.display = 'block'; // Mostra a área de sucesso

                // Define a mensagem personalizada
                const messages = {
                    'diario': 'Aproveite suas 24 horas de acesso!',
                    'semanal': 'Aproveite sua semana de acesso!',
                    'mensal': 'Aproveite seu mês de acesso!'
                };
                successPlanMessage.textContent = messages[selectedPlanType] || 'Aproveite seu acesso!';
            }
        } catch (error) {
            console.error("Erro ao verificar status do pagamento:", error);
        }
    };
    
    const startPaymentTimeout = (durationInSeconds = 600) => { // 10 minutos
        let duration = durationInSeconds;
        paymentTimerDiv.style.display = 'block';
        paymentTimerDiv.className = 'alert alert-warning mt-3 text-center fs-5';

        paymentTimeoutInterval = setInterval(() => {
            let minutes = parseInt(duration / 60, 10);
            let seconds = parseInt(duration % 60, 10);
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
            paymentTimerDiv.innerHTML = `<i class="bi bi-clock"></i> Tempo para pagar: ${minutes}:${seconds}`;

            if (--duration < 0) {
                stopAllTimers();
                paymentArea.style.display = 'none';
                plansArea.style.display = 'block';
                errorMessageDiv.textContent = "Tempo para pagamento expirado. Por favor, escolha um plano novamente.";
                errorMessageDiv.style.display = 'block';
            }
        }, 1000);
    };

    buyButtons.forEach(button => {
        button.addEventListener("click", async () => {
            const amount = button.dataset.amount;
            const planType = button.dataset.plan;
            const durationDays = button.dataset.duration;

            selectedPlanType = planType; // <-- Salva o tipo do plano escolhido

            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Gerando...';

            try {
                const response = await fetch('/api/payment/create_pix', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount, planType, durationDays }),
                });
                const result = await response.json();

                if (response.ok) {
                    qrCodeImage.src = `data:image/png;base64,${result.qr_code_base64}`;
                    pixCodeText.value = result.qr_code_text;
                    plansArea.style.display = 'none';
                    paymentArea.style.display = 'block';
                    
                    stopAllTimers();
                    paymentPollingInterval = setInterval(() => checkPaymentStatus(result.mercado_pago_id), 5000);
                    startPaymentTimeout();
                } else {
                    errorMessageDiv.textContent = `Erro: ${result.error || 'Tente novamente.'}`;
                    errorMessageDiv.style.display = 'block';
                }
            } catch (error) {
                errorMessageDiv.textContent = 'Erro de comunicação. Verifique sua conexão.';
                errorMessageDiv.style.display = 'block';
            } finally {
                button.disabled = false;
                // Reseta o texto do botão com base no tipo de plano
                const buttonText = {
                    'diario': 'Comprar Agora',
                    'semanal': 'Mais Popular',
                    'mensal': 'Comprar Agora'
                };
                button.innerHTML = buttonText[planType];
            }
        });
    });

    copyPixCodeBtn.addEventListener('click', () => {
        pixCodeText.select();
        document.execCommand('copy');
        const originalText = copyPixCodeBtn.innerHTML;
        copyPixCodeBtn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copiado!';
        setTimeout(() => { copyPixCodeBtn.innerHTML = originalText; }, 2000);
    });
});