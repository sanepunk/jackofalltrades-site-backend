from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
import os

load_dotenv()

api_key_header = APIKeyHeader(name=os.getenv("API_AUTHORIZATION_KEY_NAME"), auto_error=False)

async def api_key_auth(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key is missing"
        )
    
    if api_key != os.getenv("API_AUTHORIZATION"):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return api_key