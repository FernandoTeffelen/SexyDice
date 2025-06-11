from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login')
def login_page():
    return render_template('login.html')

@main_bp.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html')

@main_bp.route('/dado')
def dado_page():
    # No futuro, esta rota será protegida para verificar se o usuário está logado e pagou
    return render_template('dado.html')