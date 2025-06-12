from flask import Blueprint, render_template
from app.models import User

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
    return render_template('dado.html')

@main_bp.route('/compra')
def compra_page():
    return render_template('compra.html')

@main_bp.route('/admin')
def admin_page():
    # Busca todos os usuários no banco, ordenados pelo mais recente
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Dados de exemplo para a renda (vamos implementar a lógica real depois)
    daily_revenue = 1.90
    weekly_revenue = 4.90
    monthly_revenue = 9.90

    return render_template('admin.html', users=users, daily_revenue=daily_revenue, weekly_revenue=weekly_revenue, monthly_revenue=monthly_revenue)

@main_bp.route('/admin/dado')
def admin_dado_page():
    # No futuro, esta rota também será protegida
    return render_template('admin_dado.html')