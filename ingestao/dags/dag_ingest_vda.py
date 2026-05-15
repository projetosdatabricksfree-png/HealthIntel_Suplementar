from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_vda",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 15 * *",
    catchup=False,
    is_paused_upon_creation=False,
    tags=["healthintel", "financeiro", "vda", "delta_ans_100"],
) as dag:
    registrar = BashOperator(
        task_id="registrar_layout_nao_mapeado",
        cwd="/workspace",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_layout_nao_mapeado
asyncio.run(registrar_layout_nao_mapeado(
    dominio='financeiro',
    dataset_codigo='vda_operadora_mensal',
    arquivo_nome='Beneficiarios_operadora_e_carteira.csv',
    assinatura='CD_OPERADORA;GR_MODALIDADE;COBERTURA;VIGENCIA_PLANO;GR_CONTRATACAO;TIPO_FINANCIAMENTO;MES;ID_CMPT;NR_BENEF',
    dag_id='dag_ingest_vda',
    task_id='registrar_layout_nao_mapeado',
    rascunho_id='vda_vinculo_beneficiario_vs_vda_financeiro_divergente',
))
"
""",
    )
