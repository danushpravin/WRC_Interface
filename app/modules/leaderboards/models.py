from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    leaderboard_type: Mapped[str] = mapped_column(String(32), nullable=False)
    game_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("games.id"))
    arena_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("arenas.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    losses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    points: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)