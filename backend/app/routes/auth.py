"""
Authentication routes — Supabase JWT verification.

Provides a ``get_current_user`` dependency that extracts and verifies the
Supabase JWT from the ``Authorization: Bearer <token>`` header, plus
standalone endpoints for token verification and user profile retrieval.
"""

from __future__ import annotations

import jwt  # PyJWT
import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class UserInfo(BaseModel):
    """Minimal user profile returned after successful auth."""

    id: str
    email: str | None = None
    user_metadata: dict[str, Any] = {}


class VerifyResponse(BaseModel):
    """Response for the ``/verify`` endpoint."""

    valid: bool
    user: UserInfo | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Supabase client helper (lazy singleton)
# ---------------------------------------------------------------------------

_supabase_client = None


def _get_supabase():
    """Return a cached Supabase client, creating it on first call."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if not url or not key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase credentials not configured (SUPABASE_URL / SUPABASE_ANON_KEY)",
            )
        _supabase_client = create_client(url, key)
    return _supabase_client


# ---------------------------------------------------------------------------
# Dependency: get_current_user
# ---------------------------------------------------------------------------

async def get_current_user(
    authorization: str | None = Header(None, description="Bearer <supabase_jwt>"),
) -> UserInfo:
    """FastAPI dependency that extracts & verifies the Supabase JWT.

    Accepts a Supabase access token from the Authorization header.

    Note: In some environments the supabase-py auth call may fail with
    "Invalid path specified in request URL" (usually due to an invalid
    SUPABASE_URL or blocked/rewritten network path). When that happens,
    we fall back to local JWT verification if SUPABASE_JWT_SECRET is set.
    """

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must start with 'Bearer '",
        )

    token = authorization.removeprefix("Bearer ").strip()
    # Guard against common formatting issues (quotes, accidental commas, etc.)
    token = token.strip().strip('"').strip("'").strip()

    # 1) Prefer Supabase API verification (keeps parity with Supabase/GoTrue)
    try:
        sb = _get_supabase()
        user_response = sb.auth.get_user(token)

        if user_response is None or user_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user = user_response.user
        return UserInfo(
            id=user.id,
            email=user.email,
            user_metadata=user.user_metadata or {},
        )

    except HTTPException:
        raise
    except Exception as exc:
        # 2) Fallback: local verification (no network). Requires JWT secret.
        secret = os.getenv("SUPABASE_JWT_SECRET", "").strip()
        if not secret:
            logger.error("JWT verification failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {exc}",
            ) from exc

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )

            sub = payload.get("sub")
            if not sub:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing 'sub' claim",
                )

            return UserInfo(
                id=sub,
                email=payload.get("email"),
                user_metadata=payload.get("user_metadata") or {},
            )

        except HTTPException:
            raise
        except Exception as jwt_exc:
            logger.error("JWT verification failed (supabase=%s, local=%s)", exc, jwt_exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {jwt_exc}",
            ) from jwt_exc


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/verify", response_model=VerifyResponse)
async def verify_token(
    authorization: str = Header(..., description="Bearer <supabase_jwt>"),
) -> VerifyResponse:
    """Verify a Supabase JWT and return the associated user info."""

    try:
        user = await get_current_user(authorization)
        return VerifyResponse(valid=True, user=user)
    except HTTPException as exc:
        return VerifyResponse(valid=False, error=exc.detail)


@router.get("/user", response_model=UserInfo)
async def get_user_profile(
    user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    """Return the profile for the currently authenticated user."""
    return user
