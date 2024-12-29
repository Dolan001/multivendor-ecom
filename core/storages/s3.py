from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticFilesStorage(S3Boto3Storage):
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    location = f"{settings.AWS_LOCATION}/static" if settings.AWS_LOCATION else "static"
    default_acl = "private"
    cloudfront_key_id = None
    cloudfront_key = None


class PublicMediaStorage(S3Boto3Storage):
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    location = f"{settings.AWS_LOCATION}/media" if settings.AWS_LOCATION else "media"
    file_overwrite = False
    default_acl = "public-read"
    querystring_expire = settings.AWS_QUERYSTRING_EXPIRE


class PrivateMediaStorage(S3Boto3Storage):
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    cloudfront_key_id = settings.CLOUDFRONT_KEY_ID
    cloudfront_key = settings.AWS_CLOUDFRONT_KEY
    querystring_expire = settings.AWS_QUERYSTRING_EXPIRE
    location = f"{settings.AWS_LOCATION}/" if settings.AWS_LOCATION else ""
    default_acl = "private"
    file_overwrite = False
    # custom_domain = False
    signature_version = "s3v4"
    addressing_style = "virtual"
