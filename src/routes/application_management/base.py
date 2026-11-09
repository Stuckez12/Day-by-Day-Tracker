from fastapi import APIRouter
from slowapi import Limiter

from src.core import client_ipaddress
from src.settings import app_config

from .backup import api as backup_api


limiter = Limiter(key_func=client_ipaddress, enabled=app_config.APP_ENV != "test")
api = APIRouter(prefix="/app-management", tags=["Application Management"])
api.include_router(backup_api)
