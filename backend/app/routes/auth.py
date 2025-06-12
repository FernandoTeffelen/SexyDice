# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from app import db, bcrypt
from app.models import User, Subscription

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # ... (o código de registro continua o mesmo de antes)
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Dados ausentes."}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Este e-mail já está em uso."}), 409

    new_user = User(name=name, email=email)
    new_user.set_password(password)
    new_subscription = Subscription(user=new_user, status='inactive')

    try:
        db.session.add(new_user)
        db.session.add(new_subscription)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao registrar no banco de dados: {e}"}), 500

    return jsonify({"message": "Usuário registrado com sucesso! Faça o login."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # --- LÓGICA DE LOGIN ATUALIZADA ---

    # 1. Verifica se as credenciais são de ADMIN
    admin_email = current_app.config['ADMIN_EMAIL']
    admin_password = current_app.config['ADMIN_PASSWORD']

    if email == admin_email and password == admin_password:
        return jsonify({
            "message": "Login de administrador bem-sucedido!",
            "token": "um-token-jwt-falso-para-ADMIN",
            "role": "admin"  # Informa ao frontend que é um admin
        }), 200

    # 2. Se não for admin, procura por um usuário comum no banco de dados
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "E-mail ou senha inválidos."}), 401

    # 3. Se for um usuário comum, retorna o sucesso com a role de user
    return jsonify({
        "message": "Login bem-sucedido!",
        "token": "um-token-jwt-falso-para-USER",
        "role": "user" # Informa ao frontend que é um usuário comum
    }), 200