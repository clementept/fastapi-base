from app.schemas.user import UserResponseSchema


def test_create_user(client):
    res = client.post("/users", json={"email": "hello@mail.com", "password": "123"})

    new_user = UserResponseSchema(**res.json())
    assert res.status_code == 201
    assert new_user.email == "hello@mail.com"

def test_get_user_by_id(authorized_client, test_active_user):
    res = authorized_client.get(f"/users/{int(test_active_user["id"])}")
    res_json = res.json()

    assert res.status_code == 200
    assert res_json['id'] == test_active_user["id"]
    assert res_json['email'] == test_active_user["email"]
    assert res_json['created_at'] == test_active_user["created_at"]

def test_get_user_by_id_inexistent_id(authorized_client):
    res = authorized_client.get(f"/users/8888")

    assert res.status_code == 404
    assert res.json()['detail'] == "User with id 8888 not found"

def test_get_user_by_id_unauthorized(client, test_active_user):
    res = client.get(f"/users/{int(test_active_user["id"])}")
    res_json = res.json()

    assert res.status_code == 401

def test_get_user_me(authorized_client, test_active_user):
    res = authorized_client.get(f"/users/me")

    res_json = res.json()

    assert res.status_code == 200
    assert res_json['id'] == test_active_user["id"]
    assert res_json['email'] == test_active_user["email"]
    assert res_json['created_at'] == test_active_user["created_at"]

def test_get_user_me_unauthorized(client, test_inactive_user):
    res = client.get(f"/users/{int(test_inactive_user["id"])}")

    assert res.status_code == 401

def test_user_activation_wrong_code(client, test_inactive_user):
    res = client.post("/users/activate?activation_code=123")

    assert res.status_code == 400
    assert res.json()['detail'] == 'Wrong activation code'

def test_user_activation_correct_code(client, test_inactive_user):
    assert test_inactive_user['is_active'] == False

    res = client.post(f"/users/activate?activation_code={test_inactive_user['activation_code']}")

    assert res.status_code == 200
    assert res.json()['is_active'] == True
    assert res.json()['activation_code'] == None
