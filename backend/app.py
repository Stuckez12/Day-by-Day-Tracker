from fastapi import FastAPI
from sqlalchemy_utils import create_database

from backend.api import api


def create_app():
    app = FastAPI(
        title="Day by Day Tracker",
        description="A web application that records user inputs regarding their day rankings, activities and summaries.",
    )

    app.include_router(api, prefix="/api/v1")

    return app
