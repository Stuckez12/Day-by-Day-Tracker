from fastapi import APIRouter

from src.routes import auth, personal, ranking

api = APIRouter()
api.include_router(auth.api)
api.include_router(personal.api)
api.include_router(ranking.api)
