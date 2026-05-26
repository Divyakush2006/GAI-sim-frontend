"""
GovernAI Studio — Auth Dependencies
=====================================
JWT authentication dependencies for route protection.
Extracts the current officer from the Authorization header.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
import jwt
import structlog

from app.config import get_settings
from app.db.database import get_db
from app.db.models import Officer

logger = structlog.get_logger()
security = HTTPBearer(auto_error=False)


async def get_current_officer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db=Depends(get_db),
) -> Optional[Officer]:
    """
    Extract and validate the current officer from JWT.

    Returns None if no token is provided (allows guest access).
    Raises 401 if token is invalid/expired.
    """
    if not credentials:
        return None

    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "INVALID_TOKEN_TYPE"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "TOKEN_EXPIRED"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN"},
        )

    # Load officer from DB
    user_id = payload["sub"]
    result = await db.execute(select(Officer).where(Officer.id == user_id))
    officer = result.scalar_one_or_none()

    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "USER_NOT_FOUND"},
        )

    return officer


async def require_officer(
    officer: Optional[Officer] = Depends(get_current_officer),
) -> Officer:
    """
    Require authentication — raises 401 if no valid token.
    Use this dependency on routes that MUST have an authenticated officer.
    """
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "AUTHENTICATION_REQUIRED"},
        )
    return officer
