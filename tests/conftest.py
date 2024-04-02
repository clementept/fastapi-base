import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.backend.config import settings
from app.backend.database import Base, get_db
from app.main import app
from app.models.user import UserModel
from app.services.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{
    settings.database_hostname}:{settings.database_port}/{settings.test_database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = 'adminpass'

@pytest.fixture
def test_inactive_user(client):
    res = client.post(
        "/users", json={"email": "user@mail.com", "password": "123"})

    new_user = res.json()
    new_user["password"] = "123"

    return new_user

@pytest.fixture
def test_active_user(client):
    res = client.post(
        "/users", json={"email": "user@mail.com", "password": "123"})

    new_user = res.json()
    new_user["password"] = "123"

    client.post(f"/users/activate?activation_code={new_user['activation_code']}")

    return new_user


@pytest.fixture
def test_user2(client):
    res = client.post(
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
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    test_client.base_url = str(test_client.base_url) +settings.base_url_suffix

    yield test_client


@pytest.fixture
def token(test_active_user):
    return create_access_token({"user_id": test_active_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture
def authorized_admin(client, session):
    # Create the admin user using the SQLAlchemy ORM
    admin_user = UserModel(email=ADMIN_EMAIL, password=ADMIN_PASSWORD, is_active=True, is_admin=True)
    
    # Add the user to the session and commit the transaction
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)

    token = create_access_token({"user_id": admin_user.id})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }    

    return client
