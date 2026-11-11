import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# A aplicação e os fixtures apontam para o banco exclusivo de testes ANTES
# de importar app.database/app.main. Nunca executar pytest no banco principal.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./sertao_digital_test.db",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.database import Base, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402

TestingSession = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_user(client, username):
    response = client.post(
        "/auth/registrar",
        json={"username": username, "password": "senha123"},
    )
    assert response.status_code == 201, response.text
    login = client.post(
        "/auth/login",
        json={"username": username, "password": "senha123"},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['token']}"}
