from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from packages.security.jwt import verify_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> dict:
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"id": user_id}