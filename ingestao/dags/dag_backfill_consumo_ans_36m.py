from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"
DBT_ENV = (
    "DBT_PROFILES_DIR=/workspace/healthintel_dbt "
    "DBT_LOG_PATH=/tmp/healthintel_dbt_logs "
    "DBT_TARGET_PATH=/tmp/healthintel_dbt_target"
)


with DAG(
    dag_id="dag_backfill_consumo_ans_36m",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=15),
    },
    params={
        "competencia": "",
        "ANS_DELTA_MAX_FILES": "36",
    },
    tags=["healthintel", "consumo_ans", "backfill_36m", "sem_tiss_sem_sib"],
) as dag:
    backfill_delta_ans = BashOperator(
        task_id="backfill_delta_ans_36m_sem_tiss_sem_sib",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
            "ANS_DELTA_MAX_FILES": "{{ dag_run.conf.get('ANS_DELTA_MAX_FILES', '36') }}",
            "ANS_ANOS_CARGA_HOT": "3",
        },
        append_env=True,
        bash_command=rf"""
        {PYTHON_ENV} python -c "
import asyncio
import os

from ingestao.app.ingestao_delta_ans import (
    executar_ingestao_diops_operadora,
    executar_ingestao_glosa_operadora,
    executar_ingestao_historico_plano,
    executar_ingestao_plano_servico_opcional,
    executar_ingestao_produto_caracteristica,
    executar_ingestao_ressarcimento_beneficiario_abi,
    executar_ingestao_ressarcimento_cobranca_arrecadacao,
    executar_ingestao_ressarcimento_hc,
    executar_ingestao_ressarcimento_indice_pagamento,
    executar_ingestao_ressarcimento_sus_operadora_plano,
    executar_ingestao_regime_especial_direcao_tecnica,
    executar_ingestao_sip_mapa_assistencial,
    executar_ingestao_taxa_resolutividade_operadora,
    executar_ingestao_tuss_oficial,
    executar_ingestao_prudencial_operadora,
)

FUNCOES = [
    executar_ingestao_produto_caracteristica,
    executar_ingestao_historico_plano,
    executar_ingestao_plano_servico_opcional,
    executar_ingestao_tuss_oficial,
    executar_ingestao_diops_operadora,
    executar_ingestao_glosa_operadora,
    executar_ingestao_prudencial_operadora,
    executar_ingestao_regime_especial_direcao_tecnica,
    executar_ingestao_taxa_resolutividade_operadora,
    executar_ingestao_sip_mapa_assistencial,
    executar_ingestao_ressarcimento_beneficiario_abi,
    executar_ingestao_ressarcimento_sus_operadora_plano,
    executar_ingestao_ressarcimento_hc,
    executar_ingestao_ressarcimento_cobranca_arrecadacao,
    executar_ingestao_ressarcimento_indice_pagamento,
]

async def main():
    competencia = os.environ['HEALTHINTEL_COMPETENCIA']
    resultados = []
    for func in FUNCOES:
        resultado = await func(competencia)
        resultados.append((func.__name__, resultado))
        print(func.__name__, resultado)
    return resultados

asyncio.run(main())
"
        """,
    )

    backfill_cnes = BashOperator(
        task_id="backfill_cnes_snapshot_atual",
        cwd="/workspace",
        env={
            "HEALTHINTEL_COMPETENCIA": (
                "{{ dag_run.conf.get('competencia', '') or ds_nodash[:6] }}"
            ),
            "ANS_ANOS_CARGA_HOT": "3",
        },
        append_env=True,
        bash_command=rf"""
        {PYTHON_ENV} python -c "
import asyncio
import os
from ingestao.app.ingestao_real import executar_ingestao_cnes
print(asyncio.run(executar_ingestao_cnes(os.environ['HEALTHINTEL_COMPETENCIA'])))
"
        """,
    )

    registrar_bloqueios = BashOperator(
        task_id="registrar_decisoes_fontes_bloqueadas",
        cwd="/workspace",
        bash_command=rf"""
        {PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import (
    registrar_fonte_indisponivel,
    registrar_layout_nao_mapeado,
)

async def main():
    await registrar_fonte_indisponivel(
        dominio='beneficiario',
        dataset_codigo='portabilidade_operadora_mensal',
        fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
        dag_id='dag_backfill_consumo_ans_36m',
        task_id='registrar_decisoes_fontes_bloqueadas',
        erro_mensagem='Portabilidade mensal por operadora nao disponivel no ANS FTP PDA.',
    )
    await registrar_layout_nao_mapeado(
        dominio='financeiro',
        dataset_codigo='vda_operadora_mensal',
        arquivo_nome='Beneficiarios_operadora_e_carteira.csv',
        assinatura='CD_OPERADORA;GR_MODALIDADE;COBERTURA;VIGENCIA_PLANO;GR_CONTRATACAO;TIPO_FINANCIAMENTO;MES;ID_CMPT;NR_BENEF',
        dag_id='dag_backfill_consumo_ans_36m',
        task_id='registrar_decisoes_fontes_bloqueadas',
        rascunho_id='vda_vinculo_beneficiario_vs_vda_financeiro_divergente',
    )
    await registrar_fonte_indisponivel(
        dominio='regulatorio',
        dataset_codigo='rn623_lista_operadora_trimestral',
        fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
        dag_id='dag_backfill_consumo_ans_36m',
        task_id='registrar_decisoes_fontes_bloqueadas',
        erro_mensagem='Lista RN623 trimestral por operadora nao localizada no ANS FTP PDA.',
    )
    await registrar_layout_nao_mapeado(
        dominio='ntrp',
        dataset_codigo='ntrp_vcm_faixa_etaria',
        arquivo_nome='nota_tecnica_ntrp_vcm_faixa_etaria',
        assinatura='dataset grande; parser atual carrega arquivo inteiro em memoria',
        dag_id='dag_backfill_consumo_ans_36m',
        task_id='registrar_decisoes_fontes_bloqueadas',
        rascunho_id='ntrp_vcm_exige_parser_streaming',
    )

asyncio.run(main())
"
        """,
    )

    dbt_build_consumo = BashOperator(
        task_id="dbt_build_consumo_ans_sem_tiss_sib",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build --select tag:consumo "
            "--exclude consumo_tiss_utilizacao_operadora_mes"
        ),
    )

    [backfill_delta_ans, backfill_cnes, registrar_bloqueios] >> dbt_build_consumo
