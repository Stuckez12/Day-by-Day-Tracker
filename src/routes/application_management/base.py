from fastapi import APIRouter

from .backup import api as backup_api


api = APIRouter(prefix="/app-management")
base_api = APIRouter(tags=["Application Management"])

api.include_router(base_api)
api.include_router(backup_api)
