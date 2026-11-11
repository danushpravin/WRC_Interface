from sqlalchemy.orm import Session

from app.modules.leaderboards.models import LeaderboardEntry
from app.modules.games.models import Game


def get_leaderboard(game_code: str, leaderboard_type: str, db: Session) -> dict | None:
    game = db.query(Game).filter(Game.game_code == game_code).first()
    if not game:
        return None

    entries = (
        db.query(LeaderboardEntry)
        .filter(
            LeaderboardEntry.game_id == game.id,
            LeaderboardEntry.leaderboard_type == leaderboard_type,
        )
        .order_by(LeaderboardEntry.points.desc())
        .all()
    )

    return {
        "game_code": game_code,
        "leaderboard_type": leaderboard_type,
        "entries": entries,
    }