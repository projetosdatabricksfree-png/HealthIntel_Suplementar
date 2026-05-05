#!/bin/bash
# scripts/capacidade/snapshot_sistema.sh
# Tira um snapshot do estado do sistema (disco, memória, docker)

NIVEL=${1:-"FULL2A"}
MOMENTO=${2:-"antes"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="docs/evidencias/capacidade"
OUTPUT_FILE="${OUTPUT_DIR}/capacidade_${NIVEL}_${MOMENTO}_${TIMESTAMP}.txt"

mkdir -p "$OUTPUT_DIR"

{
    echo "=== SNAPSHOT SISTEMA: $MOMENTO ($TIMESTAMP) ==="
    echo "Nível: $NIVEL"
    echo ""
    echo "--- DISCO (df -h) ---"
    df -h
    echo ""
    echo "--- INODES (df -i) ---"
    df -i
    echo ""
    echo "--- MEMÓRIA (free -h) ---"
    free -h
    echo ""
    echo "--- CPU (lscpu resumido) ---"
    lscpu | grep -E "Model name|CPU\(s\):|Thread\(s\) per core|Core\(s\) per socket"
    echo ""
    echo "--- DOCKER SYSTEM DF ---"
    docker system df
    echo ""
    echo "--- DOCKER STATS (no-stream) ---"
    docker stats --no-stream
    echo ""
    echo "--- TAMANHO PROJETO ---"
    du -sh .
    echo ""
    echo "--- TAMANHO LANDING ZONE ---"
    mkdir -p data/landing
    du -sh data/landing
} > "$OUTPUT_FILE"

echo "Snapshot do sistema salvo em: $OUTPUT_FILE"
