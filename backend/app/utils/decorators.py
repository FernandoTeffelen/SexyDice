from functools import wraps
from flask import session, redirect, url_for, abort

def login_required(f):
    """
    Decorator que verifica se um usuário está logado.
    Se não estiver, redireciona para a página de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main_bp.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator que verifica se o usuário logado é um admin.
    Se não for, aborta a requisição com um erro 403 (Proibido).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main_bp.login_page'))
        if session.get('role') != 'admin':
            abort(403) # Erro de acesso proibido
        return f(*args, **kwargs)
    return decorated_function