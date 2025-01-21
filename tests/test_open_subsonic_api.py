import json
from src.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_ping():
    response = client.get("/rest/ping")
    assert response.status_code == 200

    rsp = response.json()["subsonic-response"]
    assert rsp["status"] == "ok"
    assert rsp["type"] == "MusicRitmo"
    assert rsp["openSubsonic"] == True
    assert rsp["version"] is not None
    assert rsp["serverVersion"] is not None

def test_search():
    query = "track"
    response = client.post("/rest/search", json={"query": query})
    assert response.status_code == 200

    rsp = response.json()["subsonic-response"]
    assert rsp["status"] == "ok"
    assert rsp["searchResult"] is not None
    for _, v in rsp["searchResult"].items():
        print(v)
        for i in v:
            res = json.loads(i)
            assert query in res["name"]
