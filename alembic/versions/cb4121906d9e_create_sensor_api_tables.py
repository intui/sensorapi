"""Create sensor API tables

Revision ID: cb4121906d9e
Revises: 
Create Date: 2025-07-09 15:17:31.597555

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cb4121906d9e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create api_sensor_types table
    op.create_table('api_sensor_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('data_type', sa.String(length=20), nullable=True),
        sa.Column('min_value', sa.Float(), nullable=True),
        sa.Column('max_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_api_sensor_types_name', 'api_sensor_types', ['name'], unique=False)

    # Create api_locations table
    op.create_table('api_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('altitude', sa.Float(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['api_locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_locations_name', 'api_locations', ['name'], unique=False)

    # Create api_sensors table
    op.create_table('api_sensors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sensor_type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('firmware_version', sa.String(length=50), nullable=True),
        sa.Column('hardware_version', sa.String(length=50), nullable=True),
        sa.Column('sampling_interval', sa.Integer(), nullable=True),
        sa.Column('calibration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calibration_offset', sa.Float(), nullable=True),
        sa.Column('calibration_scale', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('device_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['location_id'], ['api_locations.id'], ),
        sa.ForeignKeyConstraint(['sensor_type_id'], ['api_sensor_types.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id')
    )
    op.create_index('idx_api_sensor_device_location', 'api_sensors', ['device_id', 'location_id'], unique=False)
    op.create_index('idx_api_sensor_type_location', 'api_sensors', ['sensor_type_id', 'location_id'], unique=False)
    op.create_index('ix_api_sensors_device_id', 'api_sensors', ['device_id'], unique=False)

    # Create api_sensor_readings table
    op.create_table('api_sensor_readings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sensor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('raw_value', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['sensor_id'], ['api_sensors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_reading_sensor_received', 'api_sensor_readings', ['sensor_id', 'received_at'], unique=False)
    op.create_index('idx_api_reading_sensor_timestamp', 'api_sensor_readings', ['sensor_id', 'timestamp'], unique=False)
    op.create_index('idx_api_reading_timestamp', 'api_sensor_readings', ['timestamp'], unique=False)
    op.create_index('ix_api_sensor_readings_timestamp', 'api_sensor_readings', ['timestamp'], unique=False)

    # Create api_alerts table
    op.create_table('api_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sensor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reading_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('condition_type', sa.String(length=50), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by', sa.String(length=100), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('alert_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['reading_id'], ['api_sensor_readings.id'], ),
        sa.ForeignKeyConstraint(['sensor_id'], ['api_sensors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_alert_sensor_status', 'api_alerts', ['sensor_id', 'status'], unique=False)
    op.create_index('idx_api_alert_severity_status', 'api_alerts', ['severity', 'status'], unique=False)
    op.create_index('idx_api_alert_triggered', 'api_alerts', ['triggered_at'], unique=False)


def downgrade() -> None:
    op.drop_table('api_alerts')
    op.drop_table('api_sensor_readings')
    op.drop_table('api_sensors')
    op.drop_table('api_locations')
    op.drop_table('api_sensor_types')
