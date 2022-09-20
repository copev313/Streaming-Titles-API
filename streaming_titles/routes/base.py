"""
    A module for the basic / main routing of the app.
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/api/v1",
    tags=["base"],
)


@router.get("/health")
async def health():
    return {
        "status": "Success",
        "detail": "The API is up and running!"
    }


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")


@router.get("/")
async def home():
    return {
        "status": "Success",
        "detail": "Welcome to the Streaming Titles API!"
    }
