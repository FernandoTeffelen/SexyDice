"""Adiciona plan_type na tabela Subscription

Revision ID: 7480833ac22c
Revises: 71de91ed424a
Create Date: 2025-07-05 14:21:04.383405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7480833ac22c'
down_revision = '71de91ed424a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plan_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('duration_days', sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(None, ['mercado_pago_id'])
        batch_op.drop_constraint(batch_op.f('payments_subscription_id_fkey'), type_='foreignkey')
        batch_op.drop_column('subscription_id')

    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('plan_type', sa.String(length=50), nullable=True))
        batch_op.create_unique_constraint(None, ['user_id'])
        batch_op.drop_column('is_active')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=256),
               type_=sa.String(length=128),
               existing_nullable=False)
        batch_op.drop_constraint(batch_op.f('users_email_key'), type_='unique')
        batch_op.drop_constraint(batch_op.f('users_username_key'), type_='unique')
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.drop_column('username')
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.create_unique_constraint(batch_op.f('users_username_key'), ['username'], postgresql_nulls_not_distinct=False)
        batch_op.create_unique_constraint(batch_op.f('users_email_key'), ['email'], postgresql_nulls_not_distinct=False)
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=256),
               existing_nullable=False)
        batch_op.drop_column('created_at')
        batch_op.drop_column('name')

    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('plan_type')
        batch_op.drop_column('status')

    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subscription_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key(batch_op.f('payments_subscription_id_fkey'), 'subscriptions', ['subscription_id'], ['id'])
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('duration_days')
        batch_op.drop_column('plan_type')

    # ### end Alembic commands ###
