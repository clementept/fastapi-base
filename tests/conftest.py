import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{
    settings.database_hostname}:{settings.database_port}/{settings.test_database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_user(db_client):
    res = db_client.post(
        "/users", json={"email": "user@mail.com", "password": "123"})

    new_user = res.json()
    new_user["password"] = "123"

    return new_user


@pytest.fixture
def test_user2(db_client):
    res = db_client.post(
        "/users", json={"email": "user2@mail.com", "password": "123"})

    new_user = res.json()
    new_user["password"] = "123"

    return new_user


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def db_client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(db_client, token):
    db_client.headers = {
        **db_client.headers,
        "Authorization": f"Bearer {token}"
    }

    return db_client
