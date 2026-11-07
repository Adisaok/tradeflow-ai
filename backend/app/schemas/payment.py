import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DestinationCurrency = Literal["USD", "GBP", "EUR", "CAD", "GHS"]


class PaymentCreate(BaseModel):
    vendor_id: uuid.UUID
    source_amount: Decimal = Field(
        gt=0, max_digits=18, decimal_places=2
    )
    destination_currency: DestinationCurrency = "USD"
    purpose: str = Field(min_length=3, max_length=250)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    vendor_id: uuid.UUID
    reference: str
    source_currency: str
    destination_currency: str
    source_amount: Decimal
    exchange_rate: Decimal
    destination_amount: Decimal
    fee_amount: Decimal
    total_debit: Decimal
    purpose: str
    status: str
    confirmed_at: datetime | None
    created_at: datetime
