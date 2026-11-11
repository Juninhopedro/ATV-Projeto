from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier

from fastapi import Depends, Header
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from .conftest import TestingSession, create_user
from app.database import get_db, is_sqlite
from app.main import app
from app.dependencies import current_user
from app.models import Transfer, User
from app.security import decode_token


def synchronized_user_override(barrier):
    """Carrega o usuário em cada sessão e só então libera as requisições juntas."""
    def dependency(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
        scheme, _, token = (authorization or "").partition(" ")
        assert scheme.casefold() == "bearer" and token
        username = decode_token(token)
        assert username
        user = db.query(User).filter(User.username == username).one()
        barrier.wait(timeout=10)
        return user

    return dependency


def test_register_login_and_initial_account(client):
    headers = create_user(client, "joao")
    response = client.get("/conta", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"username": "joao", "saldo": 1000}

    with TestingSession() as db:
        stored = db.query(User).filter_by(username="joao").one()
        assert stored.password_hash != "senha123"
        assert stored.password_hash.startswith("$argon2")


def test_duplicate_user_has_exact_contract(client):
    create_user(client, "joao")
    response = client.post(
        "/auth/registrar",
        json={"username": "joao", "password": "senha123"},
    )
    assert response.status_code == 409
    assert response.json() == {"error": "USUARIO_EXISTENTE"}


def test_invalid_login_has_exact_contract_even_for_short_password(client):
    response = client.post(
        "/auth/login",
        json={"username": "inexistente", "password": "x"},
    )
    assert response.status_code == 401
    assert response.json() == {"error": "CREDENCIAIS_INVALIDAS"}


def test_authentication_required_and_invalid_token(client):
    for headers in ({}, {"Authorization": "Bearer token-invalido"}, {"Authorization": "Basic abc"}):
        response = client.get("/conta", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"error": "NAO_AUTENTICADO"}

        response = client.post(
            "/transferencias",
            headers=headers,
            json={"destino": "maria", "valor": 10},
        )
        assert response.status_code == 401
        assert response.json() == {"error": "NAO_AUTENTICADO"}


def test_transfer_and_audit_conserve_all_coins(client):
    joao = create_user(client, "joao")
    maria = create_user(client, "maria")
    response = client.post(
        "/transferencias",
        headers=joao,
        json={"destino": "maria", "valor": 150},
    )
    assert response.status_code == 201
    assert response.json()["saldo"] == 850
    assert client.get("/conta", headers=joao).json()["saldo"] == 850
    assert client.get("/conta", headers=maria).json()["saldo"] == 1150
    assert client.get("/auditoria").json() == {
        "usuarios": 2,
        "somaSaldos": 2000,
        "transferencias": 1,
    }


def test_client_cannot_choose_another_origin(client):
    joao = create_user(client, "joao")
    maria = create_user(client, "maria")
    carlos = create_user(client, "carlos")

    response = client.post(
        "/transferencias",
        headers=joao,
        json={"origem": "maria", "destino": "carlos", "valor": 100},
    )
    assert response.status_code == 201
    assert response.json()["origem"] == "joao"
    assert client.get("/conta", headers=joao).json()["saldo"] == 900
    assert client.get("/conta", headers=maria).json()["saldo"] == 1000
    assert client.get("/conta", headers=carlos).json()["saldo"] == 1100


def test_duplicate_transfer_is_rejected_without_second_debit(client):
    joao = create_user(client, "joao")
    create_user(client, "maria")
    payload = {"destino": "maria", "valor": 100}

    first = client.post("/transferencias", headers=joao, json=payload)
    second = client.post("/transferencias", headers=joao, json=payload)
    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json() == {"error": "TRANSFERENCIA_DUPLICADA"}
    assert client.get("/conta", headers=joao).json()["saldo"] == 900
    assert client.get("/auditoria").json()["transferencias"] == 1


def test_duplicate_check_precedes_insufficient_balance(client):
    joao = create_user(client, "joao")
    create_user(client, "maria")
    payload = {"destino": "maria", "valor": 800}

    first = client.post("/transferencias", headers=joao, json=payload)
    repeated = client.post("/transferencias", headers=joao, json=payload)
    assert first.status_code == 201
    assert client.get("/conta", headers=joao).json()["saldo"] == 200
    assert repeated.status_code == 409
    assert repeated.json() == {"error": "TRANSFERENCIA_DUPLICADA"}


def test_same_transfer_is_allowed_at_or_after_60_seconds(client):
    joao = create_user(client, "joao")
    create_user(client, "maria")
    payload = {"destino": "maria", "valor": 100}
    first = client.post("/transferencias", headers=joao, json=payload)
    assert first.status_code == 201

    with TestingSession() as db:
        if is_sqlite:
            db.query(Transfer).update({Transfer.created_at: datetime.utcnow() - timedelta(seconds=60)})
        else:
            db.query(Transfer).update(
                {Transfer.created_at: func.clock_timestamp() - text("INTERVAL '60 seconds'")}
            )
        db.commit()

    second = client.post("/transferencias", headers=joao, json=payload)
    assert second.status_code == 201
    assert client.get("/auditoria").json()["transferencias"] == 2


def test_insufficient_balance_exact_error(client):
    joao = create_user(client, "joao")
    create_user(client, "maria")
    response = client.post(
        "/transferencias",
        headers=joao,
        json={"destino": "maria", "valor": 1001},
    )
    assert response.status_code == 409
    assert response.json() == {"error": "SALDO_INSUFICIENTE"}


def test_transfer_business_rejections_exact_errors(client):
    joao = create_user(client, "joao")

    same = client.post(
        "/transferencias",
        headers=joao,
        json={"destino": "joao", "valor": 10},
    )
    assert same.status_code == 422
    assert same.json() == {"error": "MESMA_CONTA"}

    missing = client.post(
        "/transferencias",
        headers=joao,
        json={"destino": "naoexiste", "valor": 10},
    )
    assert missing.status_code == 404
    assert missing.json() == {"error": "DESTINO_INEXISTENTE"}



def test_invalid_amounts_are_strict_and_have_exact_error(client):
    joao = create_user(client, "joao")
    invalid_payloads = [
        {"destino": "maria"},
        {"destino": "maria", "valor": None},
        {"destino": "maria", "valor": "150"},
        {"destino": "maria", "valor": 150.0},
        {"destino": "maria", "valor": True},
        {"destino": "maria", "valor": 0},
        {"destino": "maria", "valor": -1},
    ]
    for payload in invalid_payloads:
        response = client.post("/transferencias", headers=joao, json=payload)
        assert response.status_code == 422, (payload, response.text)
        assert response.json() == {"error": "VALOR_INVALIDO"}


def test_concurrent_identical_requests_create_exactly_one_transfer(client):
    joao = create_user(client, "joao")
    create_user(client, "maria")
    payload = {"destino": "maria", "valor": 100}

    barrier = Barrier(8)
    app.dependency_overrides[current_user] = synchronized_user_override(barrier)
    try:
        def send_one(_):
            return client.post("/transferencias", headers=joao, json=payload)

        with ThreadPoolExecutor(max_workers=8) as executor:
            responses = list(executor.map(send_one, range(8)))
    finally:
        app.dependency_overrides.pop(current_user, None)

    statuses = [response.status_code for response in responses]
    assert statuses.count(201) == 1, statuses
    assert statuses.count(409) == 7, statuses
    assert all(
        response.json() == {"error": "TRANSFERENCIA_DUPLICADA"}
        for response in responses
        if response.status_code == 409
    )
    assert client.get("/auditoria").json() == {
        "usuarios": 2,
        "somaSaldos": 2000,
        "transferencias": 1,
    }


def test_concurrent_different_transfers_refresh_locked_balance(client):
    joao = create_user(client, "joao")
    create_user(client, "maria")
    create_user(client, "pedro")

    barrier = Barrier(2)
    app.dependency_overrides[current_user] = synchronized_user_override(barrier)
    try:
        def send(destination):
            return client.post(
                "/transferencias",
                headers=joao,
                json={"destino": destination, "valor": 700},
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(send, ["maria", "pedro"]))
    finally:
        app.dependency_overrides.pop(current_user, None)

    statuses = [response.status_code for response in responses]
    assert statuses.count(201) == 1, [r.text for r in responses]
    assert statuses.count(409) == 1, [r.text for r in responses]
    rejected = next(r for r in responses if r.status_code == 409)
    assert rejected.json() == {"error": "SALDO_INSUFICIENTE"}

    audit = client.get("/auditoria").json()
    assert audit == {"usuarios": 3, "somaSaldos": 3000, "transferencias": 1}
    assert client.get("/conta", headers=joao).json()["saldo"] == 300


def test_failure_after_flush_rolls_back_debit_credit_and_transfer(client):
    joao = create_user(client, "joao")
    maria = create_user(client, "maria")

    def failing_get_db():
        db = TestingSession()
        original_flush = db.flush

        def flush_then_fail(*args, **kwargs):
            original_flush(*args, **kwargs)
            raise RuntimeError("falha simulada depois do flush")

        db.flush = flush_then_fail
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = failing_get_db
    try:
        response = client.post(
            "/transferencias",
            headers=joao,
            json={"destino": "maria", "valor": 250},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"error": "ERRO_INTERNO"}
    assert client.get("/conta", headers=joao).json()["saldo"] == 1000
    assert client.get("/conta", headers=maria).json()["saldo"] == 1000
    assert client.get("/auditoria").json()["transferencias"] == 0


def test_audit_is_public(client):
    response = client.get("/auditoria")
    assert response.status_code == 200
    assert response.json() == {"usuarios": 0, "somaSaldos": 0, "transferencias": 0}
