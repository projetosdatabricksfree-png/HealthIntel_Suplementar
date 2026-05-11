#!/usr/bin/env bash
# Sprint 42 — Validação pós-carga real ANS na VPS
# Uso: bash scripts/validar_pos_carga_real_sprint_42.sh
# Pré-requisito: chave SSH em ~/.ssh/healthintel_vps com acesso à VPS
set -euo pipefail

VPS_HOST="5.189.160.27"
SSH_USER="root"
SSH_KEY="${HOME}/.ssh/healthintel_vps"
VPS_PROJECT="/opt/healthintel"
COMPOSE_FILE="infra/docker-compose.yml"
PSQL_CMD="docker compose -f ${COMPOSE_FILE} exec -T postgres psql -U healthintel -d healthintel"
AIRFLOW_CMD="docker compose -f ${COMPOSE_FILE} exec -T airflow-scheduler airflow"
EVIDENCE_DIR="docs/evidencias/ans_100_delta"
SQL_FILE="scripts/smoke_delta_ans_100_sql.sql"
TS=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "desconhecido")

ssh_exec() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
        -o BatchMode=yes -o ConnectTimeout=15 \
        "${SSH_USER}@${VPS_HOST}" \
        "cd ${VPS_PROJECT} && $*"
}

psql_exec() {
    local query="$1"
    ssh_exec "${PSQL_CMD} -c \"${query}\""
}

header() {
    local label="$1"
    local file="$2"
    {
        echo "# ${label}"
        echo ""
        echo "**Timestamp:** ${TS}  "
        echo "**Commit:** ${COMMIT}  "
        echo ""
    } > "$file"
}

echo "=== Sprint 42 — Validação Pós-Carga Real ANS ==="
echo "Timestamp : ${TS}"
echo "Commit    : ${COMMIT}"
echo "VPS       : ${VPS_HOST}"
echo ""

# ----------------------------------------------------------------
# H1 — Ambiente VPS
# ----------------------------------------------------------------
echo "[1/8] Validando ambiente VPS..."
header "Evidência — Ambiente VPS Pós-Carga Real" "${EVIDENCE_DIR}/pos_carga_real_ambiente.md"

{
    echo "## docker compose ps"
    echo '```'
    ssh_exec "docker compose -f ${COMPOSE_FILE} ps" 2>&1 || echo "ERRO: docker compose ps falhou"
    echo '```'
    echo ""

    echo "## /saude (interno VPS)"
    echo '```'
    ssh_exec "curl -si http://localhost:8080/saude" 2>&1 || echo "ERRO: curl /saude falhou"
    echo '```'
    echo ""

    echo "## /ready (interno VPS)"
    echo '```'
    ssh_exec "curl -si http://localhost:8080/ready" 2>&1 || echo "AVISO: /ready pode requerer auth"
    echo '```'
    echo ""

    echo "## Frontend (externo)"
    echo '```'
    curl -si --max-time 15 https://app.healthintel.com.br 2>&1 | head -5 || echo "ERRO: frontend"
    echo '```'
} >> "${EVIDENCE_DIR}/pos_carga_real_ambiente.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_ambiente.md"

# ----------------------------------------------------------------
# H2 — DAGs delta ANS
# ----------------------------------------------------------------
echo "[2/8] Monitorando DAGs delta ANS..."
header "Evidência — DAGs Delta ANS" "${EVIDENCE_DIR}/pos_carga_real_dags.md"

DAGS_DELTA=(
    dag_ingest_produto_plano
    dag_ingest_tuss_oficial
    dag_ingest_tiss_subfamilias
    dag_ingest_sip_delta
    dag_ingest_ressarcimento_sus
    dag_ingest_precificacao_ntrp
    dag_ingest_rede_prestadores
    dag_ingest_regulatorios_complementares
    dag_ingest_beneficiarios_cobertura
)

{
    echo "## Lista DAGs delta"
    echo '```'
    ssh_exec "${AIRFLOW_CMD} dags list | grep -E 'produto|tuss|tiss|sip|ressarcimento|precificacao|rede|regulatorios|beneficiarios|delta' || true" 2>&1
    echo '```'
    echo ""

    for dag in "${DAGS_DELTA[@]}"; do
        echo "## Últimas execuções: ${dag}"
        echo '```'
        ssh_exec "${AIRFLOW_CMD} dags list-runs --dag-id ${dag}" 2>&1 \
            || echo "AVISO: falha ao consultar ${dag}"
        echo '```'
        echo ""
    done
} >> "${EVIDENCE_DIR}/pos_carga_real_dags.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_dags.md"

# ----------------------------------------------------------------
# H3 — plataforma.arquivo_fonte_ans
# ----------------------------------------------------------------
echo "[3/8] Verificando plataforma.arquivo_fonte_ans..."
header "Evidência — Status plataforma.arquivo_fonte_ans" "${EVIDENCE_DIR}/pos_carga_real_status_arquivos.md"

run_sql_section() {
    local label="$1"
    local query="$2"
    local file="$3"
    {
        echo "## ${label}"
        echo '```'
        psql_exec "${query}" 2>&1 || echo "ERRO: query falhou"
        echo '```'
        echo ""
    } >> "$file"
}

run_sql_section "Status por família" \
    "select familia, status, count(*) as total_arquivos from plataforma.arquivo_fonte_ans group by familia, status order by familia, status;" \
    "${EVIDENCE_DIR}/pos_carga_real_status_arquivos.md"

run_sql_section "Status geral" \
    "select status, count(*) as total_arquivos from plataforma.arquivo_fonte_ans group by status order by status;" \
    "${EVIDENCE_DIR}/pos_carga_real_status_arquivos.md"

run_sql_section "Famílias delta ANS" \
    "select familia, count(*) filter (where status in ('carregado','bronze_generico','arquivado_r2')) as sucesso, count(*) filter (where status like 'erro%') as erro, count(*) filter (where status in ('baixado_sem_parser','pendente')) as pendente, count(*) as total from plataforma.arquivo_fonte_ans where familia in ('produtos_planos','tuss','tiss','sip','ressarcimento_sus','precificacao_ntrp','rede_prestadores','regulatorios_complementares','beneficiarios_cobertura') group by familia order by familia;" \
    "${EVIDENCE_DIR}/pos_carga_real_status_arquivos.md"

run_sql_section "Todas as famílias distintas" \
    "select distinct familia from plataforma.arquivo_fonte_ans order by familia;" \
    "${EVIDENCE_DIR}/pos_carga_real_status_arquivos.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_status_arquivos.md"

# ----------------------------------------------------------------
# H4 — contagens api_ans
# ----------------------------------------------------------------
echo "[4/8] Contando tabelas api_ans..."
header "Evidência — Contagens api_ans" "${EVIDENCE_DIR}/pos_carga_real_api_ans_counts.md"

run_sql_section "Contagens api_ans (20 tabelas)" \
    "select 'api_produto_plano' as tabela, count(*) as linhas from api_ans.api_produto_plano union all select 'api_historico_plano', count(*) from api_ans.api_historico_plano union all select 'api_plano_servico_opcional', count(*) from api_ans.api_plano_servico_opcional union all select 'api_quadro_auxiliar_corresponsabilidade', count(*) from api_ans.api_quadro_auxiliar_corresponsabilidade union all select 'api_tuss_procedimento_vigente', count(*) from api_ans.api_tuss_procedimento_vigente union all select 'api_tiss_ambulatorial_operadora_mes', count(*) from api_ans.api_tiss_ambulatorial_operadora_mes union all select 'api_tiss_hospitalar_operadora_mes', count(*) from api_ans.api_tiss_hospitalar_operadora_mes union all select 'api_tiss_plano_mes', count(*) from api_ans.api_tiss_plano_mes union all select 'api_sip_assistencial_operadora', count(*) from api_ans.api_sip_assistencial_operadora union all select 'api_ressarcimento_beneficiario_abi', count(*) from api_ans.api_ressarcimento_beneficiario_abi union all select 'api_ressarcimento_sus_operadora_plano', count(*) from api_ans.api_ressarcimento_sus_operadora_plano union all select 'api_ressarcimento_hc', count(*) from api_ans.api_ressarcimento_hc union all select 'api_ressarcimento_cobranca_arrecadacao', count(*) from api_ans.api_ressarcimento_cobranca_arrecadacao union all select 'api_ressarcimento_indice_pagamento', count(*) from api_ans.api_ressarcimento_indice_pagamento union all select 'api_painel_precificacao', count(*) from api_ans.api_painel_precificacao union all select 'api_valor_comercial_medio_municipio', count(*) from api_ans.api_valor_comercial_medio_municipio union all select 'api_prestador_acreditado', count(*) from api_ans.api_prestador_acreditado union all select 'api_alteracao_rede_hospitalar', count(*) from api_ans.api_alteracao_rede_hospitalar union all select 'api_penalidade_operadora', count(*) from api_ans.api_penalidade_operadora union all select 'api_rpc_operadora_mes', count(*) from api_ans.api_rpc_operadora_mes order by tabela;" \
    "${EVIDENCE_DIR}/pos_carga_real_api_ans_counts.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_api_ans_counts.md"

# ----------------------------------------------------------------
# H5 — contagens consumo_ans
# ----------------------------------------------------------------
echo "[5/8] Contando tabelas consumo_ans..."
header "Evidência — Contagens consumo_ans" "${EVIDENCE_DIR}/pos_carga_real_consumo_ans_counts.md"

run_sql_section "Contagens consumo_ans (11 tabelas)" \
    "select 'consumo_produto_plano' as tabela, count(*) as linhas from consumo_ans.consumo_produto_plano union all select 'consumo_historico_plano', count(*) from consumo_ans.consumo_historico_plano union all select 'consumo_plano_servico_opcional', count(*) from consumo_ans.consumo_plano_servico_opcional union all select 'consumo_tuss_procedimento_vigente', count(*) from consumo_ans.consumo_tuss_procedimento_vigente union all select 'consumo_tiss_utilizacao_operadora_mes', count(*) from consumo_ans.consumo_tiss_utilizacao_operadora_mes union all select 'consumo_sip_assistencial_operadora', count(*) from consumo_ans.consumo_sip_assistencial_operadora union all select 'consumo_ressarcimento_sus_operadora', count(*) from consumo_ans.consumo_ressarcimento_sus_operadora union all select 'consumo_precificacao_plano', count(*) from consumo_ans.consumo_precificacao_plano union all select 'consumo_rede_acreditacao', count(*) from consumo_ans.consumo_rede_acreditacao union all select 'consumo_regulatorio_complementar_operadora', count(*) from consumo_ans.consumo_regulatorio_complementar_operadora union all select 'consumo_beneficiarios_cobertura_municipio', count(*) from consumo_ans.consumo_beneficiarios_cobertura_municipio order by tabela;" \
    "${EVIDENCE_DIR}/pos_carga_real_consumo_ans_counts.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_consumo_ans_counts.md"

# ----------------------------------------------------------------
# H6 — TISS / RPC 24 meses
# ----------------------------------------------------------------
echo "[6/8] Validando TISS/RPC janela 24 meses..."
header "Evidência — TISS/RPC Janela 24 Meses" "${EVIDENCE_DIR}/pos_carga_real_tiss_rpc_24_meses.md"

run_sql_section "TISS e RPC api_ans" \
    "select 'api_tiss_ambulatorial_operadora_mes' as tabela, min(competencia) as competencia_min, max(competencia) as competencia_max, count(distinct competencia) as qtd_competencias, count(*) as linhas from api_ans.api_tiss_ambulatorial_operadora_mes union all select 'api_tiss_hospitalar_operadora_mes', min(competencia), max(competencia), count(distinct competencia), count(*) from api_ans.api_tiss_hospitalar_operadora_mes union all select 'api_tiss_plano_mes', min(competencia), max(competencia), count(distinct competencia), count(*) from api_ans.api_tiss_plano_mes union all select 'api_rpc_operadora_mes', min(competencia), max(competencia), count(distinct competencia), count(*) from api_ans.api_rpc_operadora_mes;" \
    "${EVIDENCE_DIR}/pos_carga_real_tiss_rpc_24_meses.md"

run_sql_section "TISS consumo_ans" \
    "select 'consumo_tiss_utilizacao_operadora_mes' as tabela, min(competencia) as competencia_min, max(competencia) as competencia_max, count(distinct competencia) as qtd_competencias, count(*) as linhas from consumo_ans.consumo_tiss_utilizacao_operadora_mes;" \
    "${EVIDENCE_DIR}/pos_carga_real_tiss_rpc_24_meses.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_tiss_rpc_24_meses.md"

# ----------------------------------------------------------------
# H7 — TUSS oficial
# ----------------------------------------------------------------
echo "[7/8] Validando TUSS oficial..."
header "Evidência — TUSS Oficial" "${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

run_sql_section "Contagem TUSS vigente" \
    "select count(*) as total_tuss_vigente from api_ans.api_tuss_procedimento_vigente;" \
    "${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

run_sql_section "Duplicidade por codigo_tuss + versao_tuss" \
    "select codigo_tuss, versao_tuss, count(*) as total from api_ans.api_tuss_procedimento_vigente group by codigo_tuss, versao_tuss having count(*) > 1 order by total desc limit 20;" \
    "${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

run_sql_section "Amostra por código" \
    "select codigo_tuss, descricao, versao_tuss, vigencia_inicio, vigencia_fim, is_tuss_vigente from api_ans.api_tuss_procedimento_vigente where codigo_tuss is not null limit 20;" \
    "${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

run_sql_section "Busca por descrição (consulta)" \
    "select codigo_tuss, descricao, versao_tuss, is_tuss_vigente from api_ans.api_tuss_procedimento_vigente where lower(descricao) like '%consulta%' limit 20;" \
    "${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

run_sql_section "Contagem TUSS consumo" \
    "select count(*) as total_tuss_consumo from consumo_ans.consumo_tuss_procedimento_vigente;" \
    "${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_tuss_oficial_busca.md"

# ----------------------------------------------------------------
# H8 — Grants finais
# ----------------------------------------------------------------
echo "[8/8] Validando grants..."
header "Evidência — Grants Finais" "${EVIDENCE_DIR}/pos_carga_real_grants.md"

run_sql_section "Grants em camadas comerciais" \
    "select grantee, table_schema, count(*) as total_privilegios from information_schema.role_table_grants where table_schema in ('api_ans','consumo_ans','consumo_premium_ans') group by grantee, table_schema order by grantee, table_schema;" \
    "${EVIDENCE_DIR}/pos_carga_real_grants.md"

run_sql_section "Grants indevidos em camadas internas" \
    "select grantee, table_schema, count(*) as total_privilegios from information_schema.role_table_grants where table_schema in ('bruto_ans','stg_ans','int_ans','nucleo_ans') and grantee in ('healthintel_cliente_reader','healthintel_premium_reader') group by grantee, table_schema order by grantee, table_schema;" \
    "${EVIDENCE_DIR}/pos_carga_real_grants.md"

echo "    -> ${EVIDENCE_DIR}/pos_carga_real_grants.md"

echo ""
echo "=== Validação concluída ==="
echo "Evidências salvas em: ${EVIDENCE_DIR}/"
echo "Próximo passo: criar pos_carga_real_relatorio_final.md com a decisão final."
