import os # <-- Adicione esta importação no topo
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
        if not g.user or g.user.role != 'admin':
            abort(403) # Proibido
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Garante que o usuário está logado
        if not g.user:
            return redirect(url_for('main_bp.login_page'))
        
        # --- INÍCIO DA MUDANÇA ---
        # 2. Verifica se o "Modo Gratuito" está ativo no servidor
        if os.environ.get('FREE_ACCESS_MODE') == 'true':
            # Se estiver, libera o acesso para qualquer usuário logado e encerra a verificação
            return f(*args, **kwargs)
        # --- FIM DA MUDANÇA ---

        # 3. Se o modo gratuito não estiver ativo, continua com a verificação normal...
        
        # O admin sempre tem acesso
        if g.user.role == 'admin':
            return f(*args, **kwargs)
        
        # Para usuários comuns, verifica a assinatura
        subscription = g.user.subscription
        is_active = subscription and subscription.status == 'active' and (subscription.expires_at is None or subscription.expires_at > datetime.now(timezone.utc))

        if not is_active:
            return redirect(url_for('main_bp.compra_page'))
        
        return f(*args, **kwargs)
    return decorated_function