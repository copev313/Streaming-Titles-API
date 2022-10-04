"""
    Main module containing the FastAPI app and lambda handler.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from database.session import db, engine, Base
from routes import base, titles


stage = os.getenv("STAGE", "dev")
openapi_prefix = f"/{stage}" if stage else "/"

app = FastAPI(
    title="Streaming Titles API",
    version="0.0.2",
    prefix="/api/v1",
    redoc_url=None,
    description=(
        "A RESTful API for interacting with titles from various "
        "streaming platforms."),
    openapi_prefix=openapi_prefix
)

origins = [
    "http://localhost:8000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await db.connect()
    # Create a session & create all the tables:
    Base.metadata.create_all(engine)


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


@app.get("/")
def root():
    return {
        "status": "Warning",
        "detail": "No such path. Please use '/api/v1' in future requests.",
    }


app.include_router(base.router)
app.include_router(titles.router)

# Handler object for lambda integration:
handler = Mangum(app)
