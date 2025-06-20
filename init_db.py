#!/usr/bin/env python3
"""
Database initialization script for jackofalltrades backend
Run this script to set up the PostgreSQL database and tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import init_database, get_db_connection
from config.settings import settings

def main():
    print("=== jackofalltrades Database Initialization ===")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"Database: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}")
    
    try:
        # Test connection first
        print("\n1. Testing database connection...")
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"✓ Connected to PostgreSQL: {version}")
        
        # Initialize tables
        print("\n2. Creating tables...")
        init_database()
        print("✓ Tables created successfully")
        
        # Verify tables
        print("\n3. Verifying table creation...")
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = [row[0] for row in cursor.fetchall()]
                print(f"✓ Tables found: {', '.join(tables)}")
        
        print("\n=== Database initialization completed successfully! ===")
        print("\nYou can now start the FastAPI server with:")
        print("  python main.py")
        
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your database credentials in .env file")
        print("3. Ensure the database exists (create with: createdb jackofalltrades)")
        print("4. Verify the user has permission to create tables")
        sys.exit(1)

if __name__ == "__main__":
    main() 