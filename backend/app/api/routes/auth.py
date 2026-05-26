"""
GovernAI Studio — Authentication API Routes (Production)
=========================================================
Magic link authentication with JWT tokens.
Real DB operations for token storage, officer creation, and session management.
"""
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
import jwt
import structlog

from app.config import get_settings, Settings
from app.db.database import get_db
from app.db.models import Officer, MagicLink

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["authentication"])


# === Request/Response Schemas ===

class MagicLinkRequest(BaseModel):
    """Request body for magic link generation."""
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        settings = get_settings()
        domain = v.split("@")[1].lower()
        if domain not in settings.ALLOWED_EMAIL_DOMAINS:
            raise ValueError(
                f"Only government email domains are accepted: "
                f"{', '.join(settings.ALLOWED_EMAIL_DOMAINS)}"
            )
        return v.lower()


class MagicLinkResponse(BaseModel):
    message: str
    expires_in: int


class VerifyTokenRequest(BaseModel):
    token: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


# === Token Utilities ===

class TokenService:
    """Handles JWT creation, validation, and magic link tokens."""

    def __init__(self, settings: Settings):
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_ttl = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        self.refresh_ttl = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.magic_ttl = timedelta(minutes=settings.MAGIC_LINK_EXPIRE_MINUTES)

    def create_magic_token(self) -> str:
        """Generate a cryptographically secure magic link token."""
        return secrets.token_urlsafe(32)

    def hash_magic_token(self, token: str) -> str:
        """Hash the magic token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    def create_access_token(self, user_id: str, email: str) -> str:
        """Create a short-lived JWT access token."""
        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc) + self.access_ttl,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """Create a long-lived JWT refresh token."""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + self.refresh_ttl,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str, expected_type: str = "access") -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            if payload.get("type") != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"error": "INVALID_TOKEN_TYPE"},
                )
            return payload
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


# === Endpoints ===

@router.post("/magic-link", response_model=MagicLinkResponse, status_code=status.HTTP_200_OK)
async def request_magic_link(req: MagicLinkRequest, db=Depends(get_db)):
    """
    Generate and store a magic link token for the officer's email.

    In production, this sends an email via Resend. In dev mode, it returns
    the token directly for testing.
    """
    settings = get_settings()
    token_service = TokenService(settings)

    # Generate and hash token
    raw_token = token_service.create_magic_token()
    token_hash = token_service.hash_magic_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.MAGIC_LINK_EXPIRE_MINUTES
    )

    # Invalidate any existing unused tokens for this email
    existing = await db.execute(
        select(MagicLink).where(
            MagicLink.email == req.email,
            MagicLink.used == False,
        )
    )
    for old_token in existing.scalars().all():
        old_token.used = True

    # Store hashed token in DB
    magic_link = MagicLink(
        email=req.email,
        token_hash=token_hash,
        expires_at=expires_at,
        used=False,
    )
    db.add(magic_link)
    await db.flush()

    logger.info("magic_link_created", email=req.email[:3] + "***")

    # In dev mode, return the token directly for testing
    # In production, send email via Resend
    if settings.DEBUG:
        return MagicLinkResponse(
            message=f"[DEV] Magic link token: {raw_token}",
            expires_in=settings.MAGIC_LINK_EXPIRE_MINUTES * 60,
        )

    # Production: send email via Resend
    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        # Build verification URL (frontend handles this)
        verify_url = f"https://governai.vercel.app/auth/verify?token={raw_token}"

        resend.Emails.send({
            "from": f"GovernAI Studio <{settings.RESEND_FROM_EMAIL}>",
            "to": [req.email],
            "subject": "Your GovernAI Studio Login Link",
            "html": f"""
            <div style="font-family: 'Segoe UI', sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
                <h2 style="color: #1a1a2e; margin-bottom: 8px;">GovernAI Studio</h2>
                <p style="color: #555; font-size: 15px;">
                    Click the button below to sign in. This link expires in {settings.MAGIC_LINK_EXPIRE_MINUTES} minutes.
                </p>
                <a href="{verify_url}"
                   style="display: inline-block; background: #6366f1; color: white;
                          padding: 12px 32px; border-radius: 8px; text-decoration: none;
                          font-weight: 600; margin: 24px 0;">
                    Sign In to GovernAI
                </a>
                <p style="color: #999; font-size: 12px; margin-top: 32px;">
                    If you didn't request this link, you can safely ignore this email.
                    <br>GovernAI Studio — AI Governance Simulation for Indian Civil Servants
                </p>
            </div>
            """,
        })
        logger.info("magic_link_email_sent", email=req.email[:3] + "***")
    except Exception as e:
        logger.error("magic_link_email_failed", error=str(e))
        # Don't fail the request — token is stored in DB, user can retry
        return MagicLinkResponse(
            message="There was an issue sending the email. Please try again.",
            expires_in=settings.MAGIC_LINK_EXPIRE_MINUTES * 60,
        )

    return MagicLinkResponse(
        message="Magic link sent. Check your email.",
        expires_in=settings.MAGIC_LINK_EXPIRE_MINUTES * 60,
    )


@router.post("/verify", response_model=AuthTokenResponse)
async def verify_magic_link(req: VerifyTokenRequest, db=Depends(get_db)):
    """
    Verify a magic link token and issue JWT access + refresh tokens.

    1. Hash the incoming token
    2. Look up the hash in DB
    3. Check expiry and used status
    4. Create or get the officer record
    5. Issue JWTs
    """
    settings = get_settings()
    token_service = TokenService(settings)

    # Hash the incoming token
    token_hash = token_service.hash_magic_token(req.token)

    # Look up in DB
    result = await db.execute(
        select(MagicLink).where(
            MagicLink.token_hash == token_hash,
            MagicLink.used == False,
        )
    )
    magic_link = result.scalar_one_or_none()

    if not magic_link:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_OR_USED_TOKEN"},
        )

    # Check expiry
    if magic_link.expires_at < datetime.now(timezone.utc):
        magic_link.used = True  # Mark as used to prevent replay
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "TOKEN_EXPIRED"},
        )

    # Mark token as used
    magic_link.used = True

    # Get or create officer
    officer_result = await db.execute(
        select(Officer).where(Officer.email == magic_link.email)
    )
    officer = officer_result.scalar_one_or_none()

    if not officer:
        # First-time login — create officer record
        officer = Officer(
            email=magic_link.email,
            onboarding_complete=False,
        )
        db.add(officer)
        await db.flush()
        logger.info("officer_created", email=magic_link.email[:3] + "***")
    else:
        # Update last login
        officer.last_login_at = datetime.now(timezone.utc)

    await db.flush()

    # Issue JWTs
    user_id = str(officer.id)
    access = token_service.create_access_token(user_id, magic_link.email)
    refresh = token_service.create_refresh_token(user_id)

    logger.info("auth_success", user_id=user_id)

    return AuthTokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user={
            "id": user_id,
            "email": magic_link.email,
            "onboarding_complete": officer.onboarding_complete,
            "tier": officer.tier,
        },
    )


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh_token(req: RefreshRequest, db=Depends(get_db)):
    """Refresh an expired access token using a valid refresh token."""
    settings = get_settings()
    token_service = TokenService(settings)

    payload = token_service.verify_token(req.refresh_token, expected_type="refresh")
    user_id = payload["sub"]

    # Load officer from DB
    result = await db.execute(
        select(Officer).where(Officer.id == user_id)
    )
    officer = result.scalar_one_or_none()
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "USER_NOT_FOUND"},
        )

    access = token_service.create_access_token(user_id, officer.email)
    refresh = token_service.create_refresh_token(user_id)

    return AuthTokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user={
            "id": user_id,
            "email": officer.email,
            "onboarding_complete": officer.onboarding_complete,
            "tier": officer.tier,
        },
    )
