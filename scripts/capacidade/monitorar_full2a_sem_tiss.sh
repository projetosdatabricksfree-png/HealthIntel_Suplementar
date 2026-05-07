#!/bin/bash
# scripts/capacidade/monitorar_full2a_sem_tiss.sh

set -uo pipefail

INTERVALO_SEGUNDOS=300
ONCE=false
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="docs/evidencias/capacidade/FULL2A_SEM_TISS_monitor_${TIMESTAMP}.log"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --once) ONCE=true; shift ;;
        --intervalo) INTERVALO_SEGUNDOS="$2"; shift 2 ;;
        --log) LOG_FILE="$2"; shift 2 ;;
        *) echo "Parâmetro desconhecido: $1"; exit 1 ;;
    esac
done

mkdir -p "$(dirname "$LOG_FILE")"

executar_coleta() {
    local ts
    ts=$(date "+%Y-%m-%d %H:%M:%S")
    
    echo "=================================================================" >> "$LOG_FILE"
    echo "COLETA - $ts" >> "$LOG_FILE"
    echo "=================================================================" >> "$LOG_FILE"
    
    echo "--- USO DE DISCO ---" >> "$LOG_FILE"
    df -h . >> "$LOG_FILE" 2>&1
    
    local disk_usage
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    echo "" >> "$LOG_FILE"
    echo "--- MEMÓRIA LIVRE ---" >> "$LOG_FILE"
    free -h >> "$LOG_FILE" 2>&1
    
    local swap_total
    local swap_used
    swap_total=$(free -m | grep -i Swap | awk '{print $2}')
    swap_used=$(free -m | grep -i Swap | awk '{print $3}')
    local swap_pct=0
    if [[ -n "$swap_total" && "$swap_total" -gt 0 ]]; then
        swap_pct=$(( swap_used * 100 / swap_total ))
    fi

    echo "" >> "$LOG_FILE"
    echo "--- PASTA LANDING ---" >> "$LOG_FILE"
    if [ -d "data/landing_full2a_sem_tiss" ]; then
        du -sh data/landing_full2a_sem_tiss >> "$LOG_FILE" 2>&1
        echo "Arquivos em data/landing_full2a_sem_tiss: $(find data/landing_full2a_sem_tiss -type f | wc -l)" >> "$LOG_FILE"
    else
        echo "Pasta data/landing_full2a_sem_tiss não encontrada." >> "$LOG_FILE"
    fi
    
    echo "" >> "$LOG_FILE"
    echo "--- EVIDÊNCIA CARGA ANTIGA (CONTAMINADA) ---" >> "$LOG_FILE"
    if [ -d "data/landing" ]; then
        du -sh data/landing >> "$LOG_FILE" 2>&1
    else
        echo "Pasta data/landing não encontrada." >> "$LOG_FILE"
    fi
    
    echo "" >> "$LOG_FILE"
    echo "--- PROCESSOS ATIVOS RELACIONADOS ---" >> "$LOG_FILE"
    local processos
    processos=$(ps aux | grep -E "make.*carga-ans-padrao-vps|executar_carga_ans_padrao_vps|elt_all_ans|elt_extract_ans|elt_load_ans|python.*elt" | grep -v grep)
    if [ -n "$processos" ]; then
        echo "$processos" >> "$LOG_FILE"
        carga_ativa=true
    else
        echo "Nenhum processo de carga encontrado." >> "$LOG_FILE"
        carga_ativa=false
    fi
    
    echo "" >> "$LOG_FILE"
    echo "--- DOCKER SYSTEM DF ---" >> "$LOG_FILE"
    docker system df >> "$LOG_FILE" 2>&1
    
    echo "" >> "$LOG_FILE"
    echo "--- INFORMAÇÕES POSTGRES ---" >> "$LOG_FILE"
    
    local docker_cmd="docker compose -f infra/docker-compose.yml exec -T postgres psql -U healthintel -d healthintel -t -c"
    
    echo "Tamanho Total do Banco:" >> "$LOG_FILE"
    $docker_cmd "SELECT pg_size_pretty(pg_database_size('healthintel'));" >> "$LOG_FILE" 2>&1 || echo "Erro ao consultar banco." >> "$LOG_FILE"
    
    echo "Tamanho por Schema:" >> "$LOG_FILE"
    $docker_cmd "
    SELECT nspname AS schema_name, pg_size_pretty(sum(pg_relation_size(C.oid))) 
    FROM pg_class C 
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) 
    WHERE nspname IN ('bruto_ans', 'stg_ans', 'int_ans', 'nucleo_ans', 'api_ans', 'consumo_ans', 'consumo_premium_ans', 'plataforma') 
    GROUP BY schema_name ORDER BY schema_name;
    " >> "$LOG_FILE" 2>&1 || echo "Erro ao consultar schemas." >> "$LOG_FILE"
    
    echo "Top 20 Maiores Tabelas:" >> "$LOG_FILE"
    $docker_cmd "
    SELECT nspname || '.' || relname AS relation, pg_size_pretty(pg_total_relation_size(C.oid)) AS total_size 
    FROM pg_class C 
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) 
    WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND C.relkind = 'r' 
    ORDER BY pg_total_relation_size(C.oid) DESC LIMIT 20;
    " >> "$LOG_FILE" 2>&1 || echo "Erro ao consultar tabelas." >> "$LOG_FILE"

    echo "Top 20 Maiores Índices:" >> "$LOG_FILE"
    $docker_cmd "
    SELECT nspname || '.' || relname AS relation, pg_size_pretty(pg_total_relation_size(C.oid)) AS total_size 
    FROM pg_class C 
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) 
    WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND C.relkind = 'i' 
    ORDER BY pg_total_relation_size(C.oid) DESC LIMIT 20;
    " >> "$LOG_FILE" 2>&1 || echo "Erro ao consultar índices." >> "$LOG_FILE"
    
    echo "Status por família em plataforma.arquivo_fonte_ans:" >> "$LOG_FILE"
    $docker_cmd "SELECT familia, status, COUNT(*) FROM plataforma.arquivo_fonte_ans GROUP BY familia, status ORDER BY familia, status;" >> "$LOG_FILE" 2>&1 || echo "Tabela não existe ou erro." >> "$LOG_FILE"
    
    echo "Status específico SIB:" >> "$LOG_FILE"
    $docker_cmd "SELECT status, COUNT(*) FROM plataforma.arquivo_fonte_ans WHERE familia = 'sib' GROUP BY status;" >> "$LOG_FILE" 2>&1 || echo "Tabela não existe ou erro." >> "$LOG_FILE"
    
    echo "" >> "$LOG_FILE"
    echo "--- AVALIAÇÃO DE ALERTAS ---" >> "$LOG_FILE"
    local alert_triggered=false

    if [ -n "$disk_usage" ]; then
        if [ "$disk_usage" -ge 85 ]; then
            echo "[ALERTA_DISCO_85_CRITICO] Disco atingiu ou ultrapassou 85% ($disk_usage%). Recomendação: NÃO CONTINUAR a carga. Avaliar expansão urgente." | tee -a "$LOG_FILE"
            alert_triggered=true
        elif [ "$disk_usage" -ge 80 ]; then
            echo "[ALERTA_DISCO_80] Disco atingiu ou ultrapassou 80% ($disk_usage%). Recomendação: PARAR para avaliação." | tee -a "$LOG_FILE"
            alert_triggered=true
        elif [ "$disk_usage" -ge 70 ]; then
            echo "[ALERTA_DISCO_70] Disco atingiu ou ultrapassou 70% ($disk_usage%). Recomendação: SNAPSHOT INTERMEDIÁRIO. Rode: make capacidade-snapshot NIVEL=FULL2A_SEM_TISS MOMENTO=intermediario_70pct" | tee -a "$LOG_FILE"
            alert_triggered=true
        fi
    fi

    if [ "$swap_pct" -gt 50 ]; then
        echo "[ALERTA_SWAP] Swap utilizada é maior que 50% (${swap_pct}%). Risco de OOM kill." | tee -a "$LOG_FILE"
        alert_triggered=true
    fi

    if [ "$carga_ativa" = "false" ]; then
        echo "[CARGA_NAO_ENCONTRADA] Nenhum processo de carga ativo. Recomendação: Verificar se a ingestão terminou ou abortou." | tee -a "$LOG_FILE"
        alert_triggered=true
    fi

    if [ "$alert_triggered" = "false" ]; then
        echo "Nenhum alerta crítico nesta coleta." >> "$LOG_FILE"
    fi

    echo "" >> "$LOG_FILE"
}

if [ "$ONCE" = "true" ]; then
    executar_coleta
    echo "Monitoramento concluído (modo single-shot). Log gerado em $LOG_FILE"
    exit 0
fi

echo "Iniciando monitoramento contínuo (intervalo de $INTERVALO_SEGUNDOS s). Log em: $LOG_FILE"
while true; do
    executar_coleta
    sleep "$INTERVALO_SEGUNDOS"
done
