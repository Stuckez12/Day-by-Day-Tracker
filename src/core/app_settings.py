from redis.exceptions import ConnectionError as RedisConnectionError

from src.core.redis import application_redis
from src.schemas import ApplicationSettingsSchema


def get_configurable_application_settings() -> ApplicationSettingsSchema:
    try:
        redis_result = application_redis.get("application-settings")

    except RedisConnectionError:
        raise ConnectionError("Unable to connect to Redis")

    return ApplicationSettingsSchema.model_validate(redis_result)


def configure_application_settings(new_settings: ApplicationSettingsSchema) -> None:
    try:
        application_redis.set("application-settings", new_settings.model_dump_json())

    except RedisConnectionError:
        raise ConnectionError("Unable to connect to Redis")
