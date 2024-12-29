import jwt
from cryptography.fernet import Fernet
from django.conf import settings


def encrypt(data: str):
    key = bytes(settings.FERNET_SECRET_KEY, "utf-8")
    return Fernet(key).encrypt(bytes(data, "utf-8"))


def decrypt(token: str):
    key = bytes(settings.FERNET_SECRET_KEY, "utf-8")
    return Fernet(key).decrypt(bytes(token, "utf-8")).decode("utf-8")


def encode_token(payload: dict):
    return jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.SIMPLE_JWT.get("ALGORITHM"),
    )


def decode_token(token: str):
    return jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms="HS256",
    )
