import logging

from celery import Task
from celery.signals import (
    before_task_publish,
    task_failure,
    task_prerun,
    task_retry,
    task_success,
)
from datetime import datetime, timezone

from src.common import get_db
from src.enums import TaskStatus
from src.services import TaskService


@before_task_publish.connect
def record_task_to_database(sender: str, headers: dict, **kwargs):
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        service.register_task(headers["id"], sender)

    finally:
        db_gen.close()


@task_prerun.connect
def before_task_execution(task_id: str, **kwargs):
    logging.info("Before execution")
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        task_record = service.get_by_id(task_id)

        task_record.started_at = datetime.now(timezone.utc)
        task_record.status = TaskStatus.RUNNING.value
        db.commit()

    finally:
        db_gen.close()


@task_success.connect
def finalise_task(task_id: str, **kwargs):
    logging.info("After execution")
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        task_record = service.get_by_id(task_id)

        task_record.ended_at = datetime.now(timezone.utc)
        task_record.status = TaskStatus.SUCCESS.value
        db.commit()

    finally:
        db_gen.close()


@task_failure.connect
def finalise_task(task_id: str, **kwargs):
    logging.info("After execution")
    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        task_record = service.get_by_id(task_id)

        task_record.ended_at = datetime.now(timezone.utc)
        task_record.status = TaskStatus.FAILED.value
        db.commit()

    finally:
        db_gen.close()


@task_retry.connect
def log_retry(sender: Task, **kwargs):
    task_id = sender.request.id

    try:
        db_gen = get_db()
        db = next(db_gen)

        service = TaskService(db)
        task_record = service.get_by_id(task_id)

        task_record.retries += 1
        db.commit()

    finally:
        db_gen.close()
