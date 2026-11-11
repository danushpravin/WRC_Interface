from datetime import datetime
from pydantic import BaseModel


class SlotRegistrationSchema(BaseModel):
    id: int
    user_id: int
    team_or_side: str | None
    registration_status: str
    payment_status: str
    joined_at: datetime

    class Config:
        from_attributes = True


class SlotSchema(BaseModel):
    id: int
    arena_id: int
    game_variant_id: int
    starts_at: datetime
    ends_at: datetime
    capacity: int
    booked_count: int
    status: str
    wagering_allowed: bool
    price_tokens: float
    price_gbp: float
    registrations: list[SlotRegistrationSchema]

    class Config:
        from_attributes = True


class SlotCreateRequest(BaseModel):
    arena_id: int
    game_variant_id: int
    starts_at: datetime
    ends_at: datetime
    capacity: int
    wagering_allowed: bool = False
    price_tokens: float = 0
    price_gbp: float = 0