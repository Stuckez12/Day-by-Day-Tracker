import logging

from src.app import create_app
from src.celery import create_worker
from src.core.log_format import log_handler


logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler],
)


fastapi_app = create_app()
celery_app = create_worker()
