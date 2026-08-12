import logging
import uuid
from datetime import datetime, timezone

from celery.signals import (
    before_task_publish,
    task_failure,
    task_prerun,
    task_retry,
    task_success,
)
from sqlalchemy.exc import NoResultFound

from celery import Task
from src.common import get_db
from src.enums import TaskStatus
from src.services import TaskService


@before_task_publish.connect
def record_task_to_database(sender: str, headers: dict, **kwargs):
    db_gen = get_db()
    db = next(db_gen)

    try:
        name = sender.split(".")[-1]

        service = TaskService(db)
        service.register_task(headers["id"], name)

        logging.info("Recorded Task")

    finally:
        db_gen.close()

        logging.info("Task Published")


@task_prerun.connect
def before_task_execution(task_id: str, **kwargs):
    logging.info(f"Before task execution. Task ID: {task_id}")
    db_gen = get_db()
    db = next(db_gen)

    try:
        service = TaskService(db)
        task_record = service.get_by_task_id(uuid.UUID(task_id))

        task_record.started_at = datetime.now(timezone.utc)
        task_record.status = TaskStatus.RUNNING.value
        db.commit()

    except NoResultFound:
        logging.info("DB task record not found. Continuing")
        return

    finally:
        db_gen.close()

        logging.info("Execute task")


@task_success.connect
def finalise_success_task(sender: Task, **kwargs):
    task_id = uuid.UUID(sender.request.id)

    logging.info(f"After successful task execution. Task ID: {task_id}")

    db_gen = get_db()
    db = next(db_gen)

    try:
        service = TaskService(db)
        task_record = service.get_by_task_id(task_id)

        task_record.ended_at = datetime.now(timezone.utc)
        task_record.status = TaskStatus.SUCCESS.value
        db.commit()

    except NoResultFound:
        logging.info("DB task record not found. Continuing")
        return

    finally:
        db_gen.close()


@task_failure.connect
def finalise_failure_task(sender: Task, exception: Exception | None = None, **kwargs):
    task_id = uuid.UUID(sender.request.id)

    logging.info("After failed task execution")

    db_gen = get_db()
    db = next(db_gen)

    try:
        service = TaskService(db)
        task_record = service.get_by_task_id(task_id)

        task_record.ended_at = datetime.now(timezone.utc)
        task_record.status = TaskStatus.FAILED.value
        task_record.error = str(exception)
        db.commit()

    except NoResultFound:
        logging.info("DB task record not found. Continuing")
        return

    finally:
        db_gen.close()


@task_retry.connect
def log_retry(sender: Task, **kwargs):
    task_id = uuid.UUID(sender.request.id)

    logging.info("Recording retry attempt")

    db_gen = get_db()
    db = next(db_gen)

    try:
        service = TaskService(db)
        task_record = service.get_by_task_id(task_id)

        task_record.retries += 1
        db.commit()

    except NoResultFound:
        logging.info("DB task record not found. Continuing")
        return

    finally:
        logging.info(f"Task ({task_id}) retrying")

        db_gen.close()
