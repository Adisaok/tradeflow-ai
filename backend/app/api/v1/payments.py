import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.business import Business
from app.models.vendor import Vendor
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter(
    prefix="/businesses/{business_id}/payments",
    tags=["payments"],
)

# DEMONSTRATION ASSUMPTIONS ONLY.
# Values represent NGN per one unit of destination currency.
# They are NOT live market rates or Blaaiz quotations.
DEMO_EXCHANGE_RATES = {
    "USD": Decimal("1500.00"),
    "GBP": Decimal("1900.00"),
    "EUR": Decimal("1650.00"),
    "CAD": Decimal("1100.00"),
    "GHS": Decimal("100.00"),
}

DEMO_FEE_RATE = Decimal("0.015")
DEMO_MINIMUM_FEE = Decimal("500.00")


def money(value: Decimal) -> Decimal:
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


async def check_business(
    business_id: uuid.UUID,
    db: AsyncSession,
) -> Business:
    business = await db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    return business


@router.get("/supported-currencies")
async def supported_currencies():
    return {
        "funding_currency": "NGN",
        "rate_type": "illustrative_demo_rate",
        "rates": [
            {
                "currency": currency,
                "ngn_per_unit": str(rate),
            }
            for currency, rate in DEMO_EXCHANGE_RATES.items()
        ],
        "fee_rate_percent": "1.5",
        "minimum_fee_ngn": "500.00",
        "notice": (
            "Illustrative demonstration rates only. "
            "Not live FX quotations or confirmed provider rates."
        ),
    }


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    business_id: uuid.UUID,
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
):
    await check_business(business_id, db)

    vendor = await db.scalar(
        select(Vendor).where(
            Vendor.id == payload.vendor_id,
            Vendor.business_id == business_id,
            Vendor.is_active.is_(True),
        )
    )

    if vendor is None:
        raise HTTPException(
            status_code=404,
            detail="Active vendor not found in this business",
        )

    rate = DEMO_EXCHANGE_RATES[payload.destination_currency]
    amount = money(payload.source_amount)
    fee = max(
        money(amount * DEMO_FEE_RATE),
        DEMO_MINIMUM_FEE,
    )
    destination_amount = money(amount / rate)

    payment = Payment(
        business_id=business_id,
        vendor_id=vendor.id,
        reference=f"TF-{uuid.uuid4().hex[:12].upper()}",
        source_currency="NGN",
        destination_currency=payload.destination_currency,
        source_amount=amount,
        exchange_rate=rate,
        destination_amount=destination_amount,
        fee_amount=fee,
        total_debit=money(amount + fee),
        purpose=payload.purpose,
        status="pending_confirmation",
    )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return payment


@router.get("", response_model=list[PaymentResponse])
async def list_payments(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await check_business(business_id, db)

    result = await db.execute(
        select(Payment)
        .where(Payment.business_id == business_id)
        .order_by(Payment.created_at.desc())
    )

    return result.scalars().all()


@router.post(
    "/{payment_id}/confirm",
    response_model=PaymentResponse,
)
async def confirm_simulated_payment(
    business_id: uuid.UUID,
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await check_business(business_id, db)

    payment = await db.scalar(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.business_id == business_id,
        )
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    if payment.status != "pending_confirmation":
        raise HTTPException(
            status_code=409,
            detail=(
                "Payment cannot be confirmed from status: "
                f"{payment.status}"
            ),
        )

    payment.status = "simulated_success"
    payment.confirmed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(payment)

    return payment
