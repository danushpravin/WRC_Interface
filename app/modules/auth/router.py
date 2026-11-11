from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.modules.auth.service import register_user, login_user
from app.core.dependencies import get_current_user
from app.modules.users.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(data, db)
        return {"message": "Account created", "gamer_name": user.gamer_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return login_user(data, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "gamer_name": current_user.gamer_name,
        "role": current_user.role.value,
    }