"""
    Main module containing the FastAPI app and lambda handler.
"""
import time
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from database.session import db, engine, Base
from routes import auth, base, titles


app = FastAPI(
    title="Streaming Titles API",
    version="0.1.2",
    prefix="/api/v1",
    # Default docs URL is overriden below to customise the Swagger UI:
    docs_url=None,
    #openapi_url=None,
    redoc_url=None,
    description=(
        "A RESTful API for interacting with titles from various "
        "streaming platforms."
    )
)

# Mount static directory for Swagger UI:
app.mount("/static", StaticFiles(directory="static"), name="static")

# # Configure CORS middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ 
        "http://localhost:3000", # Next.js dev server
        "http://localhost:8081",
        "https://streaming-titles-api.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=[ "*" ],
    allow_headers=[ "*" ],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to add the process time to the response headers. """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 5))
    return response


@app.on_event("startup")
async def startup():
    await db.connect()
    # Create a session & create all the tables:
    Base.metadata.create_all(engine)


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


@app.get("/api/v1/docs", include_in_schema=False)
async def swagger_ui_html(request: Request) -> HTMLResponse:
    """This endpoint serves the Swagger UI generated documentation, with a
    custom favicon.
    
    Ref: https://dev.to/kludex/how-to-change-fastapis-swagger-favicon-4j6
    """
    root_path = request.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url
    response =  get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title,
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_favicon_url="/static/projector.ico",
        swagger_ui_parameters=app.swagger_ui_parameters,
    )
    return response


@app.get("/docs", include_in_schema=False)
async def docs_redirect(request: Request) -> RedirectResponse:
    root_path = request.scope.get("root_path", "").rstrip("/")
    return RedirectResponse(root_path + "/api/v1/docs")


@app.get("/", include_in_schema=False)
async def root_redirect(request: Request) -> RedirectResponse:
    root_path = request.scope.get("root_path", "").rstrip("/")
    return RedirectResponse(root_path + "/api/v1")


app.include_router(base.router)
app.include_router(titles.router)
app.include_router(auth.router)
