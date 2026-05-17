from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import stripe
import logging

from src.config import settings
from src.database import get_db
from src.models.user import User
from src.models.subscription import Subscription
from src.models.project import Project  # optional, for usage limits

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)

# Initialize Stripe API key
stripe.api_key = settings.stripe_secret_key
stripe_webhook_secret = settings.stripe_webhook_secret

# ---------------------------------------------------------------------------
# Helper: get current user (from auth middleware)
# We assume get_current_user dependency is defined in middleware/auth.py
# If not, we import from middleware.auth if exists; otherwise implement inline.
# ---------------------------------------------------------------------------
from src.middleware.auth import get_current_user  # type: ignore

# ---------------------------------------------------------------------------
# Endpoint: Create Stripe Checkout Session
# ---------------------------------------------------------------------------
@router.post("/create-checkout-session")
async def create_checkout_session(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Create a Stripe Checkout Session for subscription purchase.
    Returns the session URL for redirect.
    """
    try:
        # Ensure user does not already have an active subscription
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).first()
        if existing_sub:
            raise HTTPException(status_code=400, detail="User already has an active subscription")

        # Create or retrieve Stripe customer for this user
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)}
            )
            user.stripe_customer_id = customer.id
            db.commit()

        # Create a checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer=user.stripe_customer_id,
            mode="subscription",
            line_items=[{
                "price": settings.stripe_price_id,  # You must define this in settings
                "quantity": 1,
            }],
            success_url=settings.frontend_url + "/subscriptions/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.frontend_url + "/subscriptions/cancel",
            metadata={"user_id": str(user.id)}
        )
        return {"session_url": session.url}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Payment service error")
    except Exception as e:
        logger.error(f"Unexpected error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")