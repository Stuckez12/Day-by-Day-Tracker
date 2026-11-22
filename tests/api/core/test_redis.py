from uuid import uuid4

import pytest
from pytest_mock import MockerFixture
from redis.exceptions import LockError
from tenacity import RetryCallState, wait_none

from src.core import redis as redis_module
from src.core.redis import redis_connection_sync, redis_lock, with_redis_lock


class TestRedisLock:
    def test_success_with_default_options(self):
        lock_name = f"test-lock:{uuid4()}"

        with redis_lock(lock_name=lock_name) as lock:
            owned = lock.owned()

        assert owned
        assert lock.name == lock_name
        assert lock.sleep == 1
        assert lock.blocking is True
        assert lock.timeout == 600
        assert lock.blocking_timeout == 60

    def test_success_with_custom_options(self):
        lock_name = f"test-lock:{uuid4()}"

        with redis_lock(
            lock_name=lock_name,
            check_rate_s=0.1,
            wait_to_acquire_lock=False,
            timeout=10,
            blocking_timeout=2,
        ) as lock:
            owned = lock.owned()

        assert owned
        assert lock.name == lock_name
        assert lock.sleep == 0.1
        assert lock.blocking is False
        assert lock.timeout == 10
        assert lock.blocking_timeout == 2

    def test_nonblocking_acquisition_failure(self):
        lock_name = f"test-lock:{uuid4()}"

        with redis_lock(lock_name=lock_name):
            with pytest.raises(LockError, match="Unable to acquire lock"):
                with redis_lock(lock_name=lock_name, wait_to_acquire_lock=False):
                    pytest.fail("A second caller acquired the held lock")

    def test_blocking_acquisition_timeout(self):
        lock_name = f"test-lock:{uuid4()}"

        with redis_lock(lock_name=lock_name):
            with pytest.raises(LockError, match="Unable to acquire lock"):
                with redis_lock(
                    lock_name=lock_name, check_rate_s=0.005, blocking_timeout=0.01
                ):
                    pytest.fail("A second caller acquired the held lock")

    def test_releases_lock_when_body_raises(self):
        lock_name = f"test-lock:{uuid4()}"

        with pytest.raises(RuntimeError, match="Body failed"):
            with redis_lock(lock_name=lock_name):
                raise RuntimeError("Body failed")

        with redis_lock(lock_name=lock_name, wait_to_acquire_lock=False) as lock:
            assert lock.owned()


class TestWithRedisLock:
    def test_success_preserves_metadata_and_forwards_arguments(self):
        lock_name = f"test-lock:{uuid4()}"

        @with_redis_lock(lock_name=lock_name)
        def join_words(first: str, *, second: str) -> str:
            return f"{first} {second}"

        result = join_words("hello", second="world")
        assert result == "hello world"
        assert join_words.__name__ == "join_words"

    def test_forwards_custom_lock_options(self, mocker: MockerFixture):
        lock_name = f"test-lock:{uuid4()}"
        lock = mocker.spy(redis_module, "redis_lock")
        options = {
            "check_rate_s": 0.1,
            "wait_to_acquire_lock": False,
            "timeout": 10,
            "blocking_timeout": 2,
        }

        @with_redis_lock(lock_name=lock_name, **options)
        def get_result() -> str:
            return "done"

        result = get_result()
        assert result == "done"

        lock.assert_called_once_with(lock_name=lock_name, **options)

    def test_retries_when_lock_acquisition_fails(self):
        lock_name = f"test-lock:{uuid4()}"

        @with_redis_lock(lock_name=lock_name, wait_to_acquire_lock=False)
        def get_result() -> str:
            return "done"

        with redis_connection_sync() as redis:
            held_lock = redis.lock(lock_name, timeout=10)
            assert held_lock.acquire(blocking=False)

            def release_lock(_: RetryCallState) -> None:
                held_lock.release()

            try:
                result = get_result.retry_with(
                    wait=wait_none(), before_sleep=release_lock
                )()

            finally:
                if held_lock.owned():
                    held_lock.release()

        assert result == "done"

    def test_retries_when_wrapped_function_raises(self):
        lock_name = f"test-lock:{uuid4()}"
        attempts = 0

        @with_redis_lock(lock_name=lock_name, wait_to_acquire_lock=False)
        def get_result() -> str:
            nonlocal attempts
            attempts += 1

            if attempts == 1:
                raise RuntimeError("Try again")

            return "done"

        result = get_result.retry_with(wait=wait_none())()
        assert result == "done"
        assert attempts == 2

    def test_reraises_after_three_failed_attempts(self):
        lock_name = f"test-lock:{uuid4()}"
        attempts = 0

        @with_redis_lock(lock_name=lock_name, wait_to_acquire_lock=False)
        def get_result() -> None:
            nonlocal attempts
            attempts += 1

            raise RuntimeError("Body failed")

        with pytest.raises(RuntimeError, match="Body failed"):
            get_result.retry_with(wait=wait_none())()

        assert attempts == 3
