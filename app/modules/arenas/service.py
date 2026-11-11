from sqlalchemy.orm import Session, joinedload

from app.modules.arenas.models import Arena, ArenaStatus

def get_all_arenas(db: Session) -> list[Arena]:
    return (
        db.query(Arena)
        .options(joinedload(Arena.capabilities))
        .filter(Arena.status == ArenaStatus.active)
        .all()
    )

def get_arena_by_slug(slug: str, db: Session) -> Arena | None:
    return (
        db.query(Arena)
        .options(joinedload(Arena.capabilities))
        .filter(Arena.slug == slug)
        .first()
    )