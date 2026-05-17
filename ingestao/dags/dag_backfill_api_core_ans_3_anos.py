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
    dag_id="dag_backfill_api_core_ans_3_anos",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=True,
    max_active_runs=1,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=15),
    },
    params={
        "competencia": "",
        "ANS_DELTA_MAX_FILES": "36",
        "executar_cnes_rede_pesado": "false",
    },
    tags=["healthintel", "core_ans", "backfill_3_anos", "sem_tiss_sem_sib_historico"],
) as dag:
    backfill_mensal_trimestral_anual = BashOperator(
        task_id="backfill_core_ans_3_anos_sem_tiss_sib_historico",
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
    executar_ingestao_prudencial_operadora,
    executar_ingestao_regime_especial_direcao_tecnica,
    executar_ingestao_sip_mapa_assistencial,
    executar_ingestao_taxa_resolutividade_operadora,
)

FUNCOES = [
    executar_ingestao_produto_caracteristica,
    executar_ingestao_historico_plano,
    executar_ingestao_diops_operadora,
    executar_ingestao_glosa_operadora,
    executar_ingestao_prudencial_operadora,
    executar_ingestao_regime_especial_direcao_tecnica,
    executar_ingestao_taxa_resolutividade_operadora,
    executar_ingestao_plano_servico_opcional,
    executar_ingestao_sip_mapa_assistencial,
]

async def main():
    competencia = os.environ['HEALTHINTEL_COMPETENCIA']
    for func in FUNCOES:
        resultado = await func(competencia)
        print(func.__name__, resultado)

asyncio.run(main())
"
        """,
    )

    registrar_bloqueios_roadmap = BashOperator(
        task_id="registrar_bloqueios_roadmap_sem_fonte_viavel",
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
        dominio='cnes',
        dataset_codigo='cnes_municipio',
        fonte_url='DataSUS CNES',
        dag_id='dag_backfill_api_core_ans_3_anos',
        task_id='registrar_bloqueios_roadmap_sem_fonte_viavel',
        erro_mensagem='CNES/rede permanecem roadmap ate carga real controlada produzir dados nao zerados.',
    )
    await registrar_fonte_indisponivel(
        dominio='regulatorio',
        dataset_codigo='rn623_lista_operadora_trimestral',
        fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
        dag_id='dag_backfill_api_core_ans_3_anos',
        task_id='registrar_bloqueios_roadmap_sem_fonte_viavel',
        erro_mensagem='Lista RN623 trimestral por operadora nao localizada no ANS FTP PDA.',
    )
    await registrar_fonte_indisponivel(
        dominio='beneficiario',
        dataset_codigo='portabilidade_operadora_mensal',
        fonte_url='https://dadosabertos.ans.gov.br/FTP/PDA/',
        dag_id='dag_backfill_api_core_ans_3_anos',
        task_id='registrar_bloqueios_roadmap_sem_fonte_viavel',
        erro_mensagem='Portabilidade mensal por operadora nao disponivel no ANS FTP PDA.',
    )
    await registrar_layout_nao_mapeado(
        dominio='rede',
        dataset_codigo='vazio_assistencial_municipio',
        arquivo_nome='rede_cnes_derivado',
        assinatura='depende de CNES/rede real nao zerado; carga pesada isolada',
        dag_id='dag_backfill_api_core_ans_3_anos',
        task_id='registrar_bloqueios_roadmap_sem_fonte_viavel',
        rascunho_id='rede_cnes_vazio_assistencial_roadmap',
    )

asyncio.run(main())
"
        """,
    )

    dbt_build_serving = BashOperator(
        task_id="dbt_build_serving_core_ans_sem_tiss_sib_historico",
        cwd="/workspace/healthintel_dbt",
        bash_command=(
            f"{DBT_ENV} dbt build --select tag:consumo "
            "--exclude consumo_tiss_utilizacao_operadora_mes "
            "consumo_beneficiarios_operadora_mes consumo_beneficiarios_municipio_mes"
        ),
    )

    auditar_cobertura = BashOperator(
        task_id="auditar_cobertura_3_anos_api_core_ans",
        cwd="/workspace",
        bash_command=(
            f"{PYTHON_ENV} python scripts/auditoria/auditar_cobertura_3_anos_api.py "
            "--permitir-parcial "
            "--json-out docs/evidencias/release_0_9/cobertura_3_anos_api.json "
            "--md-out docs/evidencias/release_0_9/cobertura_3_anos_api.md"
        ),
    )

    (
        [backfill_mensal_trimestral_anual, registrar_bloqueios_roadmap]
        >> dbt_build_serving
        >> auditar_cobertura
    )
