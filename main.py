import os
import requests
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="jackofalltrades Download Stats API",
    description="Backend API for fetching download statistics from Pepy.tech",
    version="1.0.0"
)

# CORS configuration
origins = [
    "https://jackofalltrades-py.netlify.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configuration
PEPPY_API_KEY = os.getenv("VITE_PEPPY_API_KEY")
PEPY_BASE_URL = "https://api.pepy.tech"
PROJECT_NAME = "jackofalltrades"

# Response models
class DownloadStatsResponse(BaseModel):
    success: bool
    total_downloads: int
    project_id: str
    versions: list
    last_updated: str
    error: str | None = None

class HealthResponse(BaseModel):
    status: str
    message: str

# Utility functions
def format_downloads(downloads: int) -> str:
    """Format download number for display"""
    if downloads >= 1000000:
        return f"{(downloads / 1000000):.1f}M"
    elif downloads >= 1000:
        return f"{(downloads / 1000):.1f}K"
    return str(downloads)

# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="jackofalltrades Download Stats API is running"
    )

@app.get("/health", response_model=HealthResponse)
def health():
    """Detailed health check"""
    api_key_status = "configured" if PEPPY_API_KEY and PEPPY_API_KEY != "your_api_key_here" else "not configured"
    
    detailed_status = {
        "api_key_exists": bool(PEPPY_API_KEY),
        "api_key_is_default": PEPPY_API_KEY == "your_api_key_here" if PEPPY_API_KEY else True,
        "api_key_value": PEPPY_API_KEY[4:8] + "..." if PEPPY_API_KEY and len(PEPPY_API_KEY) > 10 else PEPPY_API_KEY
    }
    
    return HealthResponse(
        status="healthy",
        message=f"API is running. Pepy API key: {api_key_status}. Details: {detailed_status}"
    )

@app.get("/api/downloads", response_model=DownloadStatsResponse)
def get_download_stats():
    """Fetch download statistics from Pepy.tech API"""
    
    # Debug: Print API key status
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"DEBUG: PEPPY_API_KEY exists: {bool(PEPPY_API_KEY)}")
    # print(f"DEBUG: PEPPY_API_KEY value: {PEPPY_API_KEY[4:8] + '...' if PEPPY_API_KEY and len(PEPPY_API_KEY) > 10 else PEPPY_API_KEY}")
    
    # Check if API key is configured
    if not PEPPY_API_KEY or PEPPY_API_KEY == "your_api_key_here":
        error_detail = f"Pepy.tech API key not configured. Current value: '{PEPPY_API_KEY}'. Please create a .env file in the backend directory with PEPPY_API_KEY=your_actual_key"
        print(f"ERROR: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    
    try:
        # Make request to Pepy.tech API
        headers = {
            "X-API-Key": PEPPY_API_KEY,
            "Content-Type": "application/json",
            "User-Agent": "jackofalltrades-website/1.0"
        }
        
        url = f"{PEPY_BASE_URL}/api/v2/projects/{PROJECT_NAME}"
        print(f"DEBUG: Making request to: {url}")
        # print(f"DEBUG: Headers (without API key): {dict((k, v) for i, (k, v) in enumerate(headers.items()) if i < 2)}")
        
        response = requests.get(url, headers=headers, timeout=30.0)
        
        print(f"DEBUG: Response status: {response.status_code}")
        # print(f"DEBUG: Response headers: {dict(response.headers)}")
        if response.status_code != 200:
            print(f"DEBUG: Response text: {response.text}")
        
        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Invalid Pepy.tech API key. Please check your PEPPY_API_KEY."
            )
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Package '{PROJECT_NAME}' not found on PyPI."
            )
        elif response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        elif response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Pepy.tech API error: {response.text}"
            )
        
        data = response.json()
        # print(f"DEBUG: API Response data: {data}")
        
        return DownloadStatsResponse(
            success=True,
            total_downloads=data.get("total_downloads", 0),
            project_id=data.get("id", PROJECT_NAME),
            versions=data.get("versions", []),
            last_updated=data.get("last_updated", "")
        )
        
    except requests.exceptions.Timeout as e:
        print(f"ERROR: Timeout - {str(e)}")
        raise HTTPException(
            status_code=408,
            detail="Request to Pepy.tech API timed out. Please try again."
        )
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection Error - {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Pepy.tech API: {str(e)}"
        )
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request Exception - {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Request to Pepy.tech API failed: {str(e)}"
        )
    except Exception as e:
        print(f"ERROR: Unexpected Exception - {str(e)}")
        print(f"ERROR: Exception type - {type(e)}")
        import traceback
        print(f"ERROR: Traceback - {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/downloads/formatted")
def get_formatted_download_stats():
    """Get download stats with formatted numbers"""
    stats = get_download_stats()
    
    return {
        **stats.dict(),
        "formatted_downloads": format_downloads(stats.total_downloads),
        "raw_downloads": f"{stats.total_downloads:,}"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "total_downloads": 0,
            "project_id": PROJECT_NAME,
            "versions": [],
            "last_updated": ""
        }
    )
