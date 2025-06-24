import os
from flask import Blueprint, render_template, session, g, redirect, url_for
from app.models import User, Subscription, Payment
from app.utils.decorators import login_required, admin_required, subscription_required
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from app import db

main_bp = Blueprint('main_bp', __name__)

@main_bp.app_template_filter('localtime')
def localtime_filter(utc_dt):
    """Filtro Jinja para converter um datetime UTC para o fuso local (UTC-3)."""
    if not utc_dt:
        return "-"
    local_tz = timezone(timedelta(hours=-3))
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)

@main_bp.before_app_request
def load_logged_in_user():
    """
    Carrega o usuário logado antes de cada requisição.
    A mudança principal está aqui: garantimos que todo g.user tenha o atributo .role.
    """
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        if user_id == 'admin':
            # Para o admin, criamos um objeto com a role definida
            from types import SimpleNamespace
            g.user = SimpleNamespace(
                id='admin', 
                name='Admin', 
                role='admin', 
                subscription=SimpleNamespace(status='active', expires_at=None)
            )
        else:
            # Para o usuário comum, buscamos no DB e adicionamos o atributo role
            user = User.query.get(user_id)
            if user:
                user.role = 'user' # Adicionando o atributo que faltava dinamicamente
                g.user = user

@main_bp.app_context_processor
def inject_user():
    """Torna g.user e as configs de modo gratuito disponíveis para os templates."""
    is_free_mode = os.environ.get('FREE_ACCESS_MODE') == 'true'
    
    # Defina aqui a data final da sua promoção
    free_mode_end_date = "01/08/2025" 
    
    return dict(
        current_user=g.get('user'), 
        is_free_mode=is_free_mode,
        free_mode_end_date=free_mode_end_date # <-- Variável adicionada
    )

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
    # Se o modo gratuito estiver ativo, redireciona o usuário direto para o jogo.
    if os.environ.get('FREE_ACCESS_MODE') == 'true':
        return redirect(url_for('main_bp.dado_page'))

    # Se não estiver no modo gratuito, a lógica que já tínhamos continua:
    # Se o usuário já tem assinatura ativa, redireciona para o dado
    if g.user and g.user.subscription and g.user.subscription.status == 'active':
        if g.user.id == 'admin' or (g.user.subscription.expires_at and g.user.subscription.expires_at > datetime.now(timezone.utc)):
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
    
    # --- Lógica de Cálculo de Receita ---
    now_utc = datetime.now(timezone.utc)

    # Contagem de assinaturas ativas agrupadas por plano
    active_subs_counts = dict(db.session.query(
        Subscription.plan_type,
        func.count(Subscription.id)
    ).filter(
        Subscription.status == 'active',
        Subscription.expires_at > now_utc
    ).group_by(Subscription.plan_type).all())

    # Cálculo da renda por tipo de plano ativo
    renda_diaria = active_subs_counts.get('diario', 0) * 1.90
    renda_semanal = active_subs_counts.get('semanal', 0) * 4.90
    renda_mensal = active_subs_counts.get('mensal', 0) * 9.90

    # Cálculo da receita total de todos os pagamentos aprovados
    total_revenue_result = db.session.query(func.sum(Payment.amount)).filter_by(status='approved').scalar()
    total_revenue = float(total_revenue_result) if total_revenue_result is not None else 0.0

    return render_template(
        'admin.html',
        users=users,
        renda_diaria=renda_diaria,
        renda_semanal=renda_semanal,
        renda_mensal=renda_mensal,
        total_revenue=total_revenue
    )

@main_bp.route('/admin/dado')
@admin_required
def admin_dado_page():
    return render_template('admin_dado.html')