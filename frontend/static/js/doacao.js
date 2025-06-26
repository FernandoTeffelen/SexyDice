document.addEventListener("DOMContentLoaded", () => {
    const donateButton = document.getElementById("donateButton");
    const donationFormArea = document.getElementById("donation-form-area");
    const paymentArea = document.getElementById("payment-area");
    const qrCodeImage = document.getElementById("qrCodeImage");
    const pixCodeText = document.getElementById("pixCodeText");
    const copyPixCodeBtn = document.getElementById("copyPixCodeBtn");
    const amountInput = document.getElementById("donationAmount");
    const emailInput = document.getElementById("payerEmail");
    const messageInput = document.getElementById("donationMessage");
    const errorMessageDiv = document.getElementById('error-message');
    const paymentTimerDiv = document.getElementById('payment-timer');

    let paymentPollingInterval = null;
    let paymentTimeoutInterval = null;

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
                paymentTimerDiv.className = 'alert alert-success mt-3 text-center fs-5';
                paymentTimerDiv.innerHTML = '<i class="bi bi-check-circle-fill"></i> Doação recebida! Muito obrigado!';
                // Não redireciona, apenas mostra a mensagem de sucesso.
            }
        } catch (error) {
            console.error("Erro ao verificar status da doação:", error);
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
                donationFormArea.style.display = 'block';
                errorMessageDiv.textContent = "Tempo para pagamento expirado. Por favor, gere um novo PIX.";
                errorMessageDiv.style.display = 'block';
                donateButton.disabled = false;
                donateButton.innerHTML = '<i class="bi bi-heart-fill me-2"></i> Gerar PIX para Doação';
            }
        }, 1000);
    };

    if (donateButton) {
        donateButton.addEventListener("click", async () => {
            const amount = parseFloat(amountInput.value);
            const email = emailInput.value || 'doacao.anonima@email.com';
            const message = messageInput.value;

            if (isNaN(amount) || amount < 1) {
                errorMessageDiv.textContent = "Por favor, insira um valor de no mínimo R$ 1,00.";
                errorMessageDiv.style.display = 'block';
                return;
            }

            errorMessageDiv.style.display = 'none';
            donateButton.disabled = true;
            donateButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Gerando...';

            try {
                const response = await fetch('/api/payment/create_donation_pix', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount, email, message }),
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    qrCodeImage.src = `data:image/png;base64,${result.qr_code_base64}`;
                    pixCodeText.value = result.qr_code_text;
                    donationFormArea.style.display = 'none';
                    paymentArea.style.display = 'block';

                    stopAllTimers();
                    paymentPollingInterval = setInterval(() => checkPaymentStatus(result.mercado_pago_id), 5000); // Verifica a cada 5s
                    startPaymentTimeout(600); // Timer de 10 minutos
                } else {
                    errorMessageDiv.textContent = `Erro: ${result.error || 'Tente novamente.'}`;
                    errorMessageDiv.style.display = 'block';
                    donateButton.disabled = false;
                    donateButton.innerHTML = '<i class="bi bi-heart-fill me-2"></i> Gerar PIX para Doação';
                }
            } catch (error) {
                errorMessageDiv.textContent = 'Erro de comunicação. Verifique sua conexão.';
                errorMessageDiv.style.display = 'block';
                donateButton.disabled = false;
                donateButton.innerHTML = '<i class="bi bi-heart-fill me-2"></i> Gerar PIX para Doação';
            }
        });
    }

    if (copyPixCodeBtn) {
        copyPixCodeBtn.addEventListener('click', () => {
            pixCodeText.select();
            document.execCommand('copy');
            const originalText = copyPixCodeBtn.innerHTML;
            copyPixCodeBtn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copiado!';
            setTimeout(() => { copyPixCodeBtn.innerHTML = originalText; }, 2000);
        });
    }
});