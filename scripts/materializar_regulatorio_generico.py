from __future__ import annotations

import argparse
import asyncio
from uuid import uuid4

from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal

LAYOUT_ID = "layout_materializado_generico_v1"
LAYOUT_VERSAO_ID = f"{LAYOUT_ID}:v1"
STATUS_PARSE = "materializado_de_ans_linha_generica"


SQL_NIP = """
delete from bruto_ans.nip_operadora_trimestral
where _layout_id = :layout_id;

insert into bruto_ans.nip_operadora_trimestral (
    trimestre,
    registro_ans,
    modalidade,
    demandas_nip,
    demandas_resolvidas,
    beneficiarios,
    taxa_intermediacao_resolvida,
    taxa_resolutividade,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id,
    _layout_id,
    _layout_versao_id,
    _hash_arquivo,
    _hash_estrutura,
    _status_parse,
    _hash_linha
)
with agregado as (
    select
        concat(
            nullif(trim(dados ->> 'ANO_DE_REFERENCIA'), ''),
            lpad(nullif(trim(dados ->> 'MES_DE_REFERENCIA'), ''), 2, '0')
        ) as competencia,
        lpad(regexp_replace(coalesce(dados ->> 'REGISTRO_OPERADORA', ''), '[^0-9]', '', 'g'), 6, '0') as registro_ans,
        upper(trim(coalesce(nullif(dados ->> 'MODALIDADE_DA_OPERADORA', ''), 'NAO_INFORMADO'))) as modalidade,
        count(*)::integer as demandas_nip,
        count(*) filter (
            where lower(coalesce(dados ->> 'RESPOSTA_BENEFICIARIO', '')) like '%resol%'
               or lower(coalesce(dados ->> 'SITUACAO_DA_DEMANDA', '')) like '%resol%'
        )::integer as demandas_resolvidas,
        min(arquivo_origem) as arquivo_origem,
        min(hash_arquivo) as hash_arquivo
    from bruto_ans.ans_linha_generica
    where dataset_codigo = 'nip_reclamacao_generico'
      and nullif(trim(dados ->> 'ANO_DE_REFERENCIA'), '') is not null
      and nullif(trim(dados ->> 'MES_DE_REFERENCIA'), '') is not null
      and regexp_replace(coalesce(dados ->> 'REGISTRO_OPERADORA', ''), '[^0-9]', '', 'g') <> ''
    group by 1, 2, 3
)
select
    competencia,
    registro_ans,
    modalidade,
    demandas_nip,
    demandas_resolvidas,
    0::bigint as beneficiarios,
    case when demandas_nip = 0 then 0 else round((demandas_resolvidas::numeric / demandas_nip) * 100, 4) end,
    case when demandas_nip = 0 then 0 else round((demandas_resolvidas::numeric / demandas_nip) * 100, 4) end,
    'ANS PDA NIP demandas dos consumidores' as fonte_publicacao,
    now(),
    arquivo_origem,
    cast(:lote_id as uuid),
    :layout_id,
    :layout_versao_id,
    hash_arquivo,
    md5('nip:' || competencia || ':' || registro_ans || ':' || modalidade),
    :status_parse,
    md5('nip:' || competencia || ':' || registro_ans || ':' || modalidade || ':' || demandas_nip::text)
from agregado;
"""


SQL_IGR = """
delete from bruto_ans.igr_operadora_trimestral
where _layout_id = :layout_id;

insert into bruto_ans.igr_operadora_trimestral (
    trimestre,
    registro_ans,
    modalidade,
    porte,
    total_reclamacoes,
    beneficiarios,
    igr,
    meta_igr,
    atingiu_meta,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id,
    _layout_id,
    _layout_versao_id,
    _hash_arquivo,
    _hash_estrutura,
    _status_parse,
    _hash_linha
)
select
    nullif(trim(dados ->> 'COMPETENCIA'), '') as trimestre,
    lpad(regexp_replace(coalesce(dados ->> 'REGISTRO_ANS', ''), '[^0-9]', '', 'g'), 6, '0') as registro_ans,
    upper(trim(coalesce(nullif(dados ->> 'COBERTURA', ''), 'NAO_INFORMADO'))) as modalidade,
    upper(trim(coalesce(nullif(dados ->> 'PORTE_OPERADORA', ''), 'NAO_INFORMADO'))) as porte,
    nullif(regexp_replace(coalesce(dados ->> 'QTD_RECLAMACOES', '0'), '[^0-9-]', '', 'g'), '')::integer as total_reclamacoes,
    nullif(regexp_replace(coalesce(dados ->> 'QTD_BENEFICIARIOS', '0'), '[^0-9-]', '', 'g'), '')::bigint as beneficiarios,
    replace(nullif(trim(dados ->> 'IGR'), ''), ',', '.')::numeric as igr,
    null::numeric as meta_igr,
    false as atingiu_meta,
    'ANS PDA IGR' as fonte_publicacao,
    now(),
    arquivo_origem,
    cast(:lote_id as uuid),
    :layout_id,
    :layout_versao_id,
    hash_arquivo,
    md5('igr:' || coalesce(dados ->> 'COMPETENCIA', '') || ':' || coalesce(dados ->> 'REGISTRO_ANS', '') || ':' || coalesce(dados ->> 'COBERTURA', '')),
    :status_parse,
    md5('igr:' || coalesce(dados ->> 'COMPETENCIA', '') || ':' || coalesce(dados ->> 'REGISTRO_ANS', '') || ':' || coalesce(dados ->> 'COBERTURA', '') || ':' || coalesce(dados ->> 'IGR', ''))
from bruto_ans.ans_linha_generica
where dataset_codigo = 'igr_generico'
  and nullif(trim(dados ->> 'COMPETENCIA'), '') is not null
  and regexp_replace(coalesce(dados ->> 'REGISTRO_ANS', ''), '[^0-9]', '', 'g') <> ''
  and nullif(trim(dados ->> 'IGR'), '') is not null;
"""


SQL_IDSS = """
delete from bruto_ans.idss
where _layout_id = :layout_id;

insert into bruto_ans.idss (
    ano_base,
    registro_ans,
    idss_total,
    idqs,
    idga,
    idsm,
    idgr,
    faixa_idss,
    fonte_publicacao,
    _carregado_em,
    _arquivo_origem,
    _lote_id,
    _layout_id,
    _layout_versao_id,
    _hash_arquivo,
    _hash_estrutura,
    _status_parse,
    _hash_linha
)
with medidas as (
    select
        linha.dados,
        linha.arquivo_origem,
        linha.hash_arquivo,
        chave.key as chave_idss,
        substring(chave.key from '^IDSS_([0-9]{4})')::integer as ano_base,
        substring(chave.key from '^IDSS_(.*)$') as sufixo,
        case
            when trim(chave.value) ~ '^[0-9]+([,.][0-9]+)?$'
                then replace(trim(chave.value), ',', '.')::numeric
            else null
        end as idss_total
    from bruto_ans.ans_linha_generica as linha
    cross join lateral jsonb_each_text(linha.dados) as chave(key, value)
    where linha.dataset_codigo = 'idss_generico'
      and chave.key ~ '^IDSS_[0-9]{4}_'
)
select
    ano_base,
    lpad(regexp_replace(coalesce(dados ->> 'REGISTRO_OPERADORA', ''), '[^0-9]', '', 'g'), 6, '0') as registro_ans,
    idss_total,
    coalesce(
        case when trim(coalesce(dados ->> ('IDQS_' || sufixo), '')) ~ '^[0-9]+([,.][0-9]+)?$'
            then replace(trim(dados ->> ('IDQS_' || sufixo)), ',', '.')::numeric
        end,
        0
    ) as idqs,
    coalesce(
        case when trim(coalesce(dados ->> ('IDGA_' || sufixo), '')) ~ '^[0-9]+([,.][0-9]+)?$'
            then replace(trim(dados ->> ('IDGA_' || sufixo)), ',', '.')::numeric
        end,
        0
    ) as idga,
    coalesce(
        case when trim(coalesce(dados ->> ('IDSM_' || sufixo), '')) ~ '^[0-9]+([,.][0-9]+)?$'
            then replace(trim(dados ->> ('IDSM_' || sufixo)), ',', '.')::numeric
        end,
        0
    ) as idsm,
    coalesce(
        case when trim(coalesce(dados ->> ('IDGR_' || sufixo), '')) ~ '^[0-9]+([,.][0-9]+)?$'
            then replace(trim(dados ->> ('IDGR_' || sufixo)), ',', '.')::numeric
        end,
        0
    ) as idgr,
    case
        when idss_total >= 0.8 then 'A'
        when idss_total >= 0.6 then 'B'
        when idss_total >= 0.4 then 'C'
        when idss_total >= 0.2 then 'D'
        else 'E'
    end as faixa_idss,
    'ANS PDA historico IDSS' as fonte_publicacao,
    now(),
    arquivo_origem,
    cast(:lote_id as uuid),
    :layout_id,
    :layout_versao_id,
    hash_arquivo,
    md5('idss:' || ano_base::text || ':' || coalesce(dados ->> 'REGISTRO_OPERADORA', '')),
    :status_parse,
    md5('idss:' || ano_base::text || ':' || coalesce(dados ->> 'REGISTRO_OPERADORA', '') || ':' || idss_total::text)
from medidas
where idss_total is not null
  and regexp_replace(coalesce(dados ->> 'REGISTRO_OPERADORA', ''), '[^0-9]', '', 'g') <> '';
"""


DATASET_SQL = {
    "nip": SQL_NIP,
    "igr": SQL_IGR,
    "idss": SQL_IDSS,
}

COUNT_SQL = {
    "nip": "select count(*) from bruto_ans.nip_operadora_trimestral where _layout_id = :layout_id",
    "igr": "select count(*) from bruto_ans.igr_operadora_trimestral where _layout_id = :layout_id",
    "idss": "select count(*) from bruto_ans.idss where _layout_id = :layout_id",
}


async def materializar(dataset: str) -> dict[str, object]:
    lote_id = str(uuid4())
    async with SessionLocal() as session:
        params = {
            "layout_id": LAYOUT_ID,
            "layout_versao_id": LAYOUT_VERSAO_ID,
            "status_parse": STATUS_PARSE,
            "lote_id": lote_id,
        }
        for statement in DATASET_SQL[dataset].split(";\n\n"):
            statement = statement.strip().removesuffix(";")
            if statement:
                await session.execute(text(statement), params)
        result = await session.execute(
            text(COUNT_SQL[dataset]),
            {"layout_id": LAYOUT_ID},
        )
        total = int(result.scalar_one())
        await session.commit()
    return {"dataset": dataset, "lote_id": lote_id, "linhas_tipadas": total}


async def executar(datasets: list[str]) -> list[dict[str, object]]:
    resultados = []
    for dataset in datasets:
        if dataset not in DATASET_SQL:
            raise ValueError(f"Dataset regulatorio nao suportado: {dataset}")
        resultados.append(await materializar(dataset))
    return resultados


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materializa NIP/IGR/IDSS de ans_linha_generica para Bronze tipado."
    )
    parser.add_argument(
        "--datasets",
        default="nip,igr,idss",
        help="Lista separada por virgula: nip,igr,idss.",
    )
    args = parser.parse_args()
    datasets = [item.strip().lower() for item in args.datasets.split(",") if item.strip()]
    for resultado in asyncio.run(executar(datasets)):
        print(
            f"[materializar_regulatorio_generico] dataset={resultado['dataset']} "
            f"linhas_tipadas={resultado['linhas_tipadas']} lote_id={resultado['lote_id']}"
        )


if __name__ == "__main__":
    main()
