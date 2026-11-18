class TestRedisLock:
    def test_success_with_default_options(self):
        pass

    def test_success_with_custom_options(self):
        pass

    def test_nonblocking_acquisition_failure(self):
        pass

    def test_blocking_acquisition_timeout(self):
        pass

    def test_releases_lock_when_body_raises(self):
        pass


class TestWithRedisLock:
    def test_success_preserves_metadata_and_forwards_arguments(self):
        pass

    def test_forwards_custom_lock_options(self):
        pass

    def test_retries_when_lock_acquisition_fails(self):
        pass

    def test_retries_when_wrapped_function_raises(self):
        pass

    def test_reraises_after_three_failed_attempts(self):
        pass
