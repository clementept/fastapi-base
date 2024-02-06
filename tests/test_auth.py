import pytest
from jose import jwt

from app.config import settings
from app.schemas.login import LoginResponse


def test_login_user(client, test_user):
    res = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_res = LoginResponse(**res.json())
    print(res.json())

    payload = jwt.decode(
        login_res.access_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorythm],
    )
    id = payload.get("user_id")

    assert res.status_code == 200
    assert login_res.token_type == "bearer"
    assert id == test_user["id"]


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@mail.com", "123", 403),
        ("wrongemail@mail.com", "wrong password", 403),
        ("hello@mail.com", "wrong password", 403),
        (None, "123", 422),
        ("hello@mail.com", None, 422),
    ],
)
def test_incorrect_login(client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code
