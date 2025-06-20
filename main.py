import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config.settings import settings
from config.database import init_database
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    print("=== Starting jackofalltrades API ===")
    
    # Initialize database on startup
    try:
        print("Initializing database...")
        init_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        print("⚠️  API will still run but may use fallback behavior")
    
    # Check configuration
    # print(f"API Key configured: {'✓' if settings.PEPPY_API_KEY and settings.PEPPY_API_KEY != 'your_api_key_here' else '✗'}")
    # print(f"Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    # print(f"CORS origins: {settings.CORS_ORIGINS}")
    print("=== API Ready ===")
    
    yield
    
    print("=== Shutting down jackofalltrades API ===")

# Initialize FastAPI app with lifespan events
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    print(f"Unhandled exception: {exc}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.APP_VERSION.endswith("dev") else "Contact support"
        }
    )

# Health check for basic monitoring
@app.get("/ping")
async def ping():
    """Simple ping endpoint for monitoring"""
    return {"status": "ok", "message": "pong"}

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
