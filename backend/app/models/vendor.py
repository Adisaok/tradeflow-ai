import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base, TimestampMixin


class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254))
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    preferred_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(50))
    provider_recipient_id: Mapped[str | None] = mapped_column(String(150))
    notes: Mapped[str | None] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    business: Mapped["Business"] = relationship(
        back_populates="vendors"
    )
