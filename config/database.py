import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Dict, Any
import json
from datetime import datetime

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "jackofalltrades")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        
    def get_connection_params(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "cursor_factory": RealDictCursor
        }

db_config = DatabaseConfig()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(**db_config.get_connection_params())
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_database():
    """Initialize database tables"""
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS api_cache (
        id SERIAL PRIMARY KEY,
        endpoint VARCHAR(255) NOT NULL,
        project_name VARCHAR(100) NOT NULL,
        response_data JSONB NOT NULL,
        status_code INTEGER NOT NULL,
        success BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_api_cache_project_endpoint 
    ON api_cache (project_name, endpoint);
    
    CREATE INDEX IF NOT EXISTS idx_api_cache_created_at 
    ON api_cache (created_at DESC);
    
    CREATE INDEX IF NOT EXISTS idx_api_cache_success 
    ON api_cache (success, created_at DESC);
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_tables_sql)
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

def store_api_response(project_name: str, endpoint: str, response_data: dict, 
                      status_code: int, success: bool = True) -> bool:
    """Store API response in database cache"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO api_cache 
                    (endpoint, project_name, response_data, status_code, success, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    endpoint,
                    project_name,
                    json.dumps(response_data),
                    status_code,
                    success,
                    datetime.now()
                ))
        return True
    except Exception as e:
        print(f"Error storing API response: {e}")
        return False

def get_latest_cached_response(project_name: str, endpoint: str) -> Optional[Dict[str, Any]]:
    """Get most recent successful cached response"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT response_data, created_at, status_code
                    FROM api_cache 
                    WHERE project_name = %s 
                    AND endpoint = %s 
                    AND success = true 
                    AND status_code = 200
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                cursor.execute(query, (project_name, endpoint))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "response_data": json.loads(result["response_data"]) if isinstance(result["response_data"], str) else result["response_data"],
                        "created_at": result["created_at"],
                        "status_code": result["status_code"]
                    }
        return None
    except Exception as e:
        print(f"Error fetching cached response: {e}")
        return None

def cleanup_old_cache(days_old: int = 7):
    """Clean up cache entries older than specified days"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    DELETE FROM api_cache 
                    WHERE created_at < NOW() - INTERVAL '%s days'
                """
                cursor.execute(query, (days_old,))
                deleted_count = cursor.rowcount
        print(f"Cleaned up {deleted_count} old cache entries")
        return deleted_count
    except Exception as e:
        print(f"Error cleaning up cache: {e}")
        return 0 