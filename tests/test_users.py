import pytest
from jose import jwt

from app.config import settings
from app.schemas.login import LoginResponse
from app.schemas.user import UserResponse


def test_create_user(db_client):
    res = db_client.post("/users", json={"email": "hello@mail.com", "password": "123"})

    new_user = UserResponse(**res.json())
    assert res.status_code == 201
    assert new_user.email == "hello@mail.com"
