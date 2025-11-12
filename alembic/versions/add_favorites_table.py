"""add favorites table

Revision ID: add_favorites_001
Revises: ceb6a5fae282
Create Date: 2025-11-11 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_favorites_001'
down_revision = 'ceb6a5fae282'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade schema - Criar tabela favorites."""
    op.create_table(
        'favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('professional_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['professional_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=False)


def downgrade():
    """Downgrade schema - Remover tabela favorites."""
    op.drop_index(op.f('ix_favorites_id'), table_name='favorites')
    op.drop_table('favorites')

