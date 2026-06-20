"""Add timezone column to locations table

Revision ID: e3f8f2a9b5c1
Revises: db1946cbdfc4
Create Date: 2024-09-16 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f8f2a9b5c1'
down_revision = 'db1946cbdfc4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add timezone column to api_locations table
    op.add_column('api_locations', sa.Column('timezone', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove timezone column from api_locations table
    op.drop_column('api_locations', 'timezone')