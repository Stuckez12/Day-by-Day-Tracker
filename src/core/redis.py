import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Generator

from redis import Redis, from_url as from_url_sync
from redis.lock import Lock
from tenacity import retry, stop_after_attempt, wait_exponential

from src.settings import app_config


application_redis = Redis(
    host=app_config.REDIS_HOST,
    port=app_config.REDIS_PORT,
    db=app_config.REDIS_APP_SETTINGS_DB,
)


@contextmanager
def redis_connection_sync() -> Generator[Redis, None, None]:
    redis = from_url_sync(
        app_config.REDIS_APP_SETTINGS_URL, encoding="utf-8", decode_responses=False
    )

    try:
        yield redis

    finally:
        redis.close()


@contextmanager
def redis_lock(
    *,
    lock_name: str,
    check_rate_s: float = 1,
    wait_to_acquire_lock: bool = True,
    timeout: int = 600,
    blocking_timeout: int = 60,
) -> Generator[Lock, None, None]:
    """
    Used in a with statement to enforce that the following actions must be done sequentially.

    with redis_lock(lock_name="example"):
        sequential_required_func()

    lock_name[str] - Name of the lock

    check_rate_s[float: 1] - Should we wait to acquire the lock

    wait_to_acquire_lock[bool: True] - Should we wait to acquire the lock

    timeout[int: 600] - Maximum lifecycle of the lock

    blocking_timeout[int: 60] - Maximum time in seconds to wait for lock acquisition
    """

    with redis_connection_sync() as redis:
        with redis.lock(
            name=lock_name,
            sleep=check_rate_s,
            timeout=timeout,
            blocking=wait_to_acquire_lock,
            blocking_timeout=blocking_timeout,
        ) as lock:
            yield lock


def with_redis_lock(
    *,
    lock_name: str,
    **lock_kwargs: Any,
) -> Any:
    def decorator(func: Any) -> Any:
        func._redis_lock = True
        func._redis_lock_name = lock_name

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.5),
            reraise=True,
        )
        @wraps(func)
        def wrapped(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            logging.info(f"Waiting to acquire redis lock: '{lock_name}'")

            with redis_lock(lock_name=lock_name, **lock_kwargs):
                logging.info(f"Acquired redis lock: '{lock_name}'")
                results = func(*args, **kwargs)

            logging.info(f"Released redis lock: '{lock_name}'")

            return results

        return wrapped

    return decorator
