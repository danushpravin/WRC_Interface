import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GameStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    coming_soon = "coming_soon"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), default=GameStatus.active, nullable=False)
    team_size_min: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    team_size_max: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    supports_tournaments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_wagering: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_spectators: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_duration_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    rules_json: Mapped[str | None] = mapped_column(Text)
    ui_schema_json: Mapped[str | None] = mapped_column(Text)

    variants: Mapped[list["GameVariant"]] = relationship("GameVariant", back_populates="game")


class GameVariant(Base):
    __tablename__ = "game_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    variant_code: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    rules_override_json: Mapped[str | None] = mapped_column(Text)

    game: Mapped["Game"] = relationship("Game", back_populates="variants")