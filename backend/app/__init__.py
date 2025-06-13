import os
from flask import Flask, jsonify # Adicione jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend'))
    app = Flask(__name__,
                template_folder=os.path.join(frontend_dir, 'templates'),
                static_folder=os.path.join(frontend_dir, 'static'))
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)

    # --- ROTA DE TESTE DE SAÚDE ---
    # Esta rota simples nos dirá se a aplicação Flask está no ar.
    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    # Registra os Blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.payment import payment_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')

    return app