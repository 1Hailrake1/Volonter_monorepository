import os
import time
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from functools import lru_cache
from app.core.exceptions import InternalServerError
from settings import settings

def generate_jwt_keys():
    os.makedirs(settings.DEFAULT_DIR, exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=settings.KEY_SIZE,
    )

    encryption_algo = serialization.NoEncryption()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algo,
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(settings.JWT_PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_pem)

    with open(settings.JWT_PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_pem)

@lru_cache(maxsize=1)
def get_public_jwt_key() -> bytes:
    with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as f:
        return f.read()

@lru_cache(maxsize=1)
def get_private_jwt_key() -> bytes:
    with open(settings.JWT_PRIVATE_KEY_PATH, "rb") as f:
        return f.read()

def reset_cached_keys():
    get_private_jwt_key.cache_clear()
    get_public_jwt_key.cache_clear()

def create_jwt_token(
        claims:dict,
        type:str = 'access_token',
) -> str:
    try:
        now = int(time.time())
        if type == 'access_token':
            exp = now + settings.ACCESS_TOKEN_EXPIRE
        else:
            exp = now + settings.VERIFY_TOKEN_EXPIRE

        payload = {
            **claims,
            "iat": now,
            "exp": exp,
            "type": type,
        }

        headers = {}
        if settings.JWT_KEY_ID:
            headers["kid"] = settings.JWT_KEY_ID

        private_key = get_private_jwt_key()

        return jwt.encode(
            payload,
            private_key,
            algorithm=settings.JWT_ALGORITHM,
            headers=headers
        )
    except Exception as e:
        raise InternalServerError(f"Ошибка создания токена доступа {e}")


def decode_jwt_token(
        token:str
) -> dict:
    public_key = get_public_jwt_key()

    try:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded
    except Exception as e:
        raise InternalServerError(f"Ошибка декодирования jwt токена {e}")

#generate_jwt_keys()