from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

MVP_SOURCES = " ".join(
    [
        "source:bruto_ans.cadop",
        "source:bruto_ans.sib_beneficiario_operadora",
        "source:bruto_ans.sib_beneficiario_municipio",
        "source:bruto_ans.igr_operadora_trimestral",
        "source:bruto_ans.nip_operadora_trimestral",
        "source:bruto_ans.idss",
        "source:bruto_ans.diops_operadora_trimestral",
        "source:bruto_ans.glosa_operadora_mensal",
        "source:bruto_ans.regime_especial_operadora_trimestral",
        "source:bruto_ans.prudencial_operadora_trimestral",
        "source:bruto_ans.taxa_resolutividade_operadora_trimestral",
        "source:bruto_ans.produto_caracteristica",
        "source:bruto_ans.produto_tabela_auxiliar",
        "source:bruto_ans.historico_plano",
        "source:bruto_ans.tuss_terminologia_oficial",
        "source:bruto_ans.sip_mapa_assistencial",
    ]
)

with DAG(
    dag_id="dag_dbt_freshness",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    tags=["healthintel", "dbt"],
) as dag:
    inicio = EmptyOperator(task_id="inicio")

    executar_freshness = BashOperator(
        task_id="executar_freshness",
        bash_command=(
            "cd /workspace/healthintel_dbt"
            f" && /home/airflow/.local/bin/dbt source freshness --select {MVP_SOURCES}"
        ),
    )

    fim = EmptyOperator(task_id="fim")

    inicio >> executar_freshness >> fim
