from functools import wraps
from flask import g, redirect, url_for, session, request
import os
from datetime import datetime, timezone

def login_required(f):
    """
    Garante que o usuário esteja logado antes de acessar a rota.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('main_bp.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Garante que o usuário seja um administrador para acessar a rota.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or getattr(g.user, 'role', 'user') != 'admin':
            return redirect(url_for('main_bp.index'))
        return f(*args, **kwargs)
    return decorated_function


def subscription_required(f):
    """
    Garante que o usuário tenha uma assinatura ativa para acessar a rota.
    Permite o acesso se o modo de acesso gratuito estiver ativado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Se o modo gratuito está ativo, libera o acesso para todos
        if os.environ.get('FREE_ACCESS_MODE') == 'true':
            return f(*args, **kwargs)

        # Se não for usuário, vai para o login
        if g.user is None:
            return redirect(url_for('main_bp.login_page'))
        
        # Admin sempre tem acesso
        if getattr(g.user, 'role', 'user') == 'admin':
            return f(*args, **kwargs)

        # Usuário comum: verifica a assinatura
        subscription = getattr(g.user, 'subscription', None)
        
        # --- CORREÇÃO AQUI ---
        # Usamos datetime.utcnow() que é "naive", para comparar com a data do banco que também é "naive".
        is_active = subscription and subscription.status == 'active' and \
                    (subscription.expires_at is None or subscription.expires_at > datetime.utcnow())
        
        if not is_active:
            # Se não tem assinatura ativa, redireciona para a página de compra
            return redirect(url_for('main_bp.compra_page'))

        # Se tudo estiver ok, permite o acesso à rota
        return f(*args, **kwargs)
    return decorated_function
