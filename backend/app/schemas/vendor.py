import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import (
    normalize_country_code,
    normalize_currency_code,
)


class VendorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: str | None = Field(default=None, max_length=254)
    country_code: str = Field(min_length=2, max_length=2)
    preferred_currency: str = Field(min_length=3, max_length=3)
    payment_method: str | None = Field(default=None, max_length=50)
    provider_recipient_id: str | None = Field(default=None, max_length=150)
    notes: str | None = None
    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str) -> str:
        return normalize_country_code(value)

    @field_validator("preferred_currency")
    @classmethod
    def validate_preferred_currency(cls, value: str) -> str:
        return normalize_currency_code(value)


class VendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    email: str | None = Field(default=None, max_length=254)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    preferred_currency: str | None = Field(default=None, min_length=3, max_length=3)
    payment_method: str | None = Field(default=None, max_length=50)
    provider_recipient_id: str | None = Field(default=None, max_length=150)
    notes: str | None = None
    is_active: bool | None = None

    @field_validator(
        "name",
        "country_code",
        "preferred_currency",
        mode="before",
    )
    @classmethod
    def reject_null_required_fields(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_country_code(value)

    @field_validator("preferred_currency")
    @classmethod
    def validate_preferred_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_currency_code(value)


class VendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    email: str | None
    country_code: str
    preferred_currency: str
    payment_method: str | None
    provider_recipient_id: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
