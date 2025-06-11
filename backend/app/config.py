import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Config:
    """Configurações da aplicação Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MERCADO_PAGO_ACCESS_TOKEN = os.environ.get('MERCADO_PAGO_ACCESS_TOKEN')
    
    # Futuramente, adicionaremos a configuração do banco de dados aqui
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')