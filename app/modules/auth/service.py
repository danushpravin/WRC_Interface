from sqlalchemy.orm import Session

from app.modules.users.models import User, UserRole
from app.modules.auth.schemas import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token

def register_user(data: RegisterRequest, db: Session) -> User:
    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ValueError("Email already registered")
    
    # Check if gamer_name already exists
    existing_name = db.query(User).filter(User.gamer_name == data.gamer_name).first()
    if existing_name:
        raise ValueError("Game name already taken")
    
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        gamer_name=data.gamer_name,
        country_code=data.country_code,
        role=UserRole.player,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(data: LoginRequest, db: Session) -> dict:
    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise ValueError("Invalid email or password")
    
    # Check password
    if not verify_password(data.password, user.password_hash):
        raise ValueError("Invalid email or password")

    # Check account status
    if user.status.value != "active":
        raise ValueError("Account is suspended or banned")
    
    # Create JWT token
    token = create_access_token({"sub": str(user.id), "role": user.role.value})

    return {"access_token": token, "token_type": "bearer", "role": user.role.value}