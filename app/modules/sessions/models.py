import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SessionStatus(str, enum.Enum):
    scheduled = "scheduled"
    ready_check = "ready_check"
    live = "live"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"
    faulted = "faulted"


class StreamType(str, enum.Enum):
    player_cam = "player_cam"
    opponent_cam = "opponent_cam"
    overhead_cam = "overhead_cam"
    referee_cam = "referee_cam"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("slots.id"))
    arena_id: Mapped[int] = mapped_column(Integer, ForeignKey("arenas.id"), nullable=False)
    game_variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_variants.id"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.scheduled, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    result_code: Mapped[str | None] = mapped_column(String(32))
    winning_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    end_reason: Mapped[str | None] = mapped_column(String(64))
    wagering_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    result_payload_json: Mapped[str | None] = mapped_column(Text)

    players: Mapped[list["SessionPlayer"]] = relationship("SessionPlayer", back_populates="session")
    streams: Mapped[list["SessionStream"]] = relationship("SessionStream", back_populates="session")
    events: Mapped[list["SessionEvent"]] = relationship("SessionEvent", back_populates="session")


class SessionPlayer(Base):
    __tablename__ = "session_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    seat_index: Mapped[int] = mapped_column(Integer, nullable=False)
    team_or_side: Mapped[str | None] = mapped_column(String(32))
    is_insider_fill: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stake_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    joined_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    session: Mapped["GameSession"] = relationship("GameSession", back_populates="players")


class SessionStream(Base):
    __tablename__ = "session_streams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    stream_type: Mapped[StreamType] = mapped_column(Enum(StreamType), nullable=False)
    robot_id: Mapped[str | None] = mapped_column(String(64))
    label: Mapped[str | None] = mapped_column(String(128))
    stream_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="offline", nullable=False)

    session: Mapped["GameSession"] = relationship("GameSession", back_populates="streams")


class SessionEvent(Base):
    __tablename__ = "session_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    payload_json: Mapped[str | None] = mapped_column(Text)

    session: Mapped["GameSession"] = relationship("GameSession", back_populates="events")