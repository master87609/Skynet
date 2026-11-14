"""
Auth API Router — Google OAuth2 and Email (Host Trial) login endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.schemas import (
    GoogleAuthRequest,
    EmailAuthRequest,
    TokenResponse,
    RefreshRequest,
    UserOut,
)
from app.services.auth_service import (
    verify_google_token,
    get_or_create_user_google,
    get_or_create_user_email,
    get_user_by_id,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=TokenResponse, summary="Login with Google OAuth2")
async def google_login(payload: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Frontend sends the Google ID token (from Google Sign-In button).
    Backend verifies it with Google, then returns SKYNET JWT tokens.
    """
    google_data = await verify_google_token(payload.id_token)
    if not google_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google ID token",
        )

    user = await get_or_create_user_google(db, google_data)
    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post("/email", response_model=TokenResponse, summary="Login with Email (Host Trial)")
async def email_login(payload: EmailAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Email-based login for host/trial users.
    No password required during trial phase — instant access.
    """
    user = await get_or_create_user_email(
        db, str(payload.email), payload.name, payload.is_host
    )
    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_data = decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_id(db, token_data["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token({"sub": user.id, "email": user.email})
    new_refresh = create_refresh_token({"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        user=UserOut.model_validate(user),
    )
