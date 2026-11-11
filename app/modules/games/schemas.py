from pydantic import BaseModel


class GameVariantSchema(BaseModel):
    id: int
    variant_code: str
    title: str
    capacity: int
    rules_override_json: str | None

    class Config:
        from_attributes = True


class GameSchema(BaseModel):
    id: int
    game_code: str
    title: str
    description: str | None
    status: str
    team_size_min: int
    team_size_max: int
    supports_tournaments: bool
    supports_wagering: bool
    supports_spectators: bool
    default_duration_seconds: int
    rules_json: str | None
    ui_schema_json: str | None
    variants: list[GameVariantSchema]

    class Config:
        from_attributes = True