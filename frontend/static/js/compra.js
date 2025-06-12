document.addEventListener("DOMContentLoaded", () => {
    const payButton = document.getElementById("payButton");
    const paymentArea = document.getElementById("payment-area");
    const qrCodeImage = document.getElementById("qrCodeImage");
    const payerEmailInput = document.getElementById("payerEmail");

    // Função para tentar criar o pagamento, com N tentativas
    const tryCreatePayment = async (attemptsLeft) => {
        if (attemptsLeft === 0) {
            alert("Não foi possível gerar o QR Code após algumas tentativas. Por favor, tente novamente em um instante.");
            payButton.disabled = false;
            payButton.innerHTML = '<i class="bi bi-qr-code"></i> Pagar com PIX';
            return;
        }

        const email = payerEmailInput.value;
        if (!email || !email.includes('@')) {
            alert("Por favor, insira um e-mail válido.");
            payButton.disabled = false;
            payButton.innerHTML = '<i class="bi bi-qr-code"></i> Pagar com PIX';
            return;
        }

        try {
            const response = await fetch('/api/payment/create_pix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: 10.00, email: email, plan: 'mensal' }),
            });

            const result = await response.json();

            if (response.ok && result.success) {
                qrCodeImage.src = `data:image/png;base64,${result.qr_code_base64}`;
                paymentArea.style.display = 'block';
                payButton.closest('.card').style.display = 'none';
            } else {
                // Se falhou, tenta de novo
                console.warn(`Tentativa falhou, restam ${attemptsLeft - 1}. Erro: ${result.error}`);
                // Espera 1 segundo antes de tentar novamente
                setTimeout(() => tryCreatePayment(attemptsLeft - 1), 1000);
            }
        } catch (error) {
            console.error('Erro de rede:', error);
            // Se falhou por rede, tenta de novo
            setTimeout(() => tryCreatePayment(attemptsLeft - 1), 1000);
        }
    };

    payButton.addEventListener("click", async () => {
        payButton.disabled = true;
        payButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Gerando PIX...';
        // Inicia o processo com 3 tentativas
        tryCreatePayment(3);
    });
});