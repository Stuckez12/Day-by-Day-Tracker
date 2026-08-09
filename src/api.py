from fastapi import APIRouter

from src.routes import auth, personnel, ranking, task, task_run


api = APIRouter()
api.include_router(auth.api)
api.include_router(task.api)
api.include_router(personnel.api)
api.include_router(ranking.api)
api.include_router(task_run.api)
