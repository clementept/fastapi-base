def test_health(client):
    res = client.get("/health")
    print(res.json().get("message"))
    assert res.status_code == 200
    assert res.json().get("message") == "App running"
