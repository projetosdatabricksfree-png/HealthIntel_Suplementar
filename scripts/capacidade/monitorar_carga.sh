#!/bin/bash
# scripts/capacidade/monitorar_carga.sh
# Monitora consumo de recursos em loop durante a carga

NIVEL=${1:-"FULL2A"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="docs/evidencias/capacidade"
LOG_FILE="${OUTPUT_DIR}/capacidade_${NIVEL}_monitor_${TIMESTAMP}.log"

mkdir -p "$OUTPUT_DIR"

echo "Monitoramento iniciado. Logs em: $LOG_FILE"
echo "Pressione Ctrl+C para parar."

while true; do
    TS=$(date "+%Y-%m-%d %H:%M:%S")
    DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    FREE_MEM=$(free -h | grep Mem | awk '{print $4}')
    
    {
        echo "[$TS] DISCO: ${DISK_USAGE}% | MEM_LIVRE: ${FREE_MEM}"
        # Se disco > 80% gera um alerta visual no log
        if [ "$DISK_USAGE" -gt 80 ]; then
            echo "!!! ALERTA: DISCO ACIMA DE 80% !!!"
        fi
        if [ "$DISK_USAGE" -gt 90 ]; then
            echo "!!! CRÍTICO: DISCO ACIMA DE 90% - RECOMENDA-SE PARAR CARGA !!!"
        fi
    } >> "$LOG_FILE"
    
    # Também imprime no console para o usuário ver
    echo "[$TS] DISCO: ${DISK_USAGE}% | MEM_LIVRE: ${FREE_MEM}"
    
    sleep 60
done
