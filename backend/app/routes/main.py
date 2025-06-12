from flask import Blueprint, render_template, session, g
from app.models import User
from app.utils.decorators import login_required, admin_required

main_bp = Blueprint('main_bp', __name__)

# Esta função roda antes de CADA requisição e coloca o usuário logado (se houver)
# em 'g', que fica disponível para os templates.
@main_bp.app_context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        if user_id == 'admin':
            return {'current_user': {'name': 'Admin', 'role': 'admin'}}
        user = User.query.get(user_id)
        if user:
            return {'current_user': user}
    return {'current_user': None}

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login')
def login_page():
    return render_template('login.html')

# ... (outras rotas públicas como /cadastro e /compra)
@main_bp.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html')

@main_bp.route('/compra')
def compra_page():
    return render_template('compra.html')

@main_bp.route('/dado')
@login_required # Só acessa se estiver logado (qualquer tipo de usuário)
def dado_page():
    return render_template('dado.html')

@main_bp.route('/admin')
@admin_required # Só acessa se for admin
def admin_page():
    users = User.query.order_by(User.created_at.desc()).all()
    # ... (lógica de renda, etc.)
    return render_template('admin.html', users=users, daily_revenue=1.90, weekly_revenue=4.90, monthly_revenue=9.90)

@main_bp.route('/admin/dado')
@admin_required # Só acessa se for admin
def admin_dado_page():
    return render_template('admin_dado.html')

@main_bp.route('/sua_conta')
@login_required # Só acessa se estiver logado
def sua_conta_page():
    return render_template('sua_conta.html')