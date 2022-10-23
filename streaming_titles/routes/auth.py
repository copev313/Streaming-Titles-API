"""
    A module for handling authentication middleware.
"""
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.security.api_key import APIKey


router = APIRouter(
    prefix="/api/v1",
    tags=["auth"],
)

APIKeyHeader = APIKeyHeader(name="access_token", auto_error=False)

async def get_api_key(
    api_key_header: str = Depends(APIKeyHeader)
):
    """A function to check the API key header against valid API keys."""
    api_keys = os.getenv("API_KEYS").split("||")
    if api_key_header in api_keys:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key.",
        )


@router.get("/secure")
async def secure_route(api_key: APIKey = Depends(get_api_key)):
    """An example of a secure endpoint."""
    return {
        "status": "Success",
        "detail": "You have successfully accessed a secure route!"
    }
