from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base, is_sqlite


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    balance: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1000,
        server_default=text("1000"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP") if is_sqlite else func.clock_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_users_balance_nonnegative"),
    )


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP") if is_sqlite else func.clock_timestamp(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
        CheckConstraint("origin_id <> destination_id", name="ck_transfers_different_accounts"),
        Index(
            "ix_transfer_duplicate_lookup",
            "origin_id",
            "destination_id",
            "amount",
            "created_at",
        ),
    )
