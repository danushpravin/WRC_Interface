import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class UserRole(str, enum.Enum):
    guest = "guest"
    player = "player"
    verified_player = "verified_player"
    insider_player = "insider_player"
    arena_operator = "arena_operator"
    admin = "admin"
    super_admin = "super_admin"

class UserStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    banned = "banned"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    gamer_name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.player, nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    is_insider_player: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)