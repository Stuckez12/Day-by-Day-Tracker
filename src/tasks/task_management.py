import logging

from celery import Task
from celery.signals import after_task_publish, task_postrun, task_prerun, task_retry
from datetime import datetime, timezone

from src.common import get_db
from src.services import TaskService


@after_task_publish.connect
def record_task_to_database(sender, headers, body, routing_key, **kwargs):
    logging.info("Recording to db")
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)

        service.register_task(headers["id"], sender)

        logging.info("Recorded")

    finally:
        db_gen.close()

    logging.info("Done recording")


@task_prerun.connect
def before_task_execution(task_id: str, **kwargs):
    logging.info("Before execution")
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        task_record = service.get_by_id(task_id)

        task_record.started_at = datetime.now(timezone.utc)
        db.commit()

    finally:
        db_gen.close()


@task_postrun.connect
def finalise_task(task_id: str, **kwargs):
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        task_record = service.get_by_id(task_id)

        task_record.ended_at = datetime.now(timezone.utc)
        db.commit()

    finally:
        db_gen.close()


@task_retry.connect
def log_retry(task: Task, **kwargs):
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)

    finally:
        db_gen.close()
