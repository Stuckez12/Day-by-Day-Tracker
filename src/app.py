import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from src.api import api
from src.core.database.create_db import create_db
from src.core.database.seed_db import seed_db
from src.core.database.upgrade_db import upgrade_db
from src.settings import app_config
from src.tasks import backup_scheduler


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncGenerator[None]:
    # Ensure on fresh start of the application, the
    # future backups have been correctly scheduled
    backup_scheduler.s().apply_async()

    yield


def create_app():
    app = FastAPI(
        title="Day by Day Tracker",
        description="A web application that records user inputs regarding their day rankings, activities and summaries.",
        version=app_config.APP_VERSION,
        root_path="/api",
        lifespan=_lifespan,
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

    add_pagination(app)

    app.include_router(api, prefix="/v1")

    logging.info("DB Creation")
    create_db()

    if app_config.APP_ENV == "prod":
        logging.info("Production Environment Detected.")
        logging.info("Running Setup")

        upgrade_db()
        seed_db()

    @app.exception_handler(TypeError)
    @app.exception_handler(ValueError)
    def controlled_user_errors_exception(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    def catch_all_exception(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error", "exc": str(exc)},
        )

    return app
