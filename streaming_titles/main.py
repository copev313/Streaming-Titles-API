"""
    Main module containing the FastAPI app and lambda handler.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database.session import db, engine, Base
from routes import base, titles


app = FastAPI(
    title="Streaming Titles API",
    version="0.0.2",
    prefix="/api/v1",
    docs_url=None,
    redoc_url=None,
    description=(
        "A RESTful API for interacting with titles from various "
        "streaming platforms.")
)

# Mount static directory for Swagger UI:
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost:8000",
        "http://localhost",
    ],
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


@app.get("/docs", include_in_schema=False)
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
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_favicon_url="/static/projector.ico",
        swagger_ui_parameters=app.swagger_ui_parameters,
    )


@app.get("/")
async def root():
    return {
        "status": "Warning",
        "detail": "No such path. Please use '/api/v1' in future requests.",
    }



app.include_router(base.router)
app.include_router(titles.router)
