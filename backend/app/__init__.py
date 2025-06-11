from flask import Flask
from flask_bcrypt import Bcrypt
from .config import Config

# Instancia as extensões
bcrypt = Bcrypt()

def create_app(config_class=Config):
    """Cria e configura uma instância da aplicação Flask."""
    app = Flask(__name__,
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    
    app.config.from_object(config_class)

    # Inicializa as extensões com a app
    bcrypt.init_app(app)

    # Registra os Blueprints (nossos arquivos de rotas)
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.payment import payment_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')

    return app