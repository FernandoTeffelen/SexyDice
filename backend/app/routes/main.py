from flask import Blueprint, render_template, session, g, redirect, url_for
from app.models import User
from app.utils.decorators import login_required, admin_required, subscription_required
from datetime import datetime, timezone

main_bp = Blueprint('main_bp', __name__)

@main_bp.before_app_request
def load_logged_in_user():
    """
    Carrega o usuário logado antes de CADA requisição.
    A mudança principal está aqui: garantimos que todo g.user tenha o atributo .role.
    """
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        if user_id == 'admin':
            # Para o admin, criamos um objeto com a role definida
            from types import SimpleNamespace
            g.user = SimpleNamespace(id='admin', name='Admin', role='admin', subscription=SimpleNamespace(status='active'))
        else:
            # Para o usuário comum, buscamos no DB e adicionamos o atributo role
            user = User.query.get(user_id)
            if user:
                user.role = 'user' # Adicionando o atributo que faltava
                g.user = user

@main_bp.app_context_processor
def inject_user():
    """Torna o usuário disponível para todos os templates como 'current_user'."""
    return dict(current_user=g.get('user'))

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login')
def login_page():
    return render_template('login.html')

@main_bp.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html')

@main_bp.route('/compra')
@login_required
def compra_page():
    if g.user and g.user.subscription and g.user.subscription.status == 'active':
        
        # --- MUDANÇA PRINCIPAL AQUI ---
        # Usando datetime.now(timezone.utc) para a comparação correta
        is_active_and_not_expired = (g.user.id == 'admin' or 
                                     g.user.subscription.expires_at is None or 
                                     g.user.subscription.expires_at > datetime.now(timezone.utc))

        if is_active_and_not_expired:
            return redirect(url_for('main_bp.dado_page'))
            
    return render_template('compra.html')

@main_bp.route('/dado')
@subscription_required
def dado_page():
    return render_template('dado.html')

@main_bp.route('/sua_conta')
@login_required
def sua_conta_page():
    return render_template('sua_conta.html')

@main_bp.route('/admin')
@admin_required
def admin_page():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin.html', users=users, daily_revenue=1.90, weekly_revenue=4.90, monthly_revenue=9.90)

@main_bp.route('/admin/dado')
@admin_required
def admin_dado_page():
    return render_template('admin_dado.html')