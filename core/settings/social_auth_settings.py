import os

GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
GOOGLE_REDIRECT_URL = os.getenv("GOOGLE_REDIRECT_URL")

SOCIAL_AUTH_APPLE_ID_SERVICE = os.getenv("SOCIAL_AUTH_APPLE_ID_SERVICE")
SOCIAL_AUTH_APPLE_ID_CLIENT = os.getenv("SOCIAL_AUTH_APPLE_ID_CLIENT")
SOCIAL_AUTH_APPLE_ID_TEAM = os.getenv("SOCIAL_AUTH_APPLE_ID_TEAM")
SOCIAL_AUTH_APPLE_ID_SECRET = os.getenv("SOCIAL_AUTH_APPLE_ID_SECRET")
SOCIAL_AUTH_APPLE_ID_KEY = os.getenv("SOCIAL_AUTH_APPLE_ID_KEY")
SOCIAL_AUTH_APPLE_ID_SCOPE = ["email", "name"]
APPLE_TOKEN_URL = os.getenv("APPLE_TOKEN_URL")
APPLE_REDIRECT_URL = os.getenv("APPLE_REDIRECT_URL")

KAKAO_TOKEN_URL = os.getenv("KAKAO_TOKEN_URL")
KAKAO_REDIRECT_URL = os.getenv("KAKAO_REDIRECT_URL")
SOCIAL_AUTH_KAKAO_KEY = os.getenv("SOCIAL_AUTH_KAKAO_KEY")
SOCIAL_AUTH_KAKAO_APP_KEY = os.getenv("SOCIAL_AUTH_KAKAO_APP_KEY")


DEEPL_TRANSLATOR_API_KEY = os.getenv("DEEPL_TRANSLATOR_API_KEY")
