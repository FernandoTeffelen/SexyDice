from app import db, bcrypt

# Todos os modelos agora vivem neste único arquivo.

class User(db.Model):
    """Modelo da tabela de Usuários."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relacionamentos com as outras classes que estão no mesmo arquivo
    subscription = db.relationship('Subscription', backref='user', uselist=False, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Cria o hash da senha."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

class Subscription(db.Model):
    """Modelo da tabela de Assinaturas."""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='inactive')
    expires_at = db.Column(db.DateTime, nullable=True)
    plan_type = db.Column(db.String(50), nullable=True) # <-- NOVA COLUNA AQUI
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

class Payment(db.Model):
    """Modelo da tabela de Pagamentos."""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mercado_pago_id = db.Column(db.BigInteger, unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())