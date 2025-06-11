from flask_bcrypt import generate_password_hash, check_password_hash

class User:
    """Representa um usuário do sistema."""
    def __init__(self, id, name, email, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        # No futuro, teremos campos como 'subscription_status', 'created_at', etc.

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        return check_password_hash(self.password_hash, password)

    # Este método será usado para criar novos usuários
    @staticmethod
    def hash_password(password):
        """Gera um hash seguro para uma senha."""
        return generate_password_hash(password).decode('utf-8')

    # No futuro, teremos métodos para buscar e salvar usuários no DB.
    # Ex: @staticmethod
    #     def find_by_email(email): ...