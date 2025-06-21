from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from config.settings import settings
from config.database import get_latest_cached_response, cleanup_old_cache, cleanup_all_cache, get_db_connection, db_config
from models.schemas import DownloadStatsResponse, HealthResponse
from services.pepy_service import pepy_service
from .api_authorization import api_key_auth

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="jackofalltrades Download Stats API is running",
        database_connected=True if db_config.host else False,
        api_key_configured=True if settings.PEPPY_API_KEY else False
    )

@router.get("/health", response_model=HealthResponse)
def health():
    """Detailed health check with database and API key status"""
    # Check API key status
    api_key_configured = bool(settings.PEPPY_API_KEY and settings.PEPPY_API_KEY != "your_api_key_here")
    
    # Check database connection
    database_connected = False
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                database_connected = True
    except Exception as e:
        print(f"Database health check failed: {e}")
    
    status = "healthy" if (api_key_configured or database_connected) else "degraded"
    
    return HealthResponse(
        status=status,
        message=f"API Status: {'✓' if api_key_configured else '✗'} API Key, {'✓' if database_connected else '✗'} Database",
        database_connected=database_connected,
        api_key_configured=api_key_configured
    )

@router.get("/api/downloads", response_model=DownloadStatsResponse)
def get_download_stats():
    """
    Fetch download statistics from Pepy.tech API with database caching fallback
    
    Logic:
    1. Make API request to Pepy.tech
    2. If status_code == 200: Store in database and return data to frontend
    3. If status_code != 200: Fetch most recent data from database and return to frontend
    """
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=== Download Stats Request ===")
    
    try:
        result = pepy_service.get_download_stats()
        
        if result.cached:
            print(f"SUCCESS: Returned cached data from {result.cache_timestamp}")
        else:
            print("SUCCESS: Returned fresh API data")
            
        return result
        
    except Exception as e:
        print(f"CRITICAL ERROR in get_download_stats: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Final fallback - try to get any cached data
        try:
            cached_data = get_latest_cached_response(settings.PROJECT_NAME, "downloads")
            if cached_data:
                response_data = cached_data["response_data"]
                return DownloadStatsResponse(
                    success=True,
                    total_downloads=response_data.get("total_downloads", 0),
                    project_id=response_data.get("id", settings.PROJECT_NAME),
                    versions=response_data.get("versions", []),
                    last_updated=response_data.get("last_updated", ""),
                    cached=True,
                    cache_timestamp=cached_data["created_at"].isoformat(),
                    error=f"Service error, using cached data: {str(e)}"
                )
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/api/downloads/formatted")
def get_formatted_download_stats():
    """Get download stats with formatted numbers"""
    stats = get_download_stats()
    
    return {
        **stats.dict(),
        "formatted_downloads": pepy_service.format_downloads(stats.total_downloads),
        "raw_downloads": f"{stats.total_downloads:,}"
    }

@router.get("/api/cache/status")
def get_cache_status(api_key: str = Depends(api_key_auth)):
    """Get cache status and recent entries"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Get cache statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful_entries,
                        COUNT(CASE WHEN success = false THEN 1 END) as failed_entries,
                        MAX(created_at) as latest_entry,
                        MIN(created_at) as oldest_entry
                    FROM api_cache
                """)
                stats = cursor.fetchone()
                
                # Get recent entries
                cursor.execute("""
                    SELECT endpoint, status_code, success, created_at
                    FROM api_cache 
                    ORDER BY created_at DESC 
                    LIMIT 2
                """)
                recent_entries = cursor.fetchall()
        
        return {
            "cache_stats": dict(stats) if stats else {},
            "recent_entries": [dict(entry) for entry in recent_entries]
        }
    except Exception as e:
        return {"error": f"Failed to get cache status: {e}"}

@router.post("/api/cache/cleanup")
def cleanup_cache(api_key: str = Depends(api_key_auth), days_old: int = 7):
    """Clean up old cache entries"""
    try:
        deleted_count = cleanup_old_cache(days_old)
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} entries older than {days_old} days"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cache cleanup failed: {e}"
        )

@router.post("/api/cache/cleanup/all")
def cleanup_all_cache_entries(api_key: str = Depends(api_key_auth)):
    """Delete all cache entries"""
    try:
        deleted_count = cleanup_all_cache()
        return {
            "success": True,
            "message": f"Deleted all {deleted_count} cache entries"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cache cleanup failed: {e}"
        )

@router.get("/api/database/test")
def test_database_connection(api_key: str = Depends(api_key_auth)):
    """Test database connection and operations"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Test basic query
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                
                # Test table exists
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'api_cache'
                """)
                table_exists = cursor.fetchone() is not None
                
        return {
            "success": True,
            "postgresql_version": version,
            "api_cache_table_exists": table_exists,
            "connection_params": {
                "host": db_config.host,
                "port": db_config.port,
                "database": db_config.database,
                "user": db_config.user
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "connection_params": {
                "host": db_config.host,
                "port": db_config.port,
                "database": db_config.database,
                "user": db_config.user
            }
        } 