from datetime import datetime, timedelta
from threading import RLock

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from ..database import get_db, is_postgres, is_sqlite
from ..dependencies import current_user
from ..models import Transfer, User
from ..schemas import TransferRequest, TransferResponse

router = APIRouter(tags=["Transferências"])
SQLITE_TRANSFER_LOCK = RLock()


def _process_transfer(data: TransferRequest, user: User, db: Session):
    # A origem é sempre o usuário autenticado; o cliente não escolhe a conta de origem.
    if data.destino == user.username:
        raise HTTPException(status_code=422, detail={"error": "MESMA_CONTA"})

    destination = db.query(User).filter(User.username == data.destino).first()
    if destination is None:
        raise HTTPException(status_code=404, detail={"error": "DESTINO_INEXISTENTE"})

    try:
        if is_postgres:
            # Lock transacional por origem/destino/valor. Requisições idênticas
            # concorrentes ficam serializadas até commit ou rollback.
            duplicate_key = f"{user.id}:{destination.id}:{data.valor}"
            db.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key, 0))"),
                {"lock_key": duplicate_key},
            )

        # Usa o relógio do PostgreSQL após adquirir o lock. clock_timestamp()
        # evita usar o início antigo da transação (now()) depois de uma espera.
        # '>' implementa estritamente menos de 60 segundos.
        if is_sqlite:
            cutoff = datetime.utcnow() - timedelta(seconds=60)
            duplicate = db.scalar(
                select(Transfer.id)
                .where(
                    Transfer.origin_id == user.id,
                    Transfer.destination_id == destination.id,
                    Transfer.amount == data.valor,
                    Transfer.created_at > cutoff,
                )
                .limit(1)
            )
        else:
            duplicate = db.scalar(
                select(Transfer.id)
                .where(
                    Transfer.origin_id == user.id,
                    Transfer.destination_id == destination.id,
                    Transfer.amount == data.valor,
                    Transfer.created_at > func.clock_timestamp() - text("INTERVAL '60 seconds'"),
                )
                .limit(1)
            )
        if duplicate is not None:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={"error": "TRANSFERENCIA_DUPLICADA"},
            )

        # A duplicidade sempre é verificada antes do saldo, conforme o contrato.
        # Bloqueia as contas em ordem crescente para reduzir deadlocks.
        account_ids = sorted((user.id, destination.id))
        locked_accounts = (
            db.query(User)
            .filter(User.id.in_(account_ids))
            .order_by(User.id)
            .with_for_update()
            # IMPORTANTE: força refresh dos objetos já presentes no identity map
            # (current_user e destination), evitando saldo antigo após esperar lock.
            .populate_existing()
            .all()
        )
        accounts = {account.id: account for account in locked_accounts}
        origin = accounts[user.id]
        target = accounts[destination.id]

        if origin.balance < data.valor:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={"error": "SALDO_INSUFICIENTE"},
            )

        # Débito, crédito e registro pertencem à mesma transação PostgreSQL.
        origin.balance -= data.valor
        target.balance += data.valor
        record = Transfer(
            origin_id=origin.id,
            destination_id=target.id,
            amount=data.valor,
        )
        db.add(record)
        db.flush()

        response = {
            "id": record.id,
            "origem": origin.username,
            "destino": target.username,
            "valor": data.valor,
            "saldo": origin.balance,
        }
        db.commit()
        return response

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


@router.post(
    "/transferencias",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
)
def transfer(
    data: TransferRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_sqlite:
        with SQLITE_TRANSFER_LOCK:
            return _process_transfer(data, user, db)
    return _process_transfer(data, user, db)
