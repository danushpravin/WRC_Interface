from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.modules.slots.schemas import SlotSchema, SlotCreateRequest
from app.modules.slots.service import get_all_slots, get_slot_by_id, create_slot, register_for_slot, cancel_registration
from app.modules.users.models import User

router = APIRouter(prefix="/api/slots", tags=["slots"])


@router.get("", response_model=list[SlotSchema])
def list_slots(db: Session = Depends(get_db)):
    return get_all_slots(db)


@router.get("/{slot_id}", response_model=SlotSchema)
def get_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = get_slot_by_id(slot_id, db)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot


@router.post("", status_code=201, response_model=SlotSchema)
def create_new_slot(
    data: SlotCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return create_slot(data, current_user, db)


@router.post("/{slot_id}/register")
def register(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        registration = register_for_slot(slot_id, current_user, db)
        return {"message": "Registered successfully", "registration_id": registration.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{slot_id}/cancel")
def cancel(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return cancel_registration(slot_id, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))