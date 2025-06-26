from functools import wraps
from flask import g, redirect, url_for, session, request
import os
from datetime import datetime

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
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if os.environ.get('FREE_ACCESS_MODE') == 'true':
            return f(*args, **kwargs)

        if g.user is None:
            return redirect(url_for('main_bp.login_page'))
        
        if getattr(g.user, 'role', 'user') == 'admin':
            return f(*args, **kwargs)

        subscription = getattr(g.user, 'subscription', None)
        
        is_active = False
        if subscription and subscription.status == 'active':
            # Se não há data de expiração, a assinatura é permanente (ativa).
            if subscription.expires_at is None:
                is_active = True
            # Compara a data de expiração (naive UTC) com a data atual (naive UTC).
            elif subscription.expires_at > datetime.utcnow():
                is_active = True
        
        if not is_active:
            return redirect(url_for('main_bp.compra_page'))

        return f(*args, **kwargs)
    return decorated_function 