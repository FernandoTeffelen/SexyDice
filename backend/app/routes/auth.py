from flask import Blueprint, request, jsonify, session, current_app, url_for, flash, redirect, g
from app import db
from app.models import User, Subscription
from datetime import datetime
from app.utils.decorators import login_required

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Dados ausentes."}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Este e-mail já está em uso."}), 409
    
    new_user = User(name=data.get('name'), email=data.get('email'))
    new_user.set_password(data.get('password'))
    new_subscription = Subscription(user=new_user, status='inactive')
    
    try:
        db.session.add(new_user)
        db.session.add(new_subscription) # Adicionando explicitamente a assinatura
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"ERRO NO REGISTRO: {e}")
        return jsonify({"message": f"Erro ao registrar no banco de dados."}), 500

    return jsonify({"message": "Usuário registrado com sucesso! Faça o login."}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    admin_email = current_app.config['ADMIN_EMAIL']
    admin_password = current_app.config['ADMIN_PASSWORD']

    # 1. Verifica se é admin
    if email == admin_email and password == admin_password:
        session.clear()
        session['user_id'] = 'admin'
        session['name'] = 'Admin'
        session['email'] = admin_email
        return jsonify({"message": "Login de admin bem-sucedido!", "redirect_url": url_for('main_bp.admin_page')}), 200

    # 2. Verifica usuário comum
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session.clear()
        session['user_id'] = user.id
        session['name'] = user.name
        
        # Após o login, SEMPRE redireciona para a página inicial.
        # A lógica de proteção de rotas cuidará de direcioná-lo a partir dali.
        redirect_url = url_for('main_bp.index')
            
        return jsonify({"message": "Login bem-sucedido!", "redirect_url": redirect_url}), 200
    
    return jsonify({"message": "E-mail ou senha inválidos."}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout bem-sucedido."}), 200

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    # g.user é carregado pela função before_app_request
    if not g.user or g.user.id == 'admin':
        # Impede que o admin tente usar esta rota
        return redirect(url_for('main_bp.index'))
        
    user = User.query.get(g.user.id)
    
    name = request.form.get('name')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    if not user.check_password(current_password):
        flash('Senha atual incorreta. Nenhuma alteração foi salva.', 'danger')
        return redirect(url_for('main_bp.sua_conta_page'))

    if name != user.name:
        user.name = name
        session['name'] = name # Atualiza o nome na sessão
        flash('Nome alterado com sucesso!', 'success')

    if email != user.email:
        if User.query.filter(User.email == email, User.id != user.id).first():
            flash('Este e-mail já está em uso por outra conta.', 'warning')
        else:
            user.email = email
            flash('E-mail alterado com sucesso!', 'success')

    if new_password:
        user.set_password(new_password)
        flash('Senha alterada com sucesso!', 'success')
    
    db.session.commit()
    return redirect(url_for('main_bp.sua_conta_page'))