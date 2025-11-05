"""initial migration with all tables

Revision ID: ceb6a5fae282
Revises: 
Create Date: 2025-11-05 07:53:00.926946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceb6a5fae282'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Criar todas as tabelas."""
    
    # Criar tabela users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('preferred_name', sa.String(length=100), nullable=True),
        sa.Column('social_name', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('password', sa.String(length=200), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('cpf', sa.String(length=14), nullable=True),
        sa.Column('user_type', sa.String(length=20), nullable=False),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('profession', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cep', sa.String(length=10), nullable=True),
        sa.Column('street', sa.String(length=200), nullable=True),
        sa.Column('number', sa.String(length=20), nullable=True),
        sa.Column('complement', sa.String(length=100), nullable=True),
        sa.Column('neighborhood', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Criar tabela specialties
    op.create_table(
        'specialties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Criar tabela user_specialties (relacionamento muitos-para-muitos)
    op.create_table(
        'user_specialties',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialty_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['specialty_id'], ['specialties.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'specialty_id')
    )
    
    # Criar tabela appointments
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('professional_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela reviews
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('professional_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema - Remover todas as tabelas."""
    op.drop_table('reviews')
    op.drop_table('appointments')
    op.drop_table('user_specialties')
    op.drop_table('specialties')
    op.drop_table('users')

