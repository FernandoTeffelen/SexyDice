from functools import wraps
from flask import session, redirect, url_for, abort, g
from datetime import datetime, timezone

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('main_bp.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or g.user.id != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('main_bp.login_page'))
        
        if g.user.id == 'admin':
            return f(*args, **kwargs)
        
        subscription = g.user.subscription
        
        is_active = subscription and subscription.status == 'active' and \
                    (subscription.expires_at is None or subscription.expires_at > datetime.now(timezone.utc))

        if not is_active:
            return redirect(url_for('main_bp.compra_page'))
        
        return f(*args, **kwargs)
    return decorated_function