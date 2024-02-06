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

def test_get_user_by_id(db_client, test_user):
    res = db_client.get(f"/users/{int(test_user["id"])}")

    res_json = res.json()

    assert res.status_code == 200
    assert res_json['id'] == test_user["id"]
    assert res_json['email'] == test_user["email"]
    assert res_json['created_at'] == test_user["created_at"]
