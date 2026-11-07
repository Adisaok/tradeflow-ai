import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base, TimestampMixin


class Business(Base, TimestampMixin):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    legal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    registration_number: Mapped[str | None] = mapped_column(String(100))
    country_code: Mapped[str] = mapped_column(
        String(2), nullable=False, default="NG"
    )
    base_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="NGN"
    )
    email: Mapped[str | None] = mapped_column(String(254))
    phone: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )

    vendors: Mapped[list["Vendor"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
    )
