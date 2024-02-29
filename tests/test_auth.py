import pytest
from jose import jwt

from app.backend.config import settings
from app.schemas.login import LoginResponseSchema


def test_login_inactive_user(client, test_inactive_user):
    res = client.post(
        "/login",
        data={
            "username": test_inactive_user["email"],
            "password": test_inactive_user["password"],
        },
    )

    assert res.status_code == 403
    assert res.json() == {"detail": "User is not active"}


def test_login_active_user(client, test_active_user):
    res = client.post(
        "/login",
        data={
            "username": test_active_user["email"],
            "password": test_active_user["password"],
        },
    )
    login_res = LoginResponseSchema(**res.json())

    payload = jwt.decode(
        login_res.access_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorythm],
    )
    id = payload.get("user_id")

    assert res.status_code == 200
    assert login_res.token_type == "bearer"
    assert "access_token" in login_res.model_dump()
    assert "refresh_token" in res.cookies
    assert "refresh_token" not in login_res.model_dump()
    assert id == test_active_user["id"]


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


def test_refresh_user(client, test_active_user):
    login_res = client.post(
        "/login",
        data={
            "username": test_active_user["email"],
            "password": test_active_user["password"],
        },
    )

    refresh_token = login_res.cookies["refresh_token"]

    client.cookies.update({"refresh_token": refresh_token}),

    refresh_res = client.get(
        "/login/refresh",
    )

    refresh_res_json = refresh_res.json()
    assert refresh_res.status_code == 200
    assert refresh_res_json["token_type"] == "bearer"
    assert "access_token" in refresh_res_json
    assert "refresh_token" not in refresh_res_json


def test_refresh_user_no_refresh_token_cookie(client, test_active_user):
    refresh_res = client.get("/login/refresh")

    assert refresh_res.status_code == 401
    assert refresh_res.json()["detail"] == "Invalid refresh token"


def test_refresh_user_invalid_token(client, test_active_user):
    login_res = client.post(
        "/login",
        data={
            "username": test_active_user["email"],
            "password": test_active_user["password"],
        },
    )
    login_res = LoginResponseSchema(**login_res.json())

    client.cookies.update({"refresh_token": "abc"})
    refresh_res = client.get("/login/refresh")

    refresh_res_json = refresh_res.json()
    assert refresh_res.status_code == 401
    assert refresh_res_json == {"detail": "Invalid refresh token"}


def test_logout_endpoint(client):
    logout_res = client.get("/logout")

    assert logout_res.status_code == 204
