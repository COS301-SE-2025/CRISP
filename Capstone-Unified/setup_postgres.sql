-- PostgreSQL setup script for CRISP
-- Run this with: psql -U postgres -h localhost -f setup_postgres.sql

-- Create database
CREATE DATABASE crisp;

-- Create user with password
CREATE USER admin WITH PASSWORD 'AdminPassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE crisp TO admin;

-- Allow user to create databases (needed for Django tests)
ALTER USER admin CREATEDB;

-- Connect to the new database and grant schema privileges
\c crisp;
GRANT ALL PRIVILEGES ON SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Verify setup
\du admin;
\l crisp;