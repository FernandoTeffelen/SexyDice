"""Migracao inicial de toda a base

Revision ID: abe1c24acd22
Revises: 
Create Date: 2025-06-25 01:52:48.404838

"""
from alembic import op
import sqlalchemy as sa
# A importação abaixo não é usada neste arquivo corrigido, mas mantive para não alterar a estrutura original
from sqlalchemy.dialects import postgresql 

# revision identifiers, used by Alembic.
revision = 'abe1c24acd22'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### INÍCIO DA CORREÇÃO OBRIGATÓRIA ###
    # Primeiro, CRIAMOS as tabelas que estão faltando no banco de dados novo.
    
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('is_admin', sa.Boolean(), server_default='f', nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='f', nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('mercado_pago_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('donations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # ### FIM DA CORREÇÃO ###


def downgrade():
    # A ordem para reverter é a inversa da criação
    op.drop_table('donations')
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('users')