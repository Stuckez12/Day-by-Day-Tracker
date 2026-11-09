import redis

from src.settings import app_config


celery_redis = redis.Redis(
    host=app_config.REDIS_HOST,
    port=app_config.REDIS_PORT,
    db=app_config.REDIS_CELERY_DB,
)


application_redis = redis.Redis(
    host=app_config.REDIS_HOST,
    port=app_config.REDIS_PORT,
    db=app_config.REDIS_APP_SETTINGS_DB,
)
