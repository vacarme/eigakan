"""JWT codec."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import jwt

from eigakan.env import JWT

from .exc import TokenValidationException

__HEADER = {"alg": "HS256"}


def create_jwt_token(sub: str) -> str:
    """Encode a JWT."""
    now = datetime.now(UTC)
    claims = {
        "sub": sub,
        "iat": now,
        "exp": now + timedelta(hours=JWT.HOURS_TO_EXPIRE),
    }
    jwt_token = jwt.encode(claims, headers=__HEADER, key=str(JWT.SECRET))
    return jwt_token


def decode_jwt_token(token: str) -> dict:
    """Decode a JWT and returns associated claims."""
    try:
        claims = jwt.decode(token, key=str(JWT.SECRET))
    except Exception as e:
        raise TokenValidationException() from e
    return claims
