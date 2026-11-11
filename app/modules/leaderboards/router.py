from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.leaderboards.schemas import LeaderboardSchema
from app.modules.leaderboards.service import get_leaderboard

router = APIRouter(prefix="/api/leaderboards", tags=["leaderboards"])


@router.get("/{game_code}", response_model=LeaderboardSchema)
def get_game_leaderboard(
    game_code: str,
    leaderboard_type: str = "global",
    db: Session = Depends(get_db)
):
    result = get_leaderboard(game_code, leaderboard_type, db)
    if not result:
        raise HTTPException(status_code=404, detail="Game not found")
    return result