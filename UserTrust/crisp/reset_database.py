#!/usr/bin/env python3
"""
Database reset script for CRISP Trust Management System.
This script resets the database and creates fresh migrations for the integrated system.
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_NAME = os.getenv('DB_NAME', 'crisp_trust_db')
DB_USER = os.getenv('DB_USER', 'crisp_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'crisp_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

def reset_database():
    """Reset the PostgreSQL database."""
    try:
        # Connect to PostgreSQL (to the default 'postgres' database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"Dropping database {DB_NAME}...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        
        print(f"Creating database {DB_NAME}...")
        cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER}")
        
        cursor.close()
        conn.close()
        print("Database reset successfully!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    
    return True

def run_django_command(command):
    """Run a Django management command."""
    try:
        result = subprocess.run(
            ['python3', 'manage.py'] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to reset database and create migrations."""
    print("CRISP Trust Management - Database Reset")
    print("=" * 50)
    
    # Reset database
    if not reset_database():
        print("Failed to reset database. Exiting.")
        sys.exit(1)
    
    print("\nCreating fresh migrations...")
    
    # Create migrations for all apps
    commands = [
        "makemigrations user_management",
        "makemigrations trust", 
        "makemigrations",
        "migrate",
    ]
    
    for command in commands:
        if not run_django_command(command):
            print(f"Failed to run: {command}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Database reset and migrations completed successfully!")
    print("You can now run the application with fresh database schema.")

if __name__ == "__main__":
    main()