import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from .config import Config

# Inicialização dos plugins fora da função para serem acessíveis globalmente
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    """Cria e configura uma instância do aplicativo Flask."""
    app = Flask(__name__, 
                static_folder='../../frontend/static', 
                template_folder='../../frontend/templates')
    
    # Carrega as configurações a partir do objeto Config
    app.config.from_object(Config)

    # Inicializa os plugins com a instância do app
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Inicializar o Flask-Migrate
    migrate = Migrate(app, db)

    with app.app_context():
        # --- CORREÇÃO AQUI ---
        # Importação corrigida para apontar para os módulos específicos
        from .routes.main import main_bp
        from .routes.auth import auth_bp
        from .routes.payment import payment_bp

        # Registro dos blueprints
        app.register_blueprint(main_bp, url_prefix='/')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(payment_bp, url_prefix='/api/payment')

        # Rota de health check
        @app.route('/health')
        def health_check():
            return "OK", 200

    return app