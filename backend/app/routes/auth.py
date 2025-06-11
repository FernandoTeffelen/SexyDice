from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Lógica para criar o usuário no banco de dados virá aqui
    print(f"Tentativa de registro com dados: {data}")
    # Simulação de sucesso
    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # Lógica para verificar o usuário e senha no banco de dados virá aqui
    print(f"Tentativa de login com dados: {data}")
    # Simulação de sucesso com um token falso
    return jsonify({"message": "Login bem-sucedido!", "token": "um-token-jwt-falso-para-teste"}), 200