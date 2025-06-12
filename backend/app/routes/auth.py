from flask import Blueprint, request, jsonify, session, current_app
from app import db
from app.models import User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # O código de registro continua o mesmo, não precisa mudar
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Dados ausentes."}), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Este e-mail já está em uso."}), 409
    
    new_user = User(name=data.get('name'), email=data.get('email'))
    new_user.set_password(data.get('password'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Usuário registrado com sucesso! Faça o login."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 1. Verifica se é o admin
    admin_email = current_app.config['ADMIN_EMAIL']
    admin_password = current_app.config['ADMIN_PASSWORD']

    if email == admin_email and password == admin_password:
        session.clear() # Limpa qualquer sessão antiga
        session['user_id'] = 'admin'
        session['role'] = 'admin'
        session['name'] = 'Admin'
        return jsonify({"message": "Login de admin bem-sucedido!", "role": "admin"}), 200

    # 2. Se não for admin, verifica um usuário comum
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session.clear()
        session['user_id'] = user.id
        session['role'] = 'user'
        session['name'] = user.name
        return jsonify({"message": "Login bem-sucedido!", "role": "user"}), 200
    
    return jsonify({"message": "E-mail ou senha inválidos."}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear() # Limpa todos os dados da sessão
    return jsonify({"message": "Logout bem-sucedido."}), 200