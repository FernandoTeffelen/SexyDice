import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações da aplicação Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MERCADO_PAGO_ACCESS_TOKEN = os.environ.get('MERCADO_PAGO_ACCESS_TOKEN')
    
    # Adicionando a configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Adicionando as credenciais de admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')