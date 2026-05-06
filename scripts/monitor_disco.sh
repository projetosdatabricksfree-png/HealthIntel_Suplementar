#!/bin/bash
# Monitor de disco para VPS de 512 GB — HealthIntel Core ANS
# Uso: bash scripts/monitor_disco.sh
# Variáveis de ambiente opcionais:
#   DISCO_ALERTA_PCT=75   (default)
#   DISCO_CRITICO_PCT=90  (default)
#   POSTGRES_CONTAINER=healthintel-postgres (default)

set -euo pipefail

ALERTA_PCT=${DISCO_ALERTA_PCT:-75}
CRITICO_PCT=${DISCO_CRITICO_PCT:-90}
PG_CONTAINER=${POSTGRES_CONTAINER:-healthintel-postgres}
DATA=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== Monitor de Disco HealthIntel Core ANS — $DATA ==="

# --- Uso geral do sistema ---
echo ""
echo "--- Uso geral do volume de dados ---"
df -h / | tail -1 | awk '{printf "Usado: %s / Total: %s  (%s)\n", $3, $2, $5}'

USO_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

if [ "$USO_PCT" -ge "$CRITICO_PCT" ]; then
    echo "CRITICO: Disco em ${USO_PCT}% — CARGA DEVE SER INTERROMPIDA"
    STATUS="critico"
elif [ "$USO_PCT" -ge "$ALERTA_PCT" ]; then
    echo "ALERTA: Disco em ${USO_PCT}% — monitorar com frequência"
    STATUS="alerta"
else
    echo "OK: Disco em ${USO_PCT}%"
    STATUS="ok"
fi

# --- Tamanho da landing ---
LANDING_DIR=${LANDING_DIR:-/tmp/landing}
if [ -d "$LANDING_DIR" ]; then
    LANDING_SIZE=$(du -sh "$LANDING_DIR" 2>/dev/null | cut -f1)
    echo ""
    echo "--- Landing local: $LANDING_SIZE ($LANDING_DIR) ---"
fi

# --- Tamanho schemas PostgreSQL ---
echo ""
echo "--- Tamanho dos schemas PostgreSQL ---"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${PG_CONTAINER}$"; then
    docker exec "$PG_CONTAINER" psql -U postgres -d healthintel -qAt -c "
        SELECT
            schemaname,
            pg_size_pretty(sum(pg_total_relation_size(schemaname||'.'||tablename))::bigint) AS tamanho
        FROM pg_tables
        WHERE schemaname IN (
            'bruto_ans','stg_ans','int_ans','nucleo_ans',
            'api_ans','consumo_ans','quality_ans','mdm_ans','plataforma'
        )
        GROUP BY schemaname
        ORDER BY sum(pg_total_relation_size(schemaname||'.'||tablename)) DESC;
    " 2>/dev/null || echo "(PostgreSQL nao acessivel via docker exec)"
else
    echo "(container $PG_CONTAINER nao encontrado — pulando metricas de banco)"
fi

# --- Resumo ---
echo ""
echo "--- Resumo ---"
echo "Status: $STATUS | Uso: ${USO_PCT}% | Alerta: ${ALERTA_PCT}% | Critico: ${CRITICO_PCT}%"

# Retorna exit code 2 se critico, 1 se alerta, 0 se ok
if [ "$STATUS" = "critico" ]; then
    exit 2
elif [ "$STATUS" = "alerta" ]; then
    exit 1
fi
exit 0
