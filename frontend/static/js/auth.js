document.addEventListener("DOMContentLoaded", () => {
    
    // --- Lógica para o Formulário de Cadastro ---
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault(); // Impede o recarregamento da página

            // Pega os dados dos campos do formulário
            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, email, password }),
                });

                const result = await response.json();
                alert(result.message); // Mostra a mensagem de sucesso/erro do backend

                if (response.ok) {
                    window.location.href = '/login'; // Redireciona para a página de login
                }
            } catch (error) {
                console.error('Erro ao registrar:', error);
                alert('Ocorreu um erro ao tentar se registrar.');
            }
        });
    }

    // --- Lógica para o Formulário de Login ---
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault(); // Impede o recarregamento da página

            // Pega os dados dos campos do formulário
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const result = await response.json();

                if (response.ok) {
                    alert(result.message);
                    // Redireciona para a URL que o backend mandar
                    window.location.href = result.redirect_url; 
                } else {
                    alert(`Erro: ${result.message || 'Ocorreu um erro.'}`);
                }
            } catch (error) {
                console.error('Erro ao fazer login:', error);
                alert('Ocorreu um erro ao tentar fazer login.');
            }
        });
    }
});