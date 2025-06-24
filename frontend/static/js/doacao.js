document.addEventListener("DOMContentLoaded", () => {
    const donateButton = document.getElementById("donateButton");
    const donationFormArea = document.getElementById("donation-form-area");
    const paymentArea = document.getElementById("payment-area");
    const qrCodeImage = document.getElementById("qrCodeImage");
    const amountInput = document.getElementById("donationAmount");
    const emailInput = document.getElementById("payerEmail");
    const errorMessageDiv = document.getElementById('error-message');

    if (donateButton) {
        donateButton.addEventListener("click", async () => {
            const amount = parseFloat(amountInput.value);
            const email = emailInput.value || 'doacao@anonima.com'; // Um email padrão se o campo estiver vazio

            if (isNaN(amount) || amount < 1) {
                errorMessageDiv.textContent = "Por favor, insira um valor de doação de no mínimo R$ 1,00.";
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
                    body: JSON.stringify({ amount, email }),
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    qrCodeImage.src = `data:image/png;base64,${result.qr_code_base64}`;
                    donationFormArea.style.display = 'none';
                    paymentArea.style.display = 'block';
                } else {
                    errorMessageDiv.textContent = `Erro ao gerar PIX: ${result.error || 'Tente novamente.'}`;
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
});