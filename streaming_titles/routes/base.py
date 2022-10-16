"""
    A module for the basic / main routing of the app.
"""
from fastapi import APIRouter


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


@router.get("/")
async def home():
    return {
        "status": "Success",
        "detail": "Welcome to the Streaming Titles API!"
    }
