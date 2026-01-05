from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy_utils import create_database

from backend.api import api


def create_app():
    app = FastAPI(
        title="Day by Day Tracker",
        description="A web application that records user inputs regarding their day rankings, activities and summaries.",
    )

    origins = [
        "http://localhost:3000",
        "http://localhost:3000/",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ],  # Explicitly include OPTIONS
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(api, prefix="/api/v1")

    return app
