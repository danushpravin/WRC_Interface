from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.games.schemas import GameSchema
from app.modules.games.service import get_all_games, get_game_by_code

router = APIRouter(prefix="/api/games", tags=["games"])


@router.get("", response_model=list[GameSchema])
def list_games(db: Session = Depends(get_db)):
    return get_all_games(db)


@router.get("/{game_code}", response_model=GameSchema)
def get_game(game_code: str, db: Session = Depends(get_db)):
    game = get_game_by_code(game_code, db)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game