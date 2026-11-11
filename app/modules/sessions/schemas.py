from datetime import datetime
from pydantic import BaseModel


class SessionPlayerSchema(BaseModel):
    id: int
    user_id: int
    seat_index: int
    team_or_side: str | None
    is_insider_fill: bool
    stake_amount: float
    joined_confirmed: bool

    class Config:
        from_attributes = True


class SessionStreamSchema(BaseModel):
    id: int
    stream_type: str
    robot_id: str | None
    label: str | None
    stream_url: str | None
    status: str

    class Config:
        from_attributes = True


class SessionEventSchema(BaseModel):
    id: int
    event_type: str
    event_time: datetime
    actor_user_id: int | None
    payload_json: str | None

    class Config:
        from_attributes = True


class SessionSchema(BaseModel):
    id: int
    slot_id: int | None
    arena_id: int
    game_variant_id: int
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int | None
    result_code: str | None
    winning_user_id: int | None
    end_reason: str | None
    wagering_enabled: bool
    result_payload_json: str | None
    players: list[SessionPlayerSchema]
    streams: list[SessionStreamSchema]
    events: list[SessionEventSchema]

    class Config:
        from_attributes = True


class SessionCreateRequest(BaseModel):
    slot_id: int | None = None
    arena_id: int
    game_variant_id: int
    wagering_enabled: bool = False


class SessionResultRequest(BaseModel):
    result_code: str
    winning_user_id: int | None = None
    end_reason: str
    result_payload_json: str | None = None


class SessionEventRequest(BaseModel):
    event_type: str
    payload_json: str | None = None