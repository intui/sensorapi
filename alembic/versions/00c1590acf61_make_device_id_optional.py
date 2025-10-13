"""make_device_id_optional

Revision ID: 00c1590acf61
Revises: 2ad68ad3b001
Create Date: 2025-10-13 17:26:35.373355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00c1590acf61'
down_revision = '2ad68ad3b001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make device_id nullable - unique constraint already removed in previous migration
    op.alter_column('api_sensors', 'device_id',
                    existing_type=sa.String(length=100),
                    nullable=True)


def downgrade() -> None:
    # Make device_id non-nullable
    # Note: This will fail if there are NULL values in device_id
    op.alter_column('api_sensors', 'device_id',
                    existing_type=sa.String(length=100),
                    nullable=False)
