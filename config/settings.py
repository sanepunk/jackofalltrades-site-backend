import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Configuration
    PEPPY_API_KEY = os.getenv("VITE_PEPPY_API_KEY")
    PEPY_BASE_URL = "https://api.pepy.tech"
    PROJECT_NAME = "jackofalltrades"
    
    # CORS Configuration
    CORS_ORIGINS = [
        "https://jackofalltrades-py.netlify.app",
        "http://localhost:5173"
    ]
    
    # Cache Configuration
    CACHE_EXPIRY_DAYS = 7
    API_TIMEOUT = 30.0
    
    # App Configuration
    APP_TITLE = "jackofalltrades Download Stats API"
    APP_DESCRIPTION = "Backend API for fetching download statistics from Pepy.tech with database caching"
    APP_VERSION = "1.0.0"

settings = Settings() 