from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy_utils import create_database

from backend.api import api


def create_app():
    app = FastAPI(
        title="Day by Day Tracker",
        description="A web application that records user inputs regarding their day rankings, activities and summaries.",
    )

    app.include_router(api, prefix="/api/v1")

    origins = ["http://localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
