// frontend/static/js/auth.js
document.addEventListener("DOMContentLoaded", () => {
    
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        // ... (o código de registro continua o mesmo)
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password }),
                });
                const result = await response.json();
                alert(result.message);
                if (response.ok) {
                    window.location.href = '/login';
                }
            } catch (error) {
                console.error('Erro ao registrar:', error);
                alert('Ocorreu um erro ao tentar se registrar.');
            }
        });
    }

    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password }),
                });

                const result = await response.json();

                if (response.ok) {
                    localStorage.setItem('authToken', result.token);
                    alert(result.message);

                    // --- LÓGICA DE REDIRECIONAMENTO ATUALIZADA ---
                    if (result.role === 'admin') {
                        window.location.href = '/admin'; // Redireciona para o painel de admin
                    } else {
                        window.location.href = '/dado'; // Redireciona para a página do jogo
                    }
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