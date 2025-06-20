from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class DownloadStatsResponse(BaseModel):
    success: bool
    total_downloads: int
    project_id: str
    versions: List[str]  # Fixed: API returns list of version strings, not dicts
    last_updated: str
    error: Optional[str] = None
    cached: Optional[bool] = False
    cache_timestamp: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    database_connected: Optional[bool] = None
    api_key_configured: Optional[bool] = None

class ApiCacheEntry(BaseModel):
    id: Optional[int] = None
    endpoint: str
    project_name: str
    response_data: dict
    status_code: int
    success: bool
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None 