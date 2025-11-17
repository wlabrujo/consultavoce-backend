"""add slot_duration to users

Revision ID: add_slot_duration
Revises: 
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_slot_duration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add slot_duration column
    op.add_column('users', sa.Column('slot_duration', sa.Integer(), nullable=True, server_default='30'))
    
    # Add check constraint
    op.create_check_constraint(
        'users_slot_duration_check',
        'users',
        'slot_duration IN (15, 30, 45, 60)'
    )


def downgrade():
    # Remove check constraint
    op.drop_constraint('users_slot_duration_check', 'users', type_='check')
    
    # Remove column
    op.drop_column('users', 'slot_duration')

