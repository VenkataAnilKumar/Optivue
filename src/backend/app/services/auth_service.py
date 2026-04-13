"""Cognito JWT validation and role extraction for FastAPI dependencies."""
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, cast

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from jose import JWTError, jwk, jwt
except ModuleNotFoundError:  # pragma: no cover - local fallback when auth libs are absent
    JWTError = Exception
    jwk = None
    jwt = None

from app.config import settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class UserContext:
    sub: str
    email: str
    role: str
    groups: list[str]


@lru_cache(maxsize=1)
def _fetch_jwks() -> dict[str, Any]:
    """Fetch and cache Cognito JWKS."""
    url = (
        f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
        f"{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )
    with httpx.Client(timeout=5) as client:
        resp = client.get(url)
        resp.raise_for_status()
    return cast(dict[str, Any], resp.json())


def _get_public_key(token: str) -> Any:
    """Retrieve the matching public key for the token's kid."""
    if jwt is None or jwk is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT dependencies are not installed",
        )

    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")
    jwks = _fetch_jwks()
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwk.construct(key)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="public key not found for token kid",
    )


def _decode_token(token: str) -> dict[str, Any]:
    """Verify and decode Cognito JWT."""
    if jwt is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT dependencies are not installed",
        )
    try:
        public_key = _get_public_key(token)
        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.cognito_client_id,
            options={"verify_exp": True},
        )
        return cast(dict[str, Any], claims)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"token validation failed: {exc}",
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserContext:
    """FastAPI dependency: validate JWT and return UserContext."""
    if settings.demo_mode:
        # Demo mode: accept any request as finops-analyst
        return UserContext(
            sub="demo-user",
            email="demo@example.com",
            role="finops-analyst",
            groups=["finops-analyst"],
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing Authorization header",
        )

    claims = _decode_token(credentials.credentials)
    groups = cast(list[str], claims.get("cognito:groups", []))
    role = groups[0] if groups else "unknown"

    return UserContext(
        sub=claims.get("sub", ""),
        email=claims.get("email", ""),
        role=role,
        groups=groups,
    )


def require_role(allowed_roles: list[str]) -> Any:
    """FastAPI dependency factory: restrict endpoint to specific roles."""
    async def _dependency(
        user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"role '{user.role}' is not permitted to access this resource",
            )
        return user
    return _dependency

