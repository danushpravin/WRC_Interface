from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.arenas.schemas import ArenaSchema
from app.modules.arenas.service import get_all_arenas, get_arena_by_slug

router = APIRouter(prefix="/api/arenas", tags=["arenas"])


@router.get("", response_model=list[ArenaSchema])
def list_arenas(db: Session = Depends(get_db)):
    return get_all_arenas(db)


@router.get("/{slug}", response_model=ArenaSchema)
def get_arena(slug: str, db: Session = Depends(get_db)):
    arena = get_arena_by_slug(slug, db)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return arena