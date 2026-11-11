from pydantic import BaseModel


class LeaderboardEntrySchema(BaseModel):
    rank: int | None
    user_id: int
    wins: int
    losses: int
    points: float

    class Config:
        from_attributes = True


class LeaderboardSchema(BaseModel):
    game_code: str
    leaderboard_type: str
    entries: list[LeaderboardEntrySchema]