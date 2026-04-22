from fastapi.testclient import TestClient

from api.app.main import app

client = TestClient(app)


def test_saude_deve_retornar_ok() -> None:
    response = client.get("/saude")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
