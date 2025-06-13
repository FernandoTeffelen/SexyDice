from functools import wraps
from flask import session, redirect, url_for, abort, g
from datetime import datetime, timezone

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main_bp.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # g.user é carregado pela função before_app_request
        if not g.user or g.user.role != 'admin':
            abort(403) # Proibido
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('main_bp.login_page'))
        
        # O objeto do admin agora também tem o atributo .subscription, então a verificação funciona
        subscription = g.user.subscription
        is_active = subscription and subscription.status == 'active' and (subscription.expires_at is None or subscription.expires_at > datetime.now(timezone.utc))

        if not is_active:
            return redirect(url_for('main_bp.compra_page'))
        
        return f(*args, **kwargs)
    return decorated_function