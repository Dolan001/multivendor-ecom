import os
from .base_settings import env
# -------------------------------------
# REDIS: configurations
# -------------------------------------
# REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env("REDIS_PORT", default="6379")
REDIS_DB = env("REDIS_DB", default="0")
REDIS_PASSWORD = env("REDIS_PASSWORD", default="")

REDIS_URL = f"redis://{REDIS_PASSWORD}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
# -------------------------------------
# CHANNELS CONFIGURATION
# -------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

# -------------------------------------
# CACHE CONFIGURATION
# -------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
