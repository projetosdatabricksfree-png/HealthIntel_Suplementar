"""Sprint 43 — orquestrador de inventário real das tabelas servidoras.

Lê pg_stat_user_tables, faz count(*) real em cada tabela com n_live_tup=0 e classifica
por domínio + prioridade (P0/P1/P2/P3). Saída CSV em docs/evidencias/sprint43/.

Execução:
    python scripts/auditoria/sprint43_count_real_tabelas_vazias.py \
        --saida docs/evidencias/sprint43/inventario_92_tabelas_vazias_inicio.csv

Read-only: apenas SELECT. Não modifica nada.
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DOCKER_COMPOSE = "/opt/healthintel/infra/docker-compose.yml"
PG_USER = "healthintel"
PG_DB = "healthintel"


@dataclass
class TabelaVazia:
    schema: str
    tabela: str
    n_live_tup: int
    row_count_real: int
    tamanho_bytes: int
    dominio: str
    prioridade: str
    camada: str
    fonte_esperada: str
    dag_responsavel: str
    dbt_model: str
    status_inicio: str


# Classificação por padrão de nome → (domínio, prioridade, fonte, dag, dbt_model)
# A prioridade segue o plano Sprint 43:
#   P0 = TISS 4 recortes + SIP
#   P1 = CNES, financeiro, regulatório, RPC, NTRP, glosa/VDA, ressarcimento, portabilidade, beneficiário
#   P2 = premium, marts derivadas estruturais
#   P3 = fontes inacessíveis / sem chave
CLASSIFICACAO = [
    # P0
    ("tiss", "P0", "tiss", "fonte ANS TISS subfamílias", "dag_ingest_tiss", "stg/api/consumo_tiss_*"),
    ("sip", "P0", "sip", "fonte ANS SIP delta", "dag_ingest_sip_delta", "stg_sip_*"),
    # P1
    ("cnes", "P1", "cnes", "fonte CNES DataSUS", "dag_ingest_cnes", "stg_cnes_*"),
    ("rede", "P1", "rede", "fonte ANS rede assistencial", "dag_ingest_rede_assistencial", "stg_rede_*"),
    ("diops", "P1", "financeiro", "DIOPS ANS", "dag_ingest_diops", "stg_diops_*"),
    ("fip", "P1", "financeiro", "FIP ANS", "dag_ingest_fip", "stg_fip_*"),
    ("financeiro", "P1", "financeiro", "DIOPS + FIP", "dag_ingest_diops/fip", "stg_financeiro_*"),
    ("nip", "P1", "regulatorio", "NIP ANS", "dag_ingest_nip", "stg_nip_*"),
    ("idss", "P1", "regulatorio", "IDSS ANS anual", "dag_anual_idss", "stg_idss_*"),
    ("rpc", "P1", "regulatorio", "RPC ANS", "dag_ingest_rpc?", "stg_rpc_*"),
    ("rn623", "P1", "regulatorio", "RN623 ANS trimestral", "dag_ingest_rn623", "stg_rn623_*"),
    ("regulatorio", "P1", "regulatorio", "agregado regulatório", "varias", "stg_regulatorio_*"),
    ("monitoramento_regulatorio", "P1", "regulatorio", "agregado regulatório", "varias", "fat_monitoramento_*"),
    ("reclamacao", "P1", "regulatorio", "reclamação ANS", "dag_ingest_nip?", "fat_reclamacao_*"),
    ("score_regulatorio", "P1", "regulatorio", "score derivado", "dbt", "fat_score_regulatorio_*"),
    ("ntrp", "P1", "ntrp", "NTRP ANS", "dag_ingest_precificacao_ntrp", "stg_ntrp_*"),
    ("painel_precificacao", "P1", "ntrp", "painel precificação", "dag_ingest_precificacao_ntrp", "stg_painel_*"),
    ("faixa_preco", "P1", "ntrp", "faixa preço", "dag_ingest_precificacao_ntrp", "stg_faixa_preco_*"),
    ("reajuste", "P1", "ntrp", "reajuste agrupamento", "dag_ingest_precificacao_ntrp", "stg_reajuste_*"),
    ("precificacao", "P1", "ntrp", "precificação plano", "dag_ingest_precificacao_ntrp", "consumo_precificacao_*"),
    ("glosa", "P1", "glosa", "glosa ANS", "dag_ingest_glosa", "stg_glosa_*"),
    ("vda", "P1", "vda", "VDA ANS", "dag_ingest_vda", "stg_vda_*"),
    ("ressarcimento", "P1", "ressarcimento", "ressarcimento SUS", "dag_ingest_ressarcimento_sus", "stg_ressarcimento_*"),
    ("portabilidade", "P1", "portabilidade", "portabilidade ANS", "dag_ingest_portabilidade", "stg_portabilidade_*"),
    ("beneficiario", "P1", "beneficiario", "SIB beneficiários", "dag_ingest_sib", "stg_sib_*"),
    ("sib", "P1", "beneficiario", "SIB beneficiários", "dag_ingest_sib", "stg_sib_*"),
    ("cobertura", "P1", "beneficiario", "SIB cobertura", "dag_ingest_beneficiarios_cobertura", "stg_cobertura_*"),
    # P2 / P3 (regulatórios complementares)
    ("premium", "P2", "premium", "validações premium", "dbt+seed", "api_premium_*"),
    ("acreditad", "P2", "rede", "rede acreditada", "varias", "fat_acreditacao_*"),
    ("garantia_atendimento", "P2", "regulatorio", "garantia atendimento ANS", "dag?", "stg_garantia_*"),
    ("regime_especial", "P2", "regulatorio", "regime especial ANS", "dag_ingest_regime_especial", "stg_regime_*"),
    ("operadora_cancelada", "P2", "cadop", "CADOP histórico", "dag_ingest_cadop", "stg_cadop_*"),
    ("operadora_acreditada", "P2", "rede", "acreditação ONA", "dag?", "stg_acreditacao_*"),
    ("prestador_acreditado", "P2", "rede", "acreditação prestador", "dag?", "stg_prestador_acred_*"),
    ("produto_prestador_hospitalar", "P2", "rede", "produto-prestador hospitalar", "dag?", "stg_produto_prestador_*"),
    ("programa_qualificacao", "P2", "regulatorio", "PQI ANS", "dag?", "stg_pqi_*"),
    ("promoprev", "P2", "regulatorio", "PROMOPREV", "dag?", "stg_promoprev_*"),
    ("pfa", "P2", "regulatorio", "PFA", "dag?", "stg_pfa_*"),
    ("peona", "P2", "regulatorio", "PEONA SUS", "dag?", "stg_peona_*"),
    ("iap", "P2", "regulatorio", "IAP ANS", "dag?", "stg_iap_*"),
    ("alteracao_rede_hospitalar", "P2", "rede", "alteração rede hospitalar", "dag?", "stg_alteracao_rede_*"),
    ("plano_servico_opcional", "P2", "produto", "plano serviço opcional", "dag?", "stg_pso_*"),
    ("taxa_cobertura", "P2", "produto", "taxa cobertura plano", "dbt", "fat_taxa_cobertura_*"),
    ("valor_comercial_medio", "P2", "ntrp", "valor comercial médio município", "dbt", "fat_vcm_*"),
    ("vazio_assistencial", "P2", "rede", "vazio assistencial", "dag?", "stg_vazio_*"),
    ("tipo_contratacao", "P2", "produto", "dim tipo contratação", "dbt seed", "dim_tipo_*"),
    ("densidade_rede", "P2", "rede", "densidade rede operadora", "dbt", "fat_densidade_*"),
]


def classificar(schema: str, tabela: str) -> tuple[str, str, str, str, str]:
    nome = tabela.lower()
    for chave, prio, dom, fonte, dag, dbt in CLASSIFICACAO:
        if chave in nome:
            return dom, prio, fonte, dag, dbt
    return "outros", "P3", "fonte_desconhecida", "n/a", "n/a"


def camada(schema: str) -> str:
    return {"api_ans": "api", "consumo_ans": "consumo", "nucleo_ans": "nucleo"}.get(schema, "desconhecida")


def psql(sql: str) -> str:
    """Executa SQL via docker compose exec -T postgres. Retorna stdout cru."""
    cmd = [
        "docker", "compose", "-f", DOCKER_COMPOSE,
        "exec", "-T", "postgres",
        "psql", "-U", PG_USER, "-d", PG_DB,
        "-A", "-F|", "-t", "-q", "-c", sql,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise RuntimeError(f"psql falhou: {res.stderr}")
    return res.stdout


def listar_tabelas() -> list[tuple[str, str, int, int]]:
    sql = (
        "select schemaname, relname, n_live_tup, "
        "pg_total_relation_size(format('%I.%I', schemaname, relname)) "
        "from pg_stat_user_tables "
        "where schemaname in ('api_ans','consumo_ans','nucleo_ans') "
        "order by schemaname, relname;"
    )
    out = psql(sql)
    tabelas = []
    for linha in out.strip().splitlines():
        partes = linha.split("|")
        if len(partes) != 4:
            continue
        schema, tabela, n_live, tamanho = partes
        tabelas.append((schema.strip(), tabela.strip(), int(n_live or 0), int(tamanho or 0)))
    return tabelas


def count_real(schema: str, tabela: str) -> int:
    """count(*) real. Tem custo, mas necessário porque n_live_tup é estimativa."""
    sql = f'select count(*) from "{schema}"."{tabela}";'
    out = psql(sql).strip()
    return int(out) if out.isdigit() else -1


def status_inicial(row_count: int) -> str:
    if row_count > 0:
        return "POPULADA"
    return "ZERADA"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--saida",
        default="docs/evidencias/sprint43/inventario_92_tabelas_vazias_inicio.csv",
        help="Caminho CSV de saída (relativo ao repo).",
    )
    parser.add_argument(
        "--apenas-vazias",
        action="store_true",
        help="Lista só tabelas com n_live_tup=0 (default: lista todas).",
    )
    args = parser.parse_args()

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)

    print(f"[sprint43] consultando pg_stat_user_tables nos 3 schemas...", file=sys.stderr)
    tabelas = listar_tabelas()
    print(f"[sprint43] total de tabelas: {len(tabelas)}", file=sys.stderr)

    candidatas = [t for t in tabelas if not args.apenas_vazias or t[2] == 0]
    print(f"[sprint43] candidatas para count real: {len(candidatas)}", file=sys.stderr)

    registros: list[TabelaVazia] = []
    for i, (schema, tabela, n_live, tamanho) in enumerate(candidatas, 1):
        try:
            rc = count_real(schema, tabela)
        except Exception as e:
            print(f"[sprint43][erro] {schema}.{tabela}: {e}", file=sys.stderr)
            rc = -1
        dom, prio, fonte, dag, dbt = classificar(schema, tabela)
        registros.append(TabelaVazia(
            schema=schema,
            tabela=tabela,
            n_live_tup=n_live,
            row_count_real=rc,
            tamanho_bytes=tamanho,
            dominio=dom,
            prioridade=prio,
            camada=camada(schema),
            fonte_esperada=fonte,
            dag_responsavel=dag,
            dbt_model=dbt,
            status_inicio=status_inicial(rc),
        ))
        if i % 50 == 0:
            print(f"[sprint43] {i}/{len(candidatas)}", file=sys.stderr)

    with open(saida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "schema", "tabela", "n_live_tup", "row_count_real", "tamanho_bytes",
            "dominio", "prioridade", "camada", "fonte_esperada",
            "dag_responsavel", "dbt_model", "status_inicio",
        ])
        for r in registros:
            w.writerow([
                r.schema, r.tabela, r.n_live_tup, r.row_count_real, r.tamanho_bytes,
                r.dominio, r.prioridade, r.camada, r.fonte_esperada,
                r.dag_responsavel, r.dbt_model, r.status_inicio,
            ])

    # Resumo no stderr para auditoria
    by_prio: dict[str, int] = {}
    by_dom: dict[str, int] = {}
    vazias = [r for r in registros if r.row_count_real == 0]
    for r in vazias:
        by_prio[r.prioridade] = by_prio.get(r.prioridade, 0) + 1
        by_dom[r.dominio] = by_dom.get(r.dominio, 0) + 1

    print(f"\n[sprint43] inventário salvo em: {saida}", file=sys.stderr)
    print(f"[sprint43] total inspecionado: {len(registros)}", file=sys.stderr)
    print(f"[sprint43] zeradas (count=0): {len(vazias)}", file=sys.stderr)
    print(f"[sprint43] populadas: {len(registros) - len(vazias)}", file=sys.stderr)
    print(f"[sprint43] zeradas por prioridade: {dict(sorted(by_prio.items()))}", file=sys.stderr)
    print(f"[sprint43] zeradas por domínio: {dict(sorted(by_dom.items(), key=lambda x: -x[1]))}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
