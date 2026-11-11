from sqlalchemy.orm import Session, joinedload

from app.modules.games.models import Game, GameStatus


def get_all_games(db: Session) -> list[Game]:
    return (
        db.query(Game)
        .options(joinedload(Game.variants))
        .filter(Game.status == GameStatus.active)
        .all()
    )


def get_game_by_code(game_code: str, db: Session) -> Game | None:
    return (
        db.query(Game)
        .options(joinedload(Game.variants))
        .filter(Game.game_code == game_code)
        .first()
    )