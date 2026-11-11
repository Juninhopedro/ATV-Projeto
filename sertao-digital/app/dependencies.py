from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_token


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": "NAO_AUTENTICADO"})

    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.casefold() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail={"error": "NAO_AUTENTICADO"})

    username = decode_token(token.strip())
    if not username:
        raise HTTPException(status_code=401, detail={"error": "NAO_AUTENTICADO"})

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail={"error": "NAO_AUTENTICADO"})
    return user
