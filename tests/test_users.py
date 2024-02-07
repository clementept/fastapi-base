from app.schemas.user import UserResponseSchema


def test_create_user(client):
    res = client.post("/users", json={"email": "hello@mail.com", "password": "123"})

    new_user = UserResponseSchema(**res.json())
    assert res.status_code == 201
    assert new_user.email == "hello@mail.com"

def test_get_user_by_id(authorized_client, test_user):
    res = authorized_client.get(f"/users/{int(test_user["id"])}")
    res_json = res.json()

    assert res.status_code == 200
    assert res_json['id'] == test_user["id"]
    assert res_json['email'] == test_user["email"]
    assert res_json['created_at'] == test_user["created_at"]

def test_get_user_me(authorized_client, test_user):
    res = authorized_client.get(f"/users/{int(test_user["id"])}")

    res_json = res.json()

    assert res.status_code == 200
    assert res_json['id'] == test_user["id"]
    assert res_json['email'] == test_user["email"]
    assert res_json['created_at'] == test_user["created_at"]

def test_get_user_me_unauthorized(client, test_user):
    res = client.get(f"/users/{int(test_user["id"])}")

    assert res.status_code == 401
