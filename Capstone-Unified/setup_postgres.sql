-- PostgreSQL setup script for CRISP
-- Run this with: psql -U postgres -h localhost -f setup_postgres.sql

-- Create database
CREATE DATABASE crisp_trust_db;

-- Create user with password
CREATE USER crisp_user WITH PASSWORD 'your-secure-database-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE crisp_trust_db TO crisp_user;

-- Allow user to create databases (needed for Django tests)
ALTER USER crisp_user CREATEDB;

-- Connect to the new database and grant schema privileges
\c crisp_trust_db;
GRANT ALL PRIVILEGES ON SCHEMA public TO crisp_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crisp_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crisp_user;

-- Verify setup
\du crisp_user;
\l crisp_trust_db;