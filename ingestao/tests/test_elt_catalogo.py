from __future__ import annotations

import pytest

from ingestao.app.elt import catalogo


@pytest.mark.asyncio
async def test_salvar_fontes_descobertas_executa_upsert(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas = []

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def execute(self, sql, params):
            chamadas.append((str(sql), params))

        async def commit(self):
            chamadas.append(("commit", None))

    monkeypatch.setattr(catalogo, "SessionLocal", lambda: FakeSession())
    total = await catalogo.salvar_fontes_descobertas(
        [
            {
                "dataset_codigo": "cadop_operadoras_ativas",
                "familia": "cadop",
                "url": "https://dadosabertos.ans.gov.br/FTP/PDA/cadop.csv",
                "diretorio_origem": "https://dadosabertos.ans.gov.br/FTP/PDA/",
                "nome_arquivo": "cadop.csv",
                "extensao": "csv",
                "tipo_arquivo": "tabular",
                "tamanho_bytes": 10,
                "last_modified": None,
                "ativo": True,
                "prioridade": 10,
                "escopo": "sector_core",
            }
        ]
    )

    assert total == 1
    assert "on conflict (url) do update" in chamadas[0][0].lower()
    assert chamadas[0][1][0]["familia"] == "cadop"


@pytest.mark.asyncio
async def test_listar_fontes_para_download_filtra_familias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas = []

    class FakeResult:
        def __iter__(self):
            return iter([])

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def execute(self, sql, params):
            chamadas.append((str(sql), params))
            return FakeResult()

    monkeypatch.setattr(catalogo, "SessionLocal", lambda: FakeSession())
    fontes = await catalogo.listar_fontes_para_download(
        escopo="sector_core", familias=["cadop"], limite=5
    )

    assert fontes == []
    assert chamadas[0][1]["familias"] == ["cadop"]
    assert chamadas[0][1]["limite"] == 5
