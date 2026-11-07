import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base, TimestampMixin


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("vendors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reference: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False, index=True
    )
    source_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="NGN"
    )
    destination_currency: Mapped[str] = mapped_column(
        String(3), nullable=False
    )
    source_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), nullable=False
    )
    destination_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    total_debit: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending_confirmation"
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
