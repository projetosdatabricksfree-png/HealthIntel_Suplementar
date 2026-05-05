#!/bin/bash
# scripts/capacidade/relatorio_capacidade_ans.sh
# Gera relatório de capacidade distinguindo download, carga e pendências.

set -euo pipefail

NIVEL=${1:-"FULL2A_SEM_TISS"}
OUTPUT_DIR="docs/evidencias/capacidade"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RELATORIO_FILE="${OUTPUT_DIR}/capacidade_${NIVEL}_relatorio_${TIMESTAMP}.md"

mkdir -p "$OUTPUT_DIR"

arquivo_mais_recente() {
    local padrao=$1
    find "$OUTPUT_DIR" -maxdepth 1 -type f -name "$padrao" -printf "%T@ %p\n" 2>/dev/null \
        | sort -nr \
        | head -1 \
        | cut -d' ' -f2-
}

valor_disco_raiz() {
    local arquivo=$1
    awk '$NF == "/" {print $3 " usado de " $2 " (" $5 ")"; exit}' "$arquivo" 2>/dev/null || true
}

valor_landing() {
    local arquivo=$1
    awk '/--- TAMANHO LANDING ZONE ---/{getline; print $0; exit}' "$arquivo" 2>/dev/null || true
}

valor_projeto() {
    local arquivo=$1
    awk '/--- TAMANHO PROJETO ---/{getline; print $0; exit}' "$arquivo" 2>/dev/null || true
}

status_mais_recente() {
    arquivo_mais_recente "FULL2A*_status*.txt"
}

status_final() {
    local arquivo=$1
    if [ -z "$arquivo" ] || [ ! -f "$arquivo" ]; then
        echo "N/A"
        return
    fi
    grep -E "CARGA_(PARCIAL_ABORTADA_COM_SEGURANCA|CONCLUIDA_SEM_TISS_REAL|CONCLUIDA_COM_TISS_REAL|ABORTADA_POR_DISCO|ABORTADA_POR_CONCORRENCIA|CONCLUIDA_COM_PENDENTES_EXPERIMENTAIS)" "$arquivo" \
        | tail -1 \
        || echo "N/A"
}

consulta_status_arquivos() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "| N/A | N/A | N/A | N/A | docker indisponivel |"
        return
    fi

    docker compose -f infra/docker-compose.yml exec -T postgres \
        psql -U healthintel -d healthintel -Atc "
            select
                familia,
                dataset_codigo,
                status,
                count(*)::text,
                coalesce(pg_size_pretty(sum(tamanho_bytes)::bigint), '0 bytes')
            from plataforma.arquivo_fonte_ans
            group by familia, dataset_codigo, status
            order by familia, dataset_codigo, status;
        " 2>/dev/null \
        | awk -F'|' '{printf "| `%s` | `%s` | `%s` | %s | %s |\n", $1, $2, $3, $4, $5}' \
        || echo "| N/A | N/A | N/A | N/A | PostgreSQL indisponivel |"
}

ARQ_ANTES=$(arquivo_mais_recente "capacidade_${NIVEL}_antes_*.txt")
ARQ_DEPOIS=$(arquivo_mais_recente "capacidade_${NIVEL}_depois_*.txt")
ARQ_STATUS=$(status_mais_recente)
STATUS_FINAL=$(status_final "$ARQ_STATUS")

{
    echo "# Relatório de Capacidade ANS - Nível $NIVEL"
    echo ""
    echo "Gerado em: $(date -Iseconds)"
    echo ""
    echo "## Status final"
    echo ""
    echo "- Status: \`$STATUS_FINAL\`"
    echo "- Arquivo de status considerado: \`${ARQ_STATUS:-N/A}\`"
    echo "- Status possíveis: \`CARGA_PARCIAL_ABORTADA_COM_SEGURANCA\`, \`CARGA_CONCLUIDA_SEM_TISS_REAL\`, \`CARGA_CONCLUIDA_COM_TISS_REAL\`, \`CARGA_ABORTADA_POR_DISCO\`, \`CARGA_ABORTADA_POR_CONCORRENCIA\`."
    echo ""
    echo "## 1. Comparativo de Recursos"
    echo ""
    echo "| Recurso | Antes | Depois | Observação |"
    echo "| :--- | :--- | :--- | :--- |"

    if [ -n "$ARQ_ANTES" ] && [ -n "$ARQ_DEPOIS" ]; then
        echo "| Disco raiz | $(valor_disco_raiz "$ARQ_ANTES") | $(valor_disco_raiz "$ARQ_DEPOIS") | Delta deve ser avaliado, não apenas valor absoluto. |"
        echo "| Tamanho do projeto | $(valor_projeto "$ARQ_ANTES") | $(valor_projeto "$ARQ_DEPOIS") | Inclui artefatos locais. |"
        echo "| Landing zone | $(valor_landing "$ARQ_ANTES") | $(valor_landing "$ARQ_DEPOIS") | Para FULL2A_SEM_TISS, usar landing isolada. |"
    else
        echo "| Snapshots | \`${ARQ_ANTES:-N/A}\` | \`${ARQ_DEPOIS:-N/A}\` | Arquivos antes/depois não encontrados para este nível. |"
    fi

    echo ""
    echo "## 2. Volumetria por Status no Catálogo"
    echo ""
    echo "| Família | Dataset | Status | Arquivos | Volume |"
    echo "| :--- | :--- | :--- | ---: | ---: |"
    consulta_status_arquivos

    echo ""
    echo "## 3. Interpretação Operacional"
    echo ""
    echo "- \`baixado\`: arquivo presente na landing, ainda elegível para carga."
    echo "- \`carregado\`: arquivo carregado no PostgreSQL."
    echo "- \`baixado_sem_parser\`: arquivo preservado, mas sem parser/load real para Bronze dedicada."
    echo "- \`erro_carga\` ou \`erro_download\`: falha operacional que exige investigação."
    echo "- \`ignorado_duplicata\`: arquivo já conhecido pelo hash e não recarregado."
    echo ""
    echo "## 4. Exclusões intencionais da carga"
    echo ""
    echo "- \`tiss_ambulatorial\`"
    echo "  - status: \`PENDENTE_PARSER_LOAD_REAL\`"
    echo "  - motivo: discovery real classifica TISS como \`tiss_ambulatorial\`, enquanto o contrato de carga/dbt existente atende \`tiss_procedimento\` e \`bruto_ans.tiss_procedimento_trimestral\`."
    echo "  - evidência: execução parcial anterior baixou 4155 arquivos TISS e carregou 0 no PostgreSQL."
    echo "  - decisão: fora da FULL2A padrão até parser/load real."
    echo ""
    echo "## 5. Recomendações de VPS"
    echo ""
    echo "- **Mínimo**: 8 vCPU, 16GB RAM, 600GB SSD."
    echo "- **Recomendado (HML)**: 16 vCPU, 32GB RAM, 1TB SSD."
    echo "- Para nova medição sem TISS real, usar \`FULL2A_LANDING_PATH=./data/landing_full2a_sem_tiss\` ou outro path isolado."
} > "$RELATORIO_FILE"

cat "$RELATORIO_FILE"
