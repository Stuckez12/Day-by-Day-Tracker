from fastapi import APIRouter

from src.routes import auth, personal, ranking, task, task_run

api = APIRouter()
api.include_router(auth.api)
api.include_router(task.api)
api.include_router(personal.api)
api.include_router(ranking.api)
api.include_router(task_run.api)
