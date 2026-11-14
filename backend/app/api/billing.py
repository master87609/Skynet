"""
Billing API — Plan subscription and upgrade/downgrade.
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.pg_models import User, Subscription
from app.schemas.schemas import SubscribeRequest, SubscriptionOut

router = APIRouter(prefix="/billing", tags=["Billing"])

PLAN_PRICES = {
    "pro": {"monthly": 2399, "yearly": 23988},   # 1999/mo * 12
    "max": {"monthly": 11999, "yearly": 119988},
    "ultra": {"monthly": 11999, "yearly": 119988},
}


@router.post("/subscribe", response_model=SubscriptionOut, summary="Activate or upgrade plan")
async def subscribe(
    payload: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Simulates payment confirmation and upgrades the user's plan.
    In production: integrate Razorpay / Stripe webhook here.
    """
    amount = PLAN_PRICES.get(payload.plan, {}).get(payload.billing_cycle, 0)
    expires_at = datetime.now(timezone.utc) + (
        timedelta(days=365) if payload.billing_cycle == "yearly" else timedelta(days=30)
    )

    # Upsert subscription record
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if sub:
        sub.plan = payload.plan
        sub.billing_cycle = payload.billing_cycle
        sub.payment_method = payload.payment_method
        sub.amount_inr = amount
        sub.is_active = True
        sub.activated_at = datetime.now(timezone.utc)
        sub.expires_at = expires_at
    else:
        sub = Subscription(
            user_id=current_user.id,
            plan=payload.plan,
            billing_cycle=payload.billing_cycle,
            payment_method=payload.payment_method,
            amount_inr=amount,
            expires_at=expires_at,
        )
        db.add(sub)

    # Update user's plan
    current_user.plan = payload.plan
    await db.commit()
    await db.refresh(sub)
    return SubscriptionOut.model_validate(sub)


@router.get("/subscription", response_model=SubscriptionOut | None, summary="Get current subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()
    if not sub:
        return None
    return SubscriptionOut.model_validate(sub)


@router.delete("/cancel", status_code=status.HTTP_204_NO_CONTENT, summary="Cancel subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()
    if sub:
        sub.is_active = False
        current_user.plan = "free"
        await db.commit()
