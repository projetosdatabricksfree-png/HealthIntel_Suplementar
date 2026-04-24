from __future__ import annotations

import pytest

from ingestao.app.elt.classifier import classificar_fonte_ans
from ingestao.app.elt.discovery import descobrir_fontes_ans


def test_classificar_urls_ans_prioritarias() -> None:
    cadop = classificar_fonte_ans(
        "https://dadosabertos.ans.gov.br/FTP/PDA/"
        "operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
    )
    sib = classificar_fonte_ans(
        "https://dadosabertos.ans.gov.br/FTP/PDA/"
        "dados_de_beneficiarios_por_operadora/sib_ativo_AC.zip"
    )
    tiss = classificar_fonte_ans("https://dadosabertos.ans.gov.br/FTP/PDA/TISS/AMBULATORIAL/")

    assert cadop["familia"] == "cadop"
    assert cadop["dataset_codigo"] == "cadop_operadoras_ativas"
    assert sib["familia"] == "sib"
    assert sib["dataset_codigo"] == "sib_ativo_uf"
    assert tiss["familia"] == "tiss"
    assert tiss["dataset_codigo"] == "tiss_ambulatorial"


@pytest.mark.asyncio
async def test_discovery_parseia_indice_html(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html><body>
      <a href="../">Parent Directory</a>
      <a href="operadoras_de_plano_de_saude_ativas/">CADOP</a>
      <a href="TISS/">TISS</a>
    </body></html>
    """
    cadop_html = '<a href="Relatorio_cadop.csv">Relatorio_cadop.csv</a>'
    tiss_html = '<a href="AMBULATORIAL/">AMBULATORIAL</a>'
    tiss_amb_html = '<a href="tiss_ambulatorial_2025.zip">tiss_ambulatorial_2025.zip</a>'

    class FakeResponse:
        def __init__(self, text: str = "", headers: dict | None = None) -> None:
            self.text = text
            self.headers = headers or {}

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url: str):
            if url.endswith("/FTP/PDA/"):
                return FakeResponse(html)
            if url.endswith("operadoras_de_plano_de_saude_ativas/"):
                return FakeResponse(cadop_html)
            if url.endswith("/TISS/"):
                return FakeResponse(tiss_html)
            return FakeResponse(tiss_amb_html)

        async def head(self, url: str, follow_redirects: bool = True):
            return FakeResponse(headers={"content-length": "123"})

    monkeypatch.setattr("ingestao.app.elt.discovery.httpx.AsyncClient", lambda **_: FakeClient())

    fontes = await descobrir_fontes_ans(max_depth=3, escopo="sector_core")

    assert {fonte["familia"] for fonte in fontes} == {"cadop", "tiss"}
    assert {fonte["nome_arquivo"] for fonte in fontes} == {
        "Relatorio_cadop.csv",
        "tiss_ambulatorial_2025.zip",
    }
