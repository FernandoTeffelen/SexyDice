document.addEventListener("DOMContentLoaded", () => {
    const payButton = document.getElementById("payButton");
    const paymentArea = document.getElementById("payment-area");
    const qrCodeImage = document.getElementById("qrCodeImage");
    const pixCodeText = document.getElementById("pixCodeText");
    const copyPixCodeBtn = document.getElementById("copyPixCodeBtn");
    const planOptions = document.querySelectorAll('input[name="plan"]');
    const errorMessageDiv = document.getElementById('error-message');
    const planSelectionCard = payButton.closest('.card');

    let paymentPollingInterval = null;
    let paymentTimeoutInterval = null;

    // Função para parar todos os timers
    const stopAllTimers = () => {
        if (paymentPollingInterval) clearInterval(paymentPollingInterval);
        if (paymentTimeoutInterval) clearInterval(paymentTimeoutInterval);
    };

    // Função para checar o status do pagamento no backend
    const checkPaymentStatus = async (paymentId) => {
        try {
            const response = await fetch(`/api/payment/status/${paymentId}`);
            if (!response.ok) return;
            
            const result = await response.json();
            if (result.status === 'approved') {
                console.log("Pagamento aprovado! Redirecionando...");
                stopAllTimers();
                paymentTimerDiv.className = 'alert alert-success mt-3 text-center fs-5';
                paymentTimerDiv.innerHTML = '<i class="bi bi-check-circle-fill"></i> Pagamento Aprovado! Redirecionando...';
                
                setTimeout(() => {
                    window.location.href = '/dado';
                }, 2000);
            }
        } catch (error) {
            console.error("Erro ao verificar status do pagamento:", error);
        }
    };

    // Função para iniciar o timer de 10 minutos
    const startPaymentTimeout = () => {
        let duration = 600; // 10 minutos em segundos
        const paymentTimerDiv = document.getElementById('payment-timer');
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
                paymentTimerDiv.style.display = 'none';
                errorMessageDiv.textContent = "Tempo para pagamento expirado. Por favor, gere um novo PIX.";
                errorMessageDiv.style.display = 'block';
                planSelectionCard.style.display = 'block';
                payButton.disabled = false;
                payButton.innerHTML = '<i class="bi bi-credit-card-fill me-2"></i> Gerar PIX para o Plano Selecionado';
            }
        }, 1000);
    };

    // Função principal para criar o pagamento, com N tentativas
    const tryCreatePayment = async (attemptsLeft, payload) => {
        if (attemptsLeft === 0) {
            errorMessageDiv.textContent = "Não foi possível gerar o QR Code após algumas tentativas. Por favor, tente novamente em um instante.";
            errorMessageDiv.style.display = 'block';
            payButton.disabled = false;
            payButton.innerHTML = '<i class="bi bi-credit-card-fill me-2"></i> Gerar PIX para o Plano Selecionado';
            return;
        }

        try {
            const response = await fetch('/api/payment/create_pix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const result = await response.json();

            if (response.ok && result.success) {
                qrCodeImage.src = `data:image/png;base64,${result.qr_code_base64}`;
                pixCodeText.value = result.qr_code_text;
                paymentArea.style.display = 'block';
                planSelectionCard.style.display = 'none';

                stopAllTimers();
                paymentPollingInterval = setInterval(() => checkPaymentStatus(result.mercado_pago_id), 3000);
                startPaymentTimeout();
            } else {
                console.warn(`Tentativa falhou, restam ${attemptsLeft - 1}. Erro: ${result.error}`);
                setTimeout(() => tryCreatePayment(attemptsLeft - 1, payload), 1000);
            }
        } catch (error) {
            console.error('Erro de rede:', error);
            setTimeout(() => tryCreatePayment(attemptsLeft - 1, payload), 1000);
        }
    };

    // Adiciona o listener principal ao botão de pagar
    if (payButton) {
        payButton.addEventListener("click", async () => {
            const selectedPlan = document.querySelector('input[name="plan"]:checked');
            if (!selectedPlan) {
                alert('Por favor, selecione um plano.');
                return;
            }

            const payload = {
                amount: parseFloat(selectedPlan.value),
                planType: selectedPlan.dataset.planType,
                durationDays: parseInt(selectedPlan.dataset.days, 10)
            };

            errorMessageDiv.style.display = 'none';
            payButton.disabled = true;
            payButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Gerando PIX...';
            
            tryCreatePayment(3, payload);
        });
    }

    // Adiciona listener para o botão de copiar o código PIX
    if (copyPixCodeBtn) {
        copyPixCodeBtn.addEventListener('click', () => {
            pixCodeText.select();
            pixCodeText.setSelectionRange(0, 99999);
            document.execCommand('copy');
            
            const originalText = copyPixCodeBtn.innerHTML;
            copyPixCodeBtn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copiado!';
            setTimeout(() => {
                copyPixCodeBtn.innerHTML = originalText;
            }, 2000);
        });
    }

    // Adiciona listener para a seleção de planos
    if (planOptions) {
        planOptions.forEach(radio => {
            radio.addEventListener('change', () => {
                planOptions.forEach(opt => opt.closest('.plan-option').classList.remove('active'));
                radio.closest('.plan-option').classList.add('active');
            });
        });
    }
});