"""
Auth Service — Google OAuth2 token verification + user upsert.
"""
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pg_models import User
from app.core.config import settings


GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"


async def verify_google_token(id_token: str) -> dict | None:
    """Verifies a Google ID token against Google's public endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(GOOGLE_TOKEN_INFO_URL, params={"id_token": id_token})
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Verify audience matches our client ID
        if data.get("aud") != settings.GOOGLE_CLIENT_ID:
            return None
        return data


async def get_or_create_user_google(db: AsyncSession, google_data: dict) -> User:
    """Fetch existing user by google_id or email, or create a new one."""
    google_id = google_data.get("sub")
    email = google_data.get("email")

    # Try find by google_id
    stmt = select(User).where(User.google_id == google_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user

    # Try find by email
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.google_id = google_id
        user.avatar_url = google_data.get("picture")
        await db.commit()
        await db.refresh(user)
        return user

    # Create new user
    user = User(
        email=email,
        name=google_data.get("name"),
        avatar_url=google_data.get("picture"),
        google_id=google_id,
        plan="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user_email(
    db: AsyncSession, email: str, name: str | None, is_host: bool
) -> User:
    """Get or create a user by email (host trial / email login)."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(
        email=email,
        name=name or email.split("@")[0].title(),
        plan="free",
        is_host=is_host,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
