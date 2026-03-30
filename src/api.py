from fastapi import APIRouter

from src.routes import personal, ranking


api = APIRouter()
api.include_router(personal.api)
api.include_router(ranking.api)
