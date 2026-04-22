import pytest

from ingestao.app.carregar_postgres import (
    carregar_cadop_bruto,
    carregar_igr_bruto,
    carregar_nip_bruto,
    carregar_rede_assistencial_bruto,
    carregar_rn623_lista_bruto,
    carregar_sib_municipio_bruto,
    carregar_sib_operadora_bruto,
    montar_registros_carga,
)


def test_montar_registros_carga_cadop_com_colunas_tecnicas() -> None:
    lote, registros = montar_registros_carga(
        "cadop",
        [
            {
                "registro_ans": "000123",
                "cnpj": "12345678000100",
                "razao_social": "OPERADORA TESTE",
                "nome_fantasia": "TESTE",
                "modalidade": "MEDICINA DE GRUPO",
                "cidade": "SAO PAULO",
                "uf": "SP",
                "competencia": 202603,
            }
        ],
        arquivo_origem="cadop_202603.csv",
        layout_id="layout_cadop_csv",
        layout_versao_id="layout_cadop_csv:v1",
        hash_arquivo="sha256:arquivo",
        hash_estrutura="sha256:estrutura",
        lote_id="lote-123",
    )

    assert lote.tabela_destino == "bruto_ans.cadop"
    assert lote.total_registros == 1
    assert registros[0]["_layout_id"] == "layout_cadop_csv"
    assert registros[0]["_arquivo_origem"] == "cadop_202603.csv"


@pytest.mark.asyncio
async def test_wrappers_delegam_para_dataset_correto(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas = []

    async def _fake_carregar(dataset_codigo: str, registros: list[dict], **kwargs) -> str:
        chamadas.append((dataset_codigo, registros, kwargs))
        return dataset_codigo

    monkeypatch.setattr(
        "ingestao.app.carregar_postgres.carregar_dataset_bruto",
        _fake_carregar,
    )

    resultado_cadop = await carregar_cadop_bruto(
        [{"registro_ans": "000123"}],
        arquivo_origem="cadop.csv",
        layout_id="layout_cadop_csv",
        layout_versao_id="layout_cadop_csv:v1",
        hash_arquivo="sha256:1",
        hash_estrutura="sha256:a",
    )
    resultado_sib_operadora = await carregar_sib_operadora_bruto(
        [{"registro_ans": "000123", "competencia": 202603}],
        arquivo_origem="sib_operadora.csv",
        layout_id="layout_sib_operadora_csv",
        layout_versao_id="layout_sib_operadora_csv:v1",
        hash_arquivo="sha256:2",
        hash_estrutura="sha256:b",
    )
    resultado_sib_municipio = await carregar_sib_municipio_bruto(
        [{"registro_ans": "000123", "competencia": 202603, "codigo_ibge": "3550308"}],
        arquivo_origem="sib_municipio.csv",
        layout_id="layout_sib_municipio_csv",
        layout_versao_id="layout_sib_municipio_csv:v1",
        hash_arquivo="sha256:3",
        hash_estrutura="sha256:c",
    )
    resultado_igr = await carregar_igr_bruto(
        [{"registro_ans": "000123", "trimestre": "2025T4", "igr": 2.4, "modalidade": "MH"}],
        arquivo_origem="igr.csv",
        layout_id="layout_igr_csv",
        layout_versao_id="layout_igr_csv:v1",
        hash_arquivo="sha256:4",
        hash_estrutura="sha256:d",
    )
    resultado_nip = await carregar_nip_bruto(
        [
            {
                "registro_ans": "000123",
                "trimestre": "2025T4",
                "modalidade": "MH",
                "demandas_nip": 10,
            }
        ],
        arquivo_origem="nip.csv",
        layout_id="layout_nip_csv",
        layout_versao_id="layout_nip_csv:v1",
        hash_arquivo="sha256:5",
        hash_estrutura="sha256:e",
    )
    resultado_rn623 = await carregar_rn623_lista_bruto(
        [
            {
                "registro_ans": "000123",
                "trimestre": "2025T4",
                "modalidade": "MH",
                "tipo_lista": "excelencia",
            }
        ],
        arquivo_origem="rn623.csv",
        layout_id="layout_rn623_lista_csv",
        layout_versao_id="layout_rn623_lista_csv:v1",
        hash_arquivo="sha256:6",
        hash_estrutura="sha256:f",
    )

    assert resultado_cadop == "cadop"
    assert resultado_sib_operadora == "sib_operadora"
    assert resultado_sib_municipio == "sib_municipio"
    assert resultado_igr == "igr"
    assert resultado_nip == "nip"
    assert resultado_rn623 == "rn623_lista"
    assert await carregar_rede_assistencial_bruto(
        [
            {
                "competencia": 202604,
                "registro_ans": "000123",
                "cd_municipio": "3550308",
                "nm_municipio": "SAO PAULO",
                "sg_uf": "SP",
                "segmento": "MEDICO",
                "tipo_prestador": "HOSPITAL",
                "qt_prestador": 10,
                "qt_especialidade_disponivel": 5,
            }
        ],
        arquivo_origem="rede.csv",
        layout_id="layout_rede_assistencial_csv",
        layout_versao_id="layout_rede_assistencial_csv:v1",
        hash_arquivo="sha256:7",
        hash_estrutura="sha256:g",
    ) == "rede_assistencial"
    assert [dataset for dataset, _, _ in chamadas] == [
        "cadop",
        "sib_operadora",
        "sib_municipio",
        "igr",
        "nip",
        "rn623_lista",
        "rede_assistencial",
    ]
