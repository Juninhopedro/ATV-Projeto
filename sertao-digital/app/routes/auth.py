from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import Credentials, UserCreated, TokenResponse
from ..security import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/registrar", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
def register(data: Credentials, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail={"error": "USUARIO_EXISTENTE"})
    user = User(username=data.username, password_hash=hash_password(data.password), balance=1000)
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        # Também cobre duas tentativas de cadastro concorrentes.
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(status_code=409, detail={"error": "USUARIO_EXISTENTE"})
        raise
    return {"username": user.username}

@router.post("/login", response_model=TokenResponse)
def login(data: Credentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail={"error": "CREDENCIAIS_INVALIDAS"})
    return {"token": create_token(user.username)}
