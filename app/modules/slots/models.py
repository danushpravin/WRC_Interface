import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SlotStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    partially_booked = "partially_booked"
    confirmed = "confirmed"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class RegistrationStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    no_show = "no_show"


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    arena_id: Mapped[int] = mapped_column(Integer, ForeignKey("arenas.id"), nullable=False)
    game_variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_variants.id"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    booked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[SlotStatus] = mapped_column(Enum(SlotStatus), default=SlotStatus.draft, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    insider_fill_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    wagering_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    price_tokens: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    price_gbp: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    registrations: Mapped[list["SlotRegistration"]] = relationship("SlotRegistration", back_populates="slot")


class SlotRegistration(Base):
    __tablename__ = "slot_registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_id: Mapped[int] = mapped_column(Integer, ForeignKey("slots.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    team_or_side: Mapped[str | None] = mapped_column(String(32))
    registration_status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus), default=RegistrationStatus.pending, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(32), default="unpaid", nullable=False)

    slot: Mapped["Slot"] = relationship("Slot", back_populates="registrations")