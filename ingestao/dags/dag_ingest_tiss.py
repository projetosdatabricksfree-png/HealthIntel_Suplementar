from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PYTHON_ENV = "PYTHONPATH=/workspace/.venv/lib/python3.12/site-packages:/workspace"

with DAG(
    dag_id="dag_ingest_tiss",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 1 2,5,8,11 *",
    catchup=False,
    tags=["healthintel", "tiss", "procedimento", "delta_ans_100"],
) as dag:
    registrar = BashOperator(
        task_id="registrar_layout_nao_mapeado",
        cwd="/workspace",
        bash_command=f"""{PYTHON_ENV} python -c "
import asyncio
from ingestao.app.auditoria_tentativa_carga import registrar_layout_nao_mapeado
asyncio.run(registrar_layout_nao_mapeado(
    dominio='tiss',
    dataset_codigo='tiss_procedimento_trimestral',
    arquivo_nome='TISS_procedimento_trimestral_ANS',
    assinatura='trimestre;registro_ans;grupo_procedimento;qt_procedimentos;qt_beneficiarios_distintos;valor_total',
    dag_id='dag_ingest_tiss',
    task_id='registrar_layout_nao_mapeado',
    rascunho_id='tiss_procedimento_trimestral_agregado - nao disponivel como arquivo plano no ANS FTP PDA (TISS/AMB|HOSP disponivel mas sem grupo_procedimento/qt_benef_distintos)',
))
"
""",
    )
