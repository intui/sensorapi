#!/bin/bash

# Database initialization script for PostgreSQL
# This script will be run when the database container starts for the first time

set -e

# Create additional databases if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Create indexes for better performance
    -- These will be created by Alembic migrations, but we can prepare the database
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE sensorapi TO sensorapi;
EOSQL

echo "Database initialization completed"