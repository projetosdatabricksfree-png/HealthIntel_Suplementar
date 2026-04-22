from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.app.main import app

client = TestClient(app)


def test_saude_deve_publicar_headers_de_seguranca() -> None:
    response = client.get("/saude")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-Request-ID" in response.headers


def test_hardening_deve_bloquear_payload_maior_que_limite() -> None:
    response = client.get("/saude", headers={"Content-Length": str(2_000_000)})

    assert response.status_code == 413
    body = response.json()
    assert body["detail"]["codigo_erro"] == "PAYLOAD_EXCEDIDO"


@patch("api.app.main.obter_prontidao", new_callable=AsyncMock)
def test_prontidao_deve_retornar_503_quando_dependencia_falha(
    mock_obter_prontidao: AsyncMock,
) -> None:
    mock_obter_prontidao.return_value = {
        "status": "indisponivel",
        "ambiente": "local",
        "versao": "0.1.0",
        "dependencias": {"postgres": {"status": "erro", "mensagem": "timeout"}},
    }

    response = client.get("/prontidao")

    assert response.status_code == 503
    assert response.json()["status"] == "indisponivel"
