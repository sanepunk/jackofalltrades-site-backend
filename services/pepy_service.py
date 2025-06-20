import requests
from typing import Dict, Any, Optional
from datetime import datetime
from config.settings import settings
from config.database import store_api_response, get_latest_cached_response
from models.schemas import DownloadStatsResponse

class PepyService:
    def __init__(self):
        self.base_url = settings.PEPY_BASE_URL
        self.api_key = settings.PEPPY_API_KEY
        self.project_name = settings.PROJECT_NAME
        self.timeout = settings.API_TIMEOUT

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "jackofalltrades-website/1.0"
        }
        
        if self.api_key and self.api_key != "your_api_key_here":
            headers["X-API-Key"] = self.api_key
            
        return headers

    def _make_api_request(self, endpoint: str) -> requests.Response:
        """Make API request to Pepy.tech"""
        url = f"{self.base_url}/api/v2/projects/{self.project_name}"
        headers = self._get_headers()
        
        print(f"DEBUG: Making request to: {url}")
        print(f"DEBUG: API key configured: {bool(self.api_key and self.api_key != 'your_api_key_here')}")
        
        response = requests.get(url, headers=headers, timeout=self.timeout)
        
        print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response text: {response.text}")
            
        return response

    def get_download_stats(self) -> DownloadStatsResponse:
        """
        Fetch download statistics with database caching fallback
        
        Logic:
        1. Make API request to Pepy.tech
        2. If status_code == 200: Store in database and return data
        3. If status_code != 200: Fetch most recent data from database and return
        """
        endpoint = "downloads"
        
        try:
            # Check if API key is configured
            if not self.api_key or self.api_key == "your_api_key_here":
                print("WARNING: API key not configured, trying cached data only")
                cached_data = get_latest_cached_response(self.project_name, endpoint)
                
                if cached_data:
                    return self._create_response_from_cache(cached_data)
                else:
                    return DownloadStatsResponse(
                        success=False,
                        total_downloads=0,
                        project_id=self.project_name,
                        versions=[],
                        last_updated="",
                        error="API key not configured and no cached data available"
                    )

            # Make API request
            response = self._make_api_request(endpoint)
            
            if response.status_code == 200:
                # Successful response - store in database and return
                data = response.json()
                
                # Store successful response in database
                store_api_response(
                    project_name=self.project_name,
                    endpoint=endpoint,
                    response_data=data,
                    status_code=response.status_code,
                    success=True
                )
                
                return DownloadStatsResponse(
                    success=True,
                    total_downloads=data.get("total_downloads", 0),
                    project_id=data.get("id", self.project_name),
                    versions=data.get("versions", []),
                    last_updated=data.get("last_updated", ""),
                    cached=False
                )
            
            else:
                # Failed response - try to get cached data
                print(f"API request failed with status {response.status_code}, trying cached data")
                
                # Store failed response for debugging
                try:
                    error_data = response.json() if response.text else {"error": "No response content"}
                except:
                    error_data = {"error": response.text or "Unknown error"}
                
                store_api_response(
                    project_name=self.project_name,
                    endpoint=endpoint,
                    response_data=error_data,
                    status_code=response.status_code,
                    success=False
                )
                
                # Get most recent successful cached response
                cached_data = get_latest_cached_response(self.project_name, endpoint)
                
                if cached_data:
                    return self._create_response_from_cache(cached_data, 
                                                          f"API error (status {response.status_code}), using cached data")
                else:
                    return self._create_error_response(response.status_code, response.text)

        except requests.exceptions.Timeout:
            print("API request timed out, trying cached data")
            return self._handle_api_failure("Request timed out", endpoint)
            
        except requests.exceptions.ConnectionError:
            print("API connection error, trying cached data")
            return self._handle_api_failure("Connection error", endpoint)
            
        except requests.exceptions.RequestException as e:
            print(f"API request exception: {e}, trying cached data")
            return self._handle_api_failure(f"Request error: {str(e)}", endpoint)
            
        except Exception as e:
            print(f"Unexpected error: {e}, trying cached data")
            return self._handle_api_failure(f"Unexpected error: {str(e)}", endpoint)

    def _create_response_from_cache(self, cached_data: Dict[str, Any], 
                                   error_message: Optional[str] = None) -> DownloadStatsResponse:
        """Create response from cached data"""
        response_data = cached_data["response_data"]
        
        return DownloadStatsResponse(
            success=True,
            total_downloads=response_data.get("total_downloads", 0),
            project_id=response_data.get("id", self.project_name),
            versions=response_data.get("versions", []),
            last_updated=response_data.get("last_updated", ""),
            cached=True,
            cache_timestamp=cached_data["created_at"].isoformat(),
            error=error_message
        )

    def _handle_api_failure(self, error_message: str, endpoint: str) -> DownloadStatsResponse:
        """Handle API failure by trying to get cached data"""
        cached_data = get_latest_cached_response(self.project_name, endpoint)
        
        if cached_data:
            return self._create_response_from_cache(cached_data, error_message)
        else:
            return DownloadStatsResponse(
                success=False,
                total_downloads=0,
                project_id=self.project_name,
                versions=[],
                last_updated="",
                error=f"{error_message}. No cached data available."
            )

    def _create_error_response(self, status_code: int, response_text: str) -> DownloadStatsResponse:
        """Create error response based on status code"""
        error_messages = {
            401: "Invalid API key",
            404: f"Package '{self.project_name}' not found on PyPI",
            429: "Rate limit exceeded",
            500: "Pepy.tech server error",
            503: "Pepy.tech service unavailable"
        }
        
        error_message = error_messages.get(status_code, f"API error (status {status_code})")
        
        return DownloadStatsResponse(
            success=False,
            total_downloads=0,
            project_id=self.project_name,
            versions=[],
            last_updated="",
            error=f"{error_message}: {response_text}"
        )

    def format_downloads(self, downloads: int) -> str:
        """Format download number for display"""
        if downloads >= 1000000:
            return f"{(downloads / 1000000):.1f}M"
        elif downloads >= 1000:
            return f"{(downloads / 1000):.1f}K"
        return str(downloads)

# Create service instance
pepy_service = PepyService() 