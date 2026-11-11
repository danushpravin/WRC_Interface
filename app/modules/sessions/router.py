from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.modules.sessions.schemas import (
    SessionSchema,
    SessionCreateRequest,
    SessionResultRequest,
    SessionEventRequest,
    SessionEventSchema,
)
from app.modules.sessions.service import (
    get_session_by_id,
    create_session,
    start_session,
    pause_session,
    resume_session,
    complete_session,
    fault_session,
    log_event,
)
from app.modules.users.models import User

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=SessionSchema)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = get_session_by_id(session_id, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("", status_code=201, response_model=SessionSchema)
def create_new_session(
    data: SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return create_session(data, current_user, db)


@router.post("/{session_id}/start", response_model=SessionSchema)
def start(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return start_session(session_id, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/pause", response_model=SessionSchema)
def pause(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return pause_session(session_id, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/resume", response_model=SessionSchema)
def resume(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return resume_session(session_id, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/complete", response_model=SessionSchema)
def complete(
    session_id: int,
    data: SessionResultRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return complete_session(session_id, data, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/fault", response_model=SessionSchema)
def fault(
    session_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return fault_session(session_id, reason, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/event", response_model=SessionEventSchema)
def add_event(
    session_id: int,
    data: SessionEventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return log_event(session_id, data, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))