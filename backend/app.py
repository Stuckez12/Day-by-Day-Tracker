from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import __version__ as APP_VERSION
from backend.api import api
from backend.settings import app_config


def create_app():
    app = FastAPI(
        title="Day by Day Tracker",
        description="A web application that records user inputs regarding their day rankings, activities and summaries.",
        version=APP_VERSION,
        root_path="/api",
    )

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(api, prefix="/v1")

    return app
