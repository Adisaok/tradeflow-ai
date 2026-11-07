import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import (
    normalize_country_code,
    normalize_currency_code,
)


class BusinessCreate(BaseModel):
    legal_name: str = Field(min_length=2, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    registration_number: str | None = Field(default=None, max_length=100)
    country_code: str = Field(default="NG", min_length=2, max_length=2)
    base_currency: str = Field(default="NGN", min_length=3, max_length=3)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, value: str) -> str:
        return normalize_country_code(value)

    @field_validator("base_currency")
    @classmethod
    def validate_base_currency(cls, value: str) -> str:
        return normalize_currency_code(value)


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    legal_name: str
    display_name: str | None
    registration_number: str | None
    country_code: str
    base_currency: str
    email: str | None
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
