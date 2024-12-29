# import os
#
# from .base_settings import APP_MEDIA_ROOT, APP_STATIC_DIR, APP_STATIC_ROOT, DEBUG
#
# STATIC_URL = "static/"
# STATIC_ROOT = APP_STATIC_ROOT
# STATICFILES_DIRS = [APP_STATIC_DIR]
#
# # DEFAULT_STORAGE = 'django.core.files.storage.FileSystemStorage'  # Default file storage
#
# DEFAULT_FILE_STORAGE = (
#     "storages.backends.s3.S3Storage"
#     if not DEBUG
#     else "django.core.files.storage.FileSystemStorage"
# )
#
# # STATICFILES_STORAGE = (
# #     "storages.backends.s3.S3Storage"
# #     if not DEBUG
# #     else "django.contrib.staticfiles.storage.StaticFilesStorage"
# # )
# AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
# AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
#
#
# STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# WHITENOISE_AUTOREFRESH = True
#
# MEDIA_URL = "/media/"
# MEDIA_ROOT = APP_MEDIA_ROOT
import os

from decouple import config

USE_S3 = config("USE_S3", default=False, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")  # AWS IAM user access key
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")  # AWS IAM user secret key
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")  # bucket name
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")  # region name
    AWS_S3_CUSTOM_DOMAIN = config(
        "CUSTOM_DOMAIN"
    )  # custom domain name from s3 or cloudfront
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }  # cache control settings
    AWS_QUERYSTRING_EXPIRE = int(
        config("AWS_QUERYSTRING_EXPIRE")
    )  # query string expire time
    AWS_LOCATION = f"{config('AWS_LOCATION')}"  # folder name in the bucket

    CLOUDFRONT_KEY_ID = config("CLOUDFRONT_KEY_ID")  # cloudfront key id
    AWS_CLOUDFRONT_KEY = config("AWS_CLOUDFRONT_KEY").replace(
        "\\n", "\n"
    )  # cloudfront private key

    # static files settings
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"  # static files url
    STORAGES = {
        "default": {
            "BACKEND": "core.storages.s3.PrivateMediaStorage",  # For media files
        },
        "staticfiles": {
            "BACKEND": "core.storages.s3.StaticFilesStorage",  # For static files
        },
    }

else:
    STATIC_URL = "static/"
    STATIC_ROOT = "static/"

    MEDIA_ROOT = "media/"
    MEDIA_URL = "media/"
