import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TournamentStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    game_variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_variants.id"), nullable=False)
    arena_id: Mapped[int] = mapped_column(Integer, ForeignKey("arenas.id"), nullable=False)
    status: Mapped[TournamentStatus] = mapped_column(Enum(TournamentStatus), default=TournamentStatus.draft, nullable=False)
    format_type: Mapped[str] = mapped_column(String(32), default="single_elimination", nullable=False)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime)
    max_players: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    prize_pool_type: Mapped[str | None] = mapped_column(String(32))
    prize_pool_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    entries: Mapped[list["TournamentEntry"]] = relationship("TournamentEntry", back_populates="tournament")
    matches: Mapped[list["TournamentMatch"]] = relationship("TournamentMatch", back_populates="tournament")


class TournamentEntry(Base):
    __tablename__ = "tournament_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_id: Mapped[int] = mapped_column(Integer, ForeignKey("tournaments.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    seed: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="registered", nullable=False)

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="entries")


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_id: Mapped[int] = mapped_column(Integer, ForeignKey("tournaments.id"), nullable=False)
    round_name: Mapped[str] = mapped_column(String(64), nullable=False)
    match_order: Mapped[int] = mapped_column(Integer, nullable=False)
    session_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("game_sessions.id"))
    player1_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    player2_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    winner_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    next_match_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tournament_matches.id"))

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="matches")