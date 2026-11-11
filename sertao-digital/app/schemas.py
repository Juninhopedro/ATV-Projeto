from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, StrictInt


Username = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=50),
]
Password = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=128),
]


class Credentials(BaseModel):
    username: Username
    password: Password


class TransferRequest(BaseModel):
    destino: Username
    # StrictInt impede coerção de "150", 150.0 e true para inteiro.
    valor: StrictInt = Field(gt=0)


class UserCreated(BaseModel):
    username: str


class TokenResponse(BaseModel):
    token: str


class AccountResponse(BaseModel):
    username: str
    saldo: int


class TransferResponse(BaseModel):
    id: int
    origem: str
    destino: str
    valor: int
    saldo: int


class AuditResponse(BaseModel):
    usuarios: int
    somaSaldos: int
    transferencias: int
