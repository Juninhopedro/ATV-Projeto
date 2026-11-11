from fastapi import APIRouter, Depends
from ..dependencies import current_user
from ..models import User

router = APIRouter(tags=["Conta"])

@router.get("/conta")
def account(user: User = Depends(current_user)):
    return {"username": user.username, "saldo": user.balance}
