from src.app import create_app
from src.celery import create_worker

fastapi_app = create_app()
celery_app = create_worker()
