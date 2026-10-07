from datetime import datetime, timedelta, timezone

import jwt

from packages.config.settings import settings


def create_access_token(data: dict) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes  #type:ignore 
    )

    payload["exp"] = expire

    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm="HS256",
    )

    return token


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.PyJWTError:
        return None