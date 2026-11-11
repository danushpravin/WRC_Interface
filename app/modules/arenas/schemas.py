from pydantic import BaseModel

class ArenaCapabilitiesSchema(BaseModel):
    wagering_enabled: bool
    spectator_betting_enabled: bool
    sponsor_prizes_enabled: bool
    token_purchases_enabled: bool
    crypto_enabled: bool
    payouts_enabled: bool
    multi_camera_enabled: bool
    third_person_tracking_enabled: bool
    message_if_disabled: str | None

    class Config:
        from_attributes = True

class ArenaSchema(BaseModel):
    id: int
    name: str
    slug: str
    country_code: str | None
    city: str | None
    timezone: str
    status: str
    description: str | None
    capabilities: ArenaCapabilitiesSchema | None

    class Config:
        from_attributes = True
