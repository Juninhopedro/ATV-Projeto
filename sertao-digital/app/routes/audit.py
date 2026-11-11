from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Transfer, User

router = APIRouter(tags=["Auditoria"])


@router.get("/auditoria")
def audit(db: Session = Depends(get_db)):
    # Uma única instrução SQL garante uma visão consistente do mesmo snapshot.
    statement = select(
        func.count(User.id).label("usuarios"),
        func.coalesce(func.sum(User.balance), 0).label("soma_saldos"),
        select(func.count(Transfer.id)).scalar_subquery().label("transferencias"),
    )
    row = db.execute(statement).one()
    return {
        "usuarios": row.usuarios,
        "somaSaldos": row.soma_saldos,
        "transferencias": row.transferencias,
    }
