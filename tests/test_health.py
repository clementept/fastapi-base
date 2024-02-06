def test_health(db_client):
    res = db_client.get("/health")
    print(res.json().get("message"))
    assert res.status_code == 200
    assert res.json().get("message") == "App running"
