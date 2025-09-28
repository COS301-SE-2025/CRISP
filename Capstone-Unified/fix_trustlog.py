"""
Simple Django management command to fix the trustlog table
"""

from django.db import connection

def check_table_structure():
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'core_trustlog' ORDER BY ordinal_position;")
        columns = cursor.fetchall()
        print("Current core_trustlog table structure:")
        for column in columns:
            print(f"  {column[0]}: {column[1]}")
        
        # Check if user_agent column exists
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'core_trustlog' AND column_name = 'user_agent';")
        user_agent_exists = cursor.fetchone()
        
        if not user_agent_exists:
            print("\nuser_agent column is missing. Adding it now...")
            cursor.execute("ALTER TABLE core_trustlog ADD COLUMN user_agent TEXT;")
            print("user_agent column added successfully!")
        else:
            print("\nuser_agent column already exists.")

if __name__ == "__main__":
    check_table_structure()