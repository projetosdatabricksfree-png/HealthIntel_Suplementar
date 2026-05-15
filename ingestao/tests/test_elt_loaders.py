from __future__ import annotations

import zipfile

import pytest

from ingestao.app.elt import downloader, loaders

DATASETS_NUNCA_GENERICOS = [
    ("produto_prestador_hospitalar", "rede_prestadores"),
    ("operadora_prestador_nao_hospitalar", "rede_prestadores"),
    ("prestador_acreditado", "rede_prestadores"),
    ("rede_assistencial", "rede_assistencial"),
    ("cnes", "cnes"),
    ("tiss_ambulatorial", "tiss"),
    ("tiss_hospitalar", "tiss"),
    ("tiss_dados_plano", "tiss"),
    ("tiss_procedimento", "tiss"),
    ("diops", "diops"),
    ("fip", "fip"),
    ("ntrp", "precificacao_ntrp"),
    ("sip", "sip"),
    ("sib", "sib"),
]


@pytest.mark.asyncio
async def test_csv_pequeno_carrega_em_linha_generica(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_path = tmp_path / "dados.csv"
    csv_path.write_text("codigo;nome\n1;Teste\n2;Outro\n", encoding="utf-8")
    batches = []
    status = []

    async def fake_inserir(arquivo, batch):
        batches.append(batch)
        return len(batch)

    async def fake_status(arquivo_id, novo_status, erro_mensagem=None):
        status.append((arquivo_id, novo_status, erro_mensagem))

    monkeypatch.setattr(loaders, "_inserir_linhas_genericas", fake_inserir)
    monkeypatch.setattr(loaders, "_marcar_status_arquivo", fake_status)

    resultado = await loaders.carregar_arquivo_tabular_generico(
        {
            "id": "arquivo-1",
            "dataset_codigo": "ans_pda_generico",
            "familia": "desconhecido",
            "nome_arquivo": "dados.csv",
            "hash_arquivo": "hash",
            "caminho_landing": str(csv_path),
            "extensao": "csv",
        }
    )

    assert resultado["status"] == "carregado"
    assert resultado["linhas_carregadas"] == 2
    assert batches[0][0][1] == {"codigo": "1", "nome": "Teste"}
    assert status == [("arquivo-1", "carregado", None)]


@pytest.mark.asyncio
async def test_zip_com_csv_allowlist_carrega_streaming(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    zip_path = tmp_path / "dados.zip"
    with zipfile.ZipFile(zip_path, "w") as pacote:
        pacote.writestr("dados.csv", "codigo;nome\n1;Teste\n")
    total = []

    async def fake_inserir(arquivo, batch):
        total.append(len(batch))
        return len(batch)

    async def fake_status(arquivo_id, novo_status, erro_mensagem=None):
        return None

    monkeypatch.setattr(loaders, "_inserir_linhas_genericas", fake_inserir)
    monkeypatch.setattr(loaders, "_marcar_status_arquivo", fake_status)

    resultado = await loaders.carregar_arquivo_tabular_generico(
        {
            "id": "arquivo-1",
            "dataset_codigo": "historico_sob_demanda",
            "familia": "historico_sob_demanda",
            "nome_arquivo": "dados.zip",
            "hash_arquivo": "hash",
            "caminho_landing": str(zip_path),
            "extensao": "zip",
        }
    )

    assert resultado["linhas_carregadas"] == 1
    assert total == [1]


@pytest.mark.asyncio
@pytest.mark.parametrize(("dataset_codigo", "familia"), DATASETS_NUNCA_GENERICOS)
async def test_datasets_criticos_nunca_usam_linha_generica(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    dataset_codigo: str,
    familia: str,
) -> None:
    csv_path = tmp_path / f"{dataset_codigo}.csv"
    csv_path.write_text("codigo;nome\n1;Teste\n", encoding="utf-8")
    insercoes = []
    bloqueios = []

    async def fake_inserir(arquivo, batch):
        insercoes.append(batch)
        return len(batch)

    async def fake_bloqueio(arquivo, *, status, mensagem, linhas_lidas=None):
        bloqueios.append((arquivo["dataset_codigo"], status, mensagem, linhas_lidas))

    monkeypatch.setattr(loaders, "_inserir_linhas_genericas", fake_inserir)
    monkeypatch.setattr(loaders, "_registrar_bloqueio_generico", fake_bloqueio)

    resultado = await loaders.carregar_arquivo_tabular_generico(
        {
            "id": "arquivo-critico",
            "dataset_codigo": dataset_codigo,
            "familia": familia,
            "url": f"https://dadosabertos.ans.gov.br/{dataset_codigo}.csv",
            "nome_arquivo": f"{dataset_codigo}.csv",
            "hash_arquivo": "hash",
            "caminho_landing": str(csv_path),
            "extensao": "csv",
        }
    )

    assert resultado["status"] == "LAYOUT_NAO_MAPEADO"
    assert "bronze canonica" in resultado["erro"]
    assert insercoes == []
    assert bloqueios and bloqueios[0][0] == dataset_codigo


@pytest.mark.asyncio
async def test_dataset_fora_allowlist_nao_usa_linha_generica(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_path = tmp_path / "desconhecido.csv"
    csv_path.write_text("codigo;nome\n1;Teste\n", encoding="utf-8")
    bloqueios = []

    async def fake_bloqueio(arquivo, *, status, mensagem, linhas_lidas=None):
        bloqueios.append((status, mensagem, linhas_lidas))

    monkeypatch.setattr(loaders, "_registrar_bloqueio_generico", fake_bloqueio)

    resultado = await loaders.carregar_arquivo_tabular_generico(
        {
            "id": "arquivo-desconhecido",
            "dataset_codigo": "fonte_desconhecida",
            "familia": "outros",
            "nome_arquivo": "desconhecido.csv",
            "hash_arquivo": "hash",
            "caminho_landing": str(csv_path),
            "extensao": "csv",
        }
    )

    assert resultado["status"] == "LAYOUT_NAO_MAPEADO"
    assert "allowlist" in resultado["erro"]
    assert bloqueios[0][0] == "LAYOUT_NAO_MAPEADO"


@pytest.mark.asyncio
async def test_arquivo_generico_acima_de_100mb_e_bloqueado(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_path = tmp_path / "dados.csv"
    csv_path.write_text("codigo;nome\n1;Teste\n", encoding="utf-8")
    bloqueios = []

    async def fake_bloqueio(arquivo, *, status, mensagem, linhas_lidas=None):
        bloqueios.append((status, mensagem, linhas_lidas))

    monkeypatch.setattr(loaders, "_registrar_bloqueio_generico", fake_bloqueio)

    resultado = await loaders.carregar_arquivo_tabular_generico(
        {
            "id": "arquivo-grande",
            "dataset_codigo": "ans_pda_generico",
            "familia": "desconhecido",
            "nome_arquivo": "dados.csv",
            "hash_arquivo": "hash",
            "caminho_landing": str(csv_path),
            "extensao": "csv",
            "tamanho_bytes": loaders.MAX_GENERIC_FILE_BYTES + 1,
        }
    )

    assert resultado["status"] == "LAYOUT_NAO_MAPEADO"
    assert "100 MB" in resultado["erro"]
    assert bloqueios[0][0] == "LAYOUT_NAO_MAPEADO"


@pytest.mark.asyncio
async def test_linha_generica_aborta_ao_passar_limite_de_linhas(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_path = tmp_path / "dados.csv"
    csv_path.write_text("codigo;nome\n1;Teste\n", encoding="utf-8")
    insercoes = []
    bloqueios = []

    async def fake_inserir(arquivo, batch):
        insercoes.append(batch)
        return len(batch)

    async def fake_status(arquivo_id, novo_status, erro_mensagem=None):
        return None

    async def fake_bloqueio(arquivo, *, status, mensagem, linhas_lidas=None):
        bloqueios.append((status, mensagem, linhas_lidas))

    monkeypatch.setattr(loaders, "MAX_GENERIC_ROWS", 2)
    monkeypatch.setattr(
        loaders,
        "_iter_csv",
        lambda path: iter([
            [(2, {"codigo": "1"})],
            [(3, {"codigo": "2"}), (4, {"codigo": "3"})],
        ]),
    )
    monkeypatch.setattr(loaders, "_inserir_linhas_genericas", fake_inserir)
    monkeypatch.setattr(loaders, "_marcar_status_arquivo", fake_status)
    monkeypatch.setattr(loaders, "_registrar_bloqueio_generico", fake_bloqueio)

    resultado = await loaders.carregar_arquivo_tabular_generico(
        {
            "id": "arquivo-limite",
            "dataset_codigo": "ans_pda_generico",
            "familia": "desconhecido",
            "nome_arquivo": "dados.csv",
            "hash_arquivo": "hash",
            "caminho_landing": str(csv_path),
            "extensao": "csv",
        }
    )

    assert resultado["status"] == "ERRO_VALIDACAO"
    assert resultado["linhas_carregadas"] == 1
    assert len(insercoes) == 1
    assert bloqueios == [("ERRO_VALIDACAO", resultado["erro"], 3)]


@pytest.mark.asyncio
async def test_pdf_vai_para_arquivo_generico(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = tmp_path / "arquivo.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")
    chamados = []

    async def fake_registrar(arquivo, status_parser="sem_parser"):
        chamados.append((arquivo, status_parser))
        return 1

    monkeypatch.setattr(loaders, "registrar_arquivo_generico", fake_registrar)
    resultado = await loaders.carregar_arquivo_ans(
        {
            "id": "arquivo-1",
            "dataset_codigo": "caderno_ss_generico",
            "familia": "caderno_ss",
            "url": "https://dadosabertos.ans.gov.br/arquivo.pdf",
            "nome_arquivo": "arquivo.pdf",
            "hash_arquivo": "hash",
            "caminho_landing": str(pdf_path),
            "extensao": "pdf",
            "tipo_arquivo": "pdf",
        }
    )

    assert resultado["status"] == "baixado_sem_parser"
    assert chamados[0][1] == "sem_parser"


@pytest.mark.asyncio
async def test_zip_sem_csv_vai_para_arquivo_generico(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    zip_path = tmp_path / "arquivo.zip"
    with zipfile.ZipFile(zip_path, "w") as pacote:
        pacote.writestr("relatorio.pdf", b"%PDF")
    chamados = []
    status = []

    async def fake_registrar(arquivo, status_parser="sem_parser"):
        chamados.append((arquivo, status_parser))
        return 1

    async def fake_status(arquivo_id, novo_status, erro_mensagem=None):
        status.append((arquivo_id, novo_status, erro_mensagem))

    monkeypatch.setattr(loaders, "registrar_arquivo_generico", fake_registrar)
    monkeypatch.setattr(loaders, "_marcar_status_arquivo", fake_status)

    resultado = await loaders.carregar_arquivo_ans(
        {
            "id": "arquivo-zip",
            "dataset_codigo": "caderno_ss_generico",
            "familia": "caderno_ss",
            "url": "https://dadosabertos.ans.gov.br/arquivo.zip",
            "nome_arquivo": "arquivo.zip",
            "hash_arquivo": "hash",
            "caminho_landing": str(zip_path),
            "extensao": "zip",
            "tipo_arquivo": "zip",
        }
    )

    assert resultado["status"] == "baixado_sem_parser"
    assert chamados[0][1] == "sem_parser"
    assert status == [("arquivo-zip", "baixado_sem_parser", None)]


@pytest.mark.asyncio
async def test_arquivo_ausente_na_landing_vira_erro_carga(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    status = []

    async def fake_status(arquivo_id, novo_status, erro_mensagem=None):
        status.append((arquivo_id, novo_status, erro_mensagem))

    monkeypatch.setattr(loaders, "_marcar_status_arquivo", fake_status)

    resultado = await loaders.carregar_arquivo_ans(
        {
            "id": "arquivo-ausente",
            "dataset_codigo": "sib_ativo_uf",
            "familia": "sib",
            "url": "https://dadosabertos.ans.gov.br/nao_existe.zip",
            "nome_arquivo": "nao_existe.zip",
            "hash_arquivo": "hash",
            "caminho_landing": str(tmp_path / "nao_existe.zip"),
            "extensao": "zip",
            "tipo_arquivo": "zip",
        }
    )

    assert resultado["status"] == "erro_carga"
    assert len(status) == 1
    arquivo_id, novo_status, erro_mensagem = status[0]
    assert arquivo_id == "arquivo-ausente"
    assert novo_status == "erro_carga"
    assert erro_mensagem is not None and "ausente" in erro_mensagem


@pytest.mark.asyncio
async def test_download_duplicado_vira_ignorado_duplicata(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registros = []

    class FakeStream:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def raise_for_status(self) -> None:
            return None

        async def aiter_bytes(self, chunk_size: int):
            yield b"abc"

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def stream(self, *args, **kwargs):
            return FakeStream()

    async def fake_hash_ja_baixado(hash_arquivo):
        return True

    async def fake_registrar(fonte, payload):
        registros.append(payload)

    settings = type(
        "Settings",
        (),
        {
            "ingestao_landing_path": str(tmp_path),
            "ans_http_connect_timeout_seconds": 1,
            "ans_http_read_timeout_seconds": 1,
            "ans_http_write_timeout_seconds": 1,
            "ans_http_pool_timeout_seconds": 1,
            "ans_http_user_agent": "test",
        },
    )()
    monkeypatch.setattr(downloader, "get_settings", lambda: settings)
    monkeypatch.setattr(downloader.httpx, "AsyncClient", lambda **_: FakeClient())
    monkeypatch.setattr(downloader, "_hash_ja_baixado", fake_hash_ja_baixado)
    monkeypatch.setattr(downloader, "_registrar_arquivo", fake_registrar)

    resultado = await downloader.baixar_fonte_ans(
        {
            "id": 1,
            "dataset_codigo": "cadop_operadoras_ativas",
            "familia": "cadop",
            "url": "https://dadosabertos.ans.gov.br/FTP/PDA/cadop.csv",
            "nome_arquivo": "cadop.csv",
            "tipo_arquivo": "tabular",
        }
    )

    assert resultado["status"] == "ignorado_duplicata"
    assert registros[0]["status"] == "ignorado_duplicata"
