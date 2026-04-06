from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import __version__ as APP_VERSION
from src.api import api
from src.common.upgrade_db import upgrade_db
from src.settings import is_prod_env


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

    if is_prod_env:
        upgrade_db()

    return app
