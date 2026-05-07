from __future__ import annotations

import asyncio

from mongo_layout_service.app.core.database import get_database, get_mongo_client
from mongo_layout_service.app.repositories.layout_repository import LayoutRepository
from mongo_layout_service.app.schemas.layout import (
    ColunaLayout,
    FonteDatasetCreate,
    LayoutAliasCreate,
    LayoutCreate,
    LayoutVersaoCreate,
    StatusLayoutUpdateRequest,
)
from mongo_layout_service.app.services.layout_service import LayoutService


async def _criar_layout(
    service: LayoutService,
    repository: LayoutRepository,
    dataset_codigo: str,
) -> None:
    await repository.upsert_dataset(
        FonteDatasetCreate(
            dataset_codigo=dataset_codigo,
            nome=f"SIB {dataset_codigo}",
            descricao="Beneficiarios SIB publico ANS.",
            formato_esperado="csv",
            tabela_raw_destino=(
                "bruto_ans.sib_beneficiario_municipio"
                if dataset_codigo == "sib_municipio"
                else "bruto_ans.sib_beneficiario_operadora"
            ),
        )
    )
    layout_id = f"layout_{dataset_codigo}_csv"
    if not await repository.obter_layout(layout_id):
        await service.criar_layout(
            LayoutCreate(
                dataset_codigo=dataset_codigo,
                nome=f"SIB {dataset_codigo}",
                descricao="Layout SIB publico ANS.",
                tabela_raw_destino=(
                    "bruto_ans.sib_beneficiario_municipio"
                    if dataset_codigo == "sib_municipio"
                    else "bruto_ans.sib_beneficiario_operadora"
                ),
                formato_esperado="csv",
            )
        )
    layout_versao_id = f"{layout_id}:v1"
    if not await repository.obter_versao(layout_versao_id):
        colunas = [
            ColunaLayout(nome_canonico="competencia", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="registro_ans", tipo="string", obrigatorio=True),
            ColunaLayout(nome_canonico="beneficiario_medico", tipo="integer"),
            ColunaLayout(nome_canonico="beneficiario_odonto", tipo="integer"),
            ColunaLayout(nome_canonico="beneficiario_total", tipo="integer", obrigatorio=True),
        ]
        if dataset_codigo == "sib_municipio":
            colunas.extend(
                [
                    ColunaLayout(nome_canonico="codigo_ibge", tipo="string", obrigatorio=True),
                    ColunaLayout(nome_canonico="municipio", tipo="string"),
                    ColunaLayout(nome_canonico="uf", tipo="string"),
                ]
            )
        await service.criar_versao_layout(
            layout_id,
            LayoutVersaoCreate(versao="v1", colunas=colunas),
        )
    aliases = [
        ("Competencia", "competencia"),
        ("Registro ANS", "registro_ans"),
        ("Beneficiarios Medico", "beneficiario_medico"),
        ("Beneficiarios Odonto", "beneficiario_odonto"),
        ("Beneficiarios Total", "beneficiario_total"),
        ("Codigo IBGE", "codigo_ibge"),
        ("Municipio", "municipio"),
        ("UF", "uf"),
        # Layout real ANS SIB ativo por beneficiario (2026): agregamos estes
        # campos em memoria antes de persistir no Bronze tipado.
        ("ID_TEMPO_COMPETENCIA", "competencia"),
        ("REGISTRO_OPERADORA", "registro_ans"),
        ("CD_MUNICIPIO", "codigo_ibge"),
        ("SG_UF", "uf"),
        ("LG_BENEFICIARIO_ATIVO", "beneficiario_total"),
        ("CD_BENE_MOTV_INCLUSAO", "_ignorado_motivo_inclusao"),
        ("CD_PLANO_RPS", "_ignorado_plano_rps"),
        ("CD_PLANO_SCPA", "_ignorado_plano_scpa"),
        ("DT_CANCELAMENTO", "_ignorado_data_cancelamento"),
        ("DT_CARGA", "_ignorado_data_carga"),
        ("DT_CONTRATACAO", "_ignorado_data_contratacao"),
        ("DT_INCLUSAO", "_ignorado_data_inclusao"),
        ("DT_NASCIMENTO", "_ignorado_data_nascimento"),
        ("DT_PRIMEIRA_CONTRATACAO", "_ignorado_data_primeira_contratacao"),
        ("DT_REATIVACAO", "_ignorado_data_reativacao"),
        ("DT_ULTIMA_MUDA_CONTRATUAL", "_ignorado_data_ultima_muda_contratual"),
        ("DT_ULTIMA_REATIVACAO", "_ignorado_data_ultima_reativacao"),
        ("DT_ULTIMO_CANCELAMENTO", "_ignorado_data_ultimo_cancelamento"),
        ("ID_BENE_MOTIV_CANCELAMENTO", "_ignorado_motivo_cancelamento"),
        ("ID_BENE_TIPO_DEPENDENTE", "_ignorado_tipo_dependente"),
        ("ID_MOTIVO_MOVIMENTO", "_ignorado_motivo_movimento"),
        ("IND_PORTABILIDADE", "_ignorado_ind_portabilidade"),
        ("LG_COBERTURA_PARCIAL_TEMP", "_ignorado_cobertura_parcial_temp"),
        ("LG_ITENS_EXCLUIDO_COBERTURA", "_ignorado_itens_excluido_cobertura"),
        ("LG_RESIDE_EXTERIOR", "_ignorado_reside_exterior"),
        ("NR_PLANO_PORTABILIDADE", "_ignorado_plano_portabilidade"),
        ("TP_SEXO", "_ignorado_sexo"),
    ]
    for nome_fisico, destino_raw in aliases:
        alias = LayoutAliasCreate(nome_fisico=nome_fisico, destino_raw=destino_raw)
        alias.layout_versao_id = layout_versao_id
        await service.criar_alias(layout_id, alias)
    await service.atualizar_status_layout(
        layout_id,
        StatusLayoutUpdateRequest(
            status="ativo",
            layout_versao_id=layout_versao_id,
            motivo=f"bootstrap_fase4_{dataset_codigo}",
        ),
    )


async def bootstrap() -> None:
    repository = LayoutRepository(get_database())
    service = LayoutService(repository)
    await service.inicializar()
    await _criar_layout(service, repository, "sib_operadora")
    await _criar_layout(service, repository, "sib_municipio")
    get_mongo_client().close()


if __name__ == "__main__":
    asyncio.run(bootstrap())
