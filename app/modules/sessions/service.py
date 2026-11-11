from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.modules.sessions.models import GameSession, SessionStatus, SessionEvent
from app.modules.sessions.schemas import SessionCreateRequest, SessionResultRequest, SessionEventRequest
from app.modules.users.models import User


def get_session_by_id(session_id: int, db: Session) -> GameSession | None:
    return (
        db.query(GameSession)
        .options(
            joinedload(GameSession.players),
            joinedload(GameSession.streams),
            joinedload(GameSession.events),
        )
        .filter(GameSession.id == session_id)
        .first()
    )


def create_session(data: SessionCreateRequest, user: User, db: Session) -> GameSession:
    session = GameSession(
        slot_id=data.slot_id,
        arena_id=data.arena_id,
        game_variant_id=data.game_variant_id,
        wagering_enabled=data.wagering_enabled,
        status=SessionStatus.scheduled,
    )
    db.add(session)
    db.flush()

    event = SessionEvent(
        session_id=session.id,
        event_type="session_created",
        actor_user_id=user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(session)
    return session


def start_session(session_id: int, user: User, db: Session) -> GameSession:
    session = get_session_by_id(session_id, db)
    if not session:
        raise ValueError("Session not found")
    if session.status != SessionStatus.scheduled:
        raise ValueError(f"Cannot start a session with status: {session.status.value}")

    session.status = SessionStatus.live
    session.started_at = datetime.utcnow()

    db.add(SessionEvent(
        session_id=session.id,
        event_type="session_started",
        actor_user_id=user.id,
    ))
    db.commit()
    db.refresh(session)
    return session


def pause_session(session_id: int, user: User, db: Session) -> GameSession:
    session = get_session_by_id(session_id, db)
    if not session:
        raise ValueError("Session not found")
    if session.status != SessionStatus.live:
        raise ValueError("Can only pause a live session")

    session.status = SessionStatus.paused

    db.add(SessionEvent(
        session_id=session.id,
        event_type="session_paused",
        actor_user_id=user.id,
    ))
    db.commit()
    db.refresh(session)
    return session


def resume_session(session_id: int, user: User, db: Session) -> GameSession:
    session = get_session_by_id(session_id, db)
    if not session:
        raise ValueError("Session not found")
    if session.status != SessionStatus.paused:
        raise ValueError("Can only resume a paused session")

    session.status = SessionStatus.live

    db.add(SessionEvent(
        session_id=session.id,
        event_type="session_resumed",
        actor_user_id=user.id,
    ))
    db.commit()
    db.refresh(session)
    return session


def complete_session(session_id: int, data: SessionResultRequest, user: User, db: Session) -> GameSession:
    session = get_session_by_id(session_id, db)
    if not session:
        raise ValueError("Session not found")
    if session.status not in [SessionStatus.live, SessionStatus.paused]:
        raise ValueError("Can only complete a live or paused session")

    session.status = SessionStatus.completed
    session.ended_at = datetime.utcnow()
    session.result_code = data.result_code
    session.winning_user_id = data.winning_user_id
    session.end_reason = data.end_reason
    session.result_payload_json = data.result_payload_json

    if session.started_at:
        delta = session.ended_at - session.started_at
        session.duration_seconds = int(delta.total_seconds())

    db.add(SessionEvent(
        session_id=session.id,
        event_type="session_completed",
        actor_user_id=user.id,
        payload_json=data.result_payload_json,
    ))
    db.commit()
    db.refresh(session)
    return session


def fault_session(session_id: int, reason: str, user: User, db: Session) -> GameSession:
    session = get_session_by_id(session_id, db)
    if not session:
        raise ValueError("Session not found")
    if session.status == SessionStatus.completed:
        raise ValueError("Cannot fault a completed session")

    session.status = SessionStatus.faulted
    session.ended_at = datetime.utcnow()
    session.end_reason = reason

    db.add(SessionEvent(
        session_id=session.id,
        event_type="session_faulted",
        actor_user_id=user.id,
        payload_json=f'{{"reason": "{reason}"}}',
    ))
    db.commit()
    db.refresh(session)
    return session


def log_event(session_id: int, data: SessionEventRequest, user: User, db: Session) -> SessionEvent:
    session = get_session_by_id(session_id, db)
    if not session:
        raise ValueError("Session not found")

    event = SessionEvent(
        session_id=session_id,
        event_type=data.event_type,
        actor_user_id=user.id,
        payload_json=data.payload_json,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event