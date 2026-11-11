from sqlalchemy.orm import Session, joinedload

from app.modules.slots.models import Slot, SlotRegistration, SlotStatus, RegistrationStatus
from app.modules.slots.schemas import SlotCreateRequest
from app.modules.users.models import User


def get_all_slots(db: Session) -> list[Slot]:
    return (
        db.query(Slot)
        .options(joinedload(Slot.registrations))
        .filter(Slot.status.in_([SlotStatus.published, SlotStatus.partially_booked, SlotStatus.confirmed]))
        .all()
    )


def get_slot_by_id(slot_id: int, db: Session) -> Slot | None:
    return (
        db.query(Slot)
        .options(joinedload(Slot.registrations))
        .filter(Slot.id == slot_id)
        .first()
    )


def create_slot(data: SlotCreateRequest, user: User, db: Session) -> Slot:
    slot = Slot(
        arena_id=data.arena_id,
        game_variant_id=data.game_variant_id,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        capacity=data.capacity,
        wagering_allowed=data.wagering_allowed,
        price_tokens=data.price_tokens,
        price_gbp=data.price_gbp,
        status=SlotStatus.published,
        created_by_user_id=user.id,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def register_for_slot(slot_id: int, user: User, db: Session) -> SlotRegistration:
    slot = get_slot_by_id(slot_id, db)

    if not slot:
        raise ValueError("Slot not found")

    if slot.status not in [SlotStatus.published, SlotStatus.partially_booked]:
        raise ValueError("Slot is not open for registration")

    if slot.booked_count >= slot.capacity:
        raise ValueError("Slot is full")

    existing = db.query(SlotRegistration).filter(
        SlotRegistration.slot_id == slot_id,
        SlotRegistration.user_id == user.id,
        SlotRegistration.registration_status != RegistrationStatus.cancelled,
    ).first()
    if existing:
        raise ValueError("You are already registered for this slot")

    registration = SlotRegistration(
        slot_id=slot_id,
        user_id=user.id,
        registration_status=RegistrationStatus.confirmed,
        payment_status="unpaid",
    )
    db.add(registration)

    slot.booked_count += 1
    if slot.booked_count >= slot.capacity:
        slot.status = SlotStatus.confirmed
    else:
        slot.status = SlotStatus.partially_booked

    db.commit()
    db.refresh(registration)
    return registration


def cancel_registration(slot_id: int, user: User, db: Session) -> dict:
    registration = db.query(SlotRegistration).filter(
        SlotRegistration.slot_id == slot_id,
        SlotRegistration.user_id == user.id,
        SlotRegistration.registration_status != RegistrationStatus.cancelled,
    ).first()

    if not registration:
        raise ValueError("No active registration found for this slot")

    slot = get_slot_by_id(slot_id, db)
    registration.registration_status = RegistrationStatus.cancelled
    slot.booked_count -= 1

    if slot.status == SlotStatus.confirmed:
        slot.status = SlotStatus.partially_booked

    db.commit()
    return {"message": "Registration cancelled"}

def get_registrations_with_users(slot_id: int, db: Session) -> list[dict]:
    registrations = (
        db.query(SlotRegistration, User)
        .join(User, SlotRegistration.user_id == User.id)
        .filter(SlotRegistration.slot_id == slot_id)
        .all()
    )
    return [
        {
            "id": reg.id,
            "user_id": reg.user_id,
            "gamer_name": user.gamer_name,
            "email": user.email,
            "team_or_side": reg.team_or_side,
            "registration_status": reg.registration_status.value,
            "payment_status": reg.payment_status,
            "joined_at": reg.joined_at,
        }
        for reg, user in registrations
    ]