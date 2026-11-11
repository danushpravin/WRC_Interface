import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ArenaStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"


class Arena(Base):
    __tablename__ = "arenas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    country_code: Mapped[str | None] = mapped_column(String(3))
    city: Mapped[str | None] = mapped_column(String(128))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    status: Mapped[ArenaStatus] = mapped_column(Enum(ArenaStatus), default=ArenaStatus.active, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    stream_base_url: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    capabilities: Mapped["ArenaCapabilities"] = relationship("ArenaCapabilities", back_populates="arena", uselist=False)


class ArenaCapabilities(Base):
    __tablename__ = "arena_capabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    arena_id: Mapped[int] = mapped_column(Integer, ForeignKey("arenas.id"), unique=True, nullable=False)
    wagering_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    spectator_betting_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sponsor_prizes_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_purchases_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    crypto_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payouts_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    multi_camera_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    third_person_tracking_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    message_if_disabled: Mapped[str | None] = mapped_column(Text)

    arena: Mapped["Arena"] = relationship("Arena", back_populates="capabilities")