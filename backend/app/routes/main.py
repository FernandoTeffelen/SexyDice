import os
from flask import Blueprint, render_template, session, g, redirect, url_for, request
from app.models import User, Subscription, Payment, Donation
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
    # Ajustado para usar o fuso horário correto do Brasil (Brasília)
    local_tz = timezone(timedelta(hours=-3))
    # Garante que a data do banco (naive) seja tratada como UTC antes de converter
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)

@main_bp.before_app_request
def load_logged_in_user():
    """
    Carrega o usuário logado antes de cada requisição.
    """
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        if user_id == 'admin':
            from types import SimpleNamespace
            g.user = SimpleNamespace(
                id='admin', 
                name='Admin', 
                role='admin', 
                subscription=SimpleNamespace(status='active', expires_at=None)
            )
        else:
            user = User.query.get(user_id)
            if user:
                user.role = 'user' 
                g.user = user

@main_bp.app_context_processor
def inject_user():
    """Torna g.user e as configs de modo gratuito disponíveis para os templates."""
    is_free_mode = os.environ.get('FREE_ACCESS_MODE') == 'true'
    free_mode_end_date = "27/06/2025" 
    
    return dict(
        current_user=g.get('user'), 
        is_free_mode=is_free_mode,
        free_mode_end_date=free_mode_end_date,
        current_year=datetime.utcnow().year
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

    # Se não estiver no modo gratuito, a lógica continua:
    # Se o usuário já tem assinatura ativa, redireciona para o dado
    if g.user and g.user.subscription and g.user.subscription.status == 'active':
        # --- CORREÇÃO AQUI ---
        # Compara "naive" com "naive"
        if g.user.id == 'admin' or (g.user.subscription.expires_at and g.user.subscription.expires_at > datetime.utcnow()):
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
    # --- LÓGICA DE CÁLCULO DE RECEITA ---
    
    # --- CORREÇÃO AQUI ---
    # Compara "naive" com "naive"
    active_subs_counts = dict(db.session.query(
        Subscription.plan_type,
        func.count(Subscription.id)
    ).filter(
        Subscription.status == 'active',
        Subscription.expires_at > datetime.utcnow()
    ).group_by(Subscription.plan_type).all())

    renda_diaria = active_subs_counts.get('diario', 0) * 1.90
    renda_semanal = active_subs_counts.get('semanal', 0) * 4.90
    renda_mensal = active_subs_counts.get('mensal', 0) * 9.90

    total_subscription_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'approved',
        Payment.plan_type != 'doacao'
    ).scalar() or 0.0

    total_donation_revenue = db.session.query(func.sum(Donation.amount)).scalar() or 0.0
    
    # --- LÓGICA DE PROCESSAMENTO DE USUÁRIOS ---
    users = User.query.order_by(User.created_at.desc()).all()
    # --- CORREÇÃO AQUI ---
    now_utc_naive = datetime.utcnow()
    processed_users = []

    for user in users:
        subscription = user.subscription
        is_active = subscription and subscription.status == 'active' and (subscription.expires_at is None or subscription.expires_at > now_utc_naive)

        tempo_restante_str = "-"
        if is_active and subscription.expires_at:
            time_left = subscription.expires_at - now_utc_naive
            days = time_left.days
            hours = time_left.seconds // 3600
            tempo_restante_str = f"{days}d {hours}h"

        total_days_purchased = db.session.query(func.sum(Payment.duration_days)).filter_by(
            user_id=user.id, 
            status='approved'
        ).scalar() or 0

        processed_users.append({
            'user': user,
            'is_active': is_active,
            'tempo_restante': tempo_restante_str,
            'dias_totais': total_days_purchased
        })

    return render_template(
        'admin.html',
        users_data=processed_users,
        renda_diaria=renda_diaria,
        renda_semanal=renda_semanal,
        renda_mensal=renda_mensal,
        total_revenue=total_subscription_revenue,
        donation_revenue=total_donation_revenue
    )

@main_bp.route('/admin/dado')
@admin_required
def admin_dado_page():
    return render_template('admin_dado.html')
    
@main_bp.route('/admin/doacoes')
@admin_required
def admin_doacoes_page():
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template('admin_doacoes.html', donations=donations)

@main_bp.route('/doacao')
def doacao_page():
    return render_template('doacao.html')
