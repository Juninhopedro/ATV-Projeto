import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()
SECRET_KEY = os.getenv("JWT_SECRET", "DEV_ONLY_CHANGE_THIS_SECRET_BEFORE_DEPLOYMENT")
ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "120"))

def hash_password(password: str) -> str:
    return _password_hash.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)

def create_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": username, "iat": now, "exp": now + timedelta(minutes=TOKEN_MINUTES)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
    except jwt.PyJWTError:
        return None
