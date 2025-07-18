import os
from flask import Blueprint, render_template, session, g, redirect, url_for, request
from ..models import User, Subscription, Payment, Donation
from ..utils.decorators import login_required, admin_required, subscription_required
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from .. import db

main_bp = Blueprint('main_bp', __name__)

@main_bp.app_template_filter('localtime')
def localtime_filter(utc_dt):
    """Filtro Jinja para converter um datetime UTC para o fuso local (UTC-3)."""
    if not utc_dt:
        return "-"
    local_tz = timezone(timedelta(hours=-3))
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(local_tz)

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
    if os.environ.get('FREE_ACCESS_MODE') == 'true':
        return redirect(url_for('main_bp.dado_page'))

    if g.user and g.user.subscription and g.user.subscription.status == 'active':
        if g.user.id == 'admin':
            return redirect(url_for('main_bp.dado_page'))
        
        expires_at_aware = g.user.subscription.expires_at
        if expires_at_aware and expires_at_aware.tzinfo is None:
            expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)

        if expires_at_aware and expires_at_aware > datetime.now(timezone.utc):
            return redirect(url_for('main_bp.dado_page'))
            
    return render_template('compra.html')

@main_bp.route('/dado')
# O decorador @subscription_required foi removido daqui
def dado_page():
    """
    Renderiza a página do dado.
    Se o modo gratuito estiver ativo, permite o acesso a todos.
    Caso contrário, exige uma assinatura ativa.
    """
    # Verifica se o modo gratuito está ativo
    is_free_mode = os.environ.get('FREE_ACCESS_MODE') == 'true'

    # Se estiver em modo gratuito, libera o acesso para qualquer um
    if is_free_mode:
        return render_template('dado.html')

    # --- Se o modo gratuito NÃO estiver ativo, a lógica de assinatura é aplicada ---

    # 1. Verifica se o usuário está logado. Se não, redireciona para a página de login.
    if not g.user:
        return redirect(url_for('main_bp.login_page'))

    # 2. Verifica se o usuário tem uma assinatura ativa.
    is_subscribed = False
    # O usuário 'admin' sempre tem acesso
    if g.user.id == 'admin':
        is_subscribed = True
    elif hasattr(g.user, 'subscription') and g.user.subscription and g.user.subscription.status == 'active':
        expires_at_aware = g.user.subscription.expires_at
        if expires_at_aware:
            # Garante que a data de expiração tenha fuso horário para a comparação
            if expires_at_aware.tzinfo is None:
                expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)
            
            # Compara com a data e hora atuais (com fuso horário)
            if expires_at_aware > datetime.now(timezone.utc):
                is_subscribed = True
    
    # 3. Se estiver inscrito, mostra a página. Caso contrário, redireciona para a página de compra.
    if is_subscribed:
        return render_template('dado.html')
    else:
        return redirect(url_for('main_bp.compra_page'))


@main_bp.route('/sua_conta')
@login_required
def sua_conta_page():
    return render_template('sua_conta.html')

@main_bp.route('/admin')
@admin_required
def admin_page():
    now_utc = datetime.now(timezone.utc)
    
    active_subs_counts = dict(db.session.query(
        Subscription.plan_type,
        func.count(Subscription.id)
    ).filter(
        Subscription.status == 'active',
        Subscription.expires_at > now_utc
    ).group_by(Subscription.plan_type).all())

    renda_diaria = active_subs_counts.get('diario', 0) * 2.90
    renda_semanal = active_subs_counts.get('semanal', 0) * 4.90
    renda_mensal = active_subs_counts.get('mensal', 0) * 9.90

    total_subscription_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'approved',
        Payment.plan_type != 'doacao'
    ).scalar() or 0.0

    total_donation_revenue = db.session.query(func.sum(Donation.amount)).filter(Donation.status == 'approved').scalar() or 0.0
    
    users = User.query.order_by(User.created_at.desc()).all()
    processed_users = []

    for user in users:
        subscription = user.subscription
        is_active = False
        
        # CORREÇÃO APLICADA AQUI
        if subscription and subscription.status == 'active':
            # Garante que a data de expiração seja "aware" antes de comparar
            expires_at_aware = subscription.expires_at
            if expires_at_aware and expires_at_aware.tzinfo is None:
                expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)

            if expires_at_aware is None or expires_at_aware > now_utc:
                is_active = True

        tempo_restante_str = "-"
        if is_active and subscription.expires_at:
            # Garante que a data de expiração seja "aware" antes do cálculo
            expires_at_aware = subscription.expires_at
            if expires_at_aware.tzinfo is None:
                expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)
            
            time_left = expires_at_aware - now_utc
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
    
@main_bp.route('/admin/doacoes')
@admin_required
def admin_doacoes_page():
    donations = Donation.query.filter_by(status='approved').order_by(Donation.created_at.desc()).all()
    return render_template('admin_doacoes.html', donations=donations)

@main_bp.route('/doacao')
def doacao_page():
    return render_template('doacao.html')