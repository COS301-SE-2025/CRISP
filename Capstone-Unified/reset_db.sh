#!/bin/bash

echo "Resetting PostgreSQL database with proper permissions..."

# Drop and recreate database with proper ownership
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS crisp_unified;
CREATE DATABASE crisp_unified OWNER crisp_user;
GRANT ALL PRIVILEGES ON DATABASE crisp_unified TO crisp_user;
\q
EOF

# Connect to the database and set up schema permissions
sudo -u postgres psql -d crisp_unified << EOF
GRANT ALL PRIVILEGES ON SCHEMA public TO crisp_user;
ALTER SCHEMA public OWNER TO crisp_user;
\q
EOF

echo "Database reset complete. Running migrations..."
python3 manage.py migrate