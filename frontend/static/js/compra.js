// frontend/static/js/compra.js

document.addEventListener("DOMContentLoaded", () => {
    const payButton = document.getElementById("payButton");
    const paymentArea = document.getElementById("payment-area");
    const qrCodeImage = document.getElementById("qrCodeImage");
    const pixCodeText = document.getElementById("pixCodeText"); // Adicionado
    const copyPixCodeBtn = document.getElementById("copyPixCodeBtn"); // Adicionado
    const payerEmailInput = document.getElementById("payerEmail");
    const planOptions = document.querySelectorAll('input[name="plan"]'); // Adicionado
    const errorMessageDiv = document.getElementById('error-message'); // Adicionado

    // Adicionar classe 'active' ao plano selecionado
    planOptions.forEach(radio => {
        radio.addEventListener('change', () => {
            planOptions.forEach(opt => opt.closest('.plan-option').classList.remove('active'));
            radio.closest('.plan-option').classList.add('active');
        });
    });

    // Função para tentar criar o pagamento, com N tentativas
    const tryCreatePayment = async (attemptsLeft, amount, email) => { // amount e email passados como parâmetros
        if (attemptsLeft === 0) {
            errorMessageDiv.textContent = "Não foi possível gerar o QR Code após algumas tentativas. Por favor, tente novamente em um instante.";
            errorMessageDiv.style.display = 'block';
            payButton.disabled = false;
            payButton.innerHTML = '<i class="bi bi-credit-card-fill me-2"></i> Gerar PIX para o Plano Selecionado';
            return;
        }

        if (!email || !email.includes('@')) {
            errorMessageDiv.textContent = "Por favor, insira um e-mail válido.";
            errorMessageDiv.style.display = 'block';
            payButton.disabled = false;
            payButton.innerHTML = '<i class="bi bi-credit-card-fill me-2"></i> Gerar PIX para o Plano Selecionado';
            return;
        }

        try {
            const response = await fetch('/api/payment/create_pix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: amount, email: email }), // amount agora é dinâmico
            });

            const result = await response.json();

            if (response.ok && result.success) {
                qrCodeImage.src = `data:image/png;base64,${result.qr_code_base64}`;
                pixCodeText.value = result.qr_code_text; // Preenche o campo de copia e cola
                paymentArea.style.display = 'block';
                payButton.closest('.card').style.display = 'none'; // Esconde a área de seleção de planos
            } else {
                console.warn(`Tentativa falhou, restam ${attemptsLeft - 1}. Erro: ${result.error}`);
                errorMessageDiv.textContent = `Erro ao gerar QR Code: ${result.error || 'Erro desconhecido.'}`;
                errorMessageDiv.style.display = 'block';
                setTimeout(() => tryCreatePayment(attemptsLeft - 1, amount, email), 1000); // Passa amount e email novamente
            }
        } catch (error) {
            console.error('Erro de rede:', error);
            errorMessageDiv.textContent = 'Ocorreu um erro de conexão. Por favor, tente novamente.';
            errorMessageDiv.style.display = 'block';
            setTimeout(() => tryCreatePayment(attemptsLeft - 1, amount, email), 1000); // Passa amount e email novamente
        }
    };

    payButton.addEventListener("click", async () => {
        const selectedPlan = document.querySelector('input[name="plan"]:checked');
        if (!selectedPlan) {
            alert('Por favor, selecione um plano.');
            return;
        }

        const amount = parseFloat(selectedPlan.value); // Pega o valor do plano selecionado
        const email = payerEmailInput.value;

        // Limpar mensagens de erro anteriores
        errorMessageDiv.style.display = 'none';
        paymentArea.style.display = 'none';

        payButton.disabled = true;
        payButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Gerando PIX...';
        
        // Inicia o processo com 3 tentativas, passando o valor e email
        tryCreatePayment(3, amount, email);
    });

    // Lógica para copiar o código PIX
    copyPixCodeBtn.addEventListener('click', () => {
        pixCodeText.select();
        pixCodeText.setSelectionRange(0, 99999); // Para mobile
        document.execCommand('copy');
        // Feedback visual de cópia
        const originalText = copyPixCodeBtn.innerHTML;
        copyPixCodeBtn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copiado!';
        setTimeout(() => {
            copyPixCodeBtn.innerHTML = originalText;
        }, 2000);
    });
});