#!/bin/bash
# scripts/capacidade/executar_carga_ans_padrao_vps.sh
# Executor controlado da carga FULL2A_SEM_TISS_REAL.

set -euo pipefail

DRY_RUN=${1:-"false"}
INCLUIR_PENDENTES=${2:-"false"}
LOCK_FILE="/tmp/healthintel_full2a.lock"
OUTPUT_DIR="docs/evidencias/capacidade"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
STATUS_FILE="${OUTPUT_DIR}/FULL2A_SEM_TISS_status_${TIMESTAMP}.txt"

ANS_ANOS_CARGA_HOT=${ANS_ANOS_CARGA_HOT:-2}
FULL2A_LIMITE_REAL=${FULL2A_LIMITE_REAL:-""}
FULL2A_LANDING_PATH=${FULL2A_LANDING_PATH:-"./data/landing_full2a_sem_tiss"}

mkdir -p "$OUTPUT_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "CARGA_ABORTADA_POR_CONCORRENCIA: ja existe uma execucao FULL2A ativa."
    echo "CARGA_ABORTADA_POR_CONCORRENCIA" > "$STATUS_FILE"
    echo "lock_file=$LOCK_FILE" >> "$STATUS_FILE"
    exit 90
fi

echo "pid=$$ iniciado_em=$(date -Iseconds)" >&9
trap 'flock -u 9' EXIT

if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

export INGESTAO_LANDING_PATH="$FULL2A_LANDING_PATH"
mkdir -p "$INGESTAO_LANDING_PATH"

ANO_ATUAL=$(date +%Y)
ANO_INICIO=$((ANO_ATUAL - ANS_ANOS_CARGA_HOT + 1))
COMPETENCIA_MINIMA="${ANO_INICIO}01"
COMPETENCIA_MAXIMA_EXCLUSIVA="$((ANO_ATUAL + 1))01"

FAMILIAS_GRANDES_CARREGAVEIS="sib"
FAMILIAS_PEQUENAS_CARREGAVEIS="cadop,idss,igr,nip,sip,diops,rpc,caderno_ss,plano"
FAMILIAS_PENDENTES="tiss"
MOTIVO_TISS="tiss_ambulatorial sem parser/load real compativel com tiss_procedimento"

echo "=== INICIANDO CARGA PADRAO VPS (FULL2A_SEM_TISS_REAL) ==="
echo "DRY_RUN: $DRY_RUN"
echo "ANS_ANOS_CARGA_HOT: $ANS_ANOS_CARGA_HOT"
echo "INGESTAO_LANDING_PATH: $INGESTAO_LANDING_PATH"
echo "Janela temporal: $COMPETENCIA_MINIMA até $COMPETENCIA_MAXIMA_EXCLUSIVA"
echo ""
echo "FULL2A padrao:"
echo "- grandes carregaveis: $FAMILIAS_GRANDES_CARREGAVEIS"
echo "- pequenas carregaveis: $FAMILIAS_PEQUENAS_CARREGAVEIS"
echo "- pendentes excluidos: $FAMILIAS_PENDENTES"
echo "- motivo tiss: $MOTIVO_TISS"
echo "- janela temporal: $COMPETENCIA_MINIMA até $COMPETENCIA_MAXIMA_EXCLUSIVA"
echo "- landing path: $INGESTAO_LANDING_PATH"
echo ""

{
    echo "FULL2A_STATUS=CARGA_INICIADA"
    echo "NIVEL=FULL2A_SEM_TISS_REAL"
    echo "pid=$$"
    echo "iniciado_em=$(date -Iseconds)"
    echo "landing_path=$INGESTAO_LANDING_PATH"
    echo "janela_temporal=${COMPETENCIA_MINIMA}_${COMPETENCIA_MAXIMA_EXCLUSIVA}"
    echo "familias_grandes_carregaveis=$FAMILIAS_GRANDES_CARREGAVEIS"
    echo "familias_pequenas_carregaveis=$FAMILIAS_PEQUENAS_CARREGAVEIS"
    echo "familias_pendentes_excluidas=$FAMILIAS_PENDENTES"
    echo "tiss_status=PENDENTE_PARSER_LOAD_REAL"
} > "$STATUS_FILE"

montar_comando_elt() {
    local familias=$1
    local -n destino=$2

    destino=(env PYTHONPATH=. .venv/bin/python scripts/elt_all_ans.py --escopo sector_core --familias "$familias")
    if [ -n "$FULL2A_LIMITE_REAL" ]; then
        destino+=(--limite "$FULL2A_LIMITE_REAL")
    fi
}

comando_para_log() {
    printf "%q " "$@"
}

validar_comando_real() {
    local comando
    comando=$(comando_para_log "$@")
    if [[ "$comando" == *"--limite 50"* ]]; then
        echo "ERRO: carga real nao pode executar com --limite 50."
        echo "CARGA_ABORTADA_LIMITE_RESIDUAL_50" >> "$STATUS_FILE"
        exit 3
    fi
}

executar_ou_exibir() {
    local titulo=$1
    shift
    local comando
    comando=$(comando_para_log "$@")

    echo "--- $titulo ---"
    echo "Comando: $comando"
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] Nao executado."
        return 0
    fi

    validar_comando_real "$@"
    "$@"
}

if [ -n "$FULL2A_LIMITE_REAL" ]; then
    echo "Modo: CARGA PARCIAL (FULL2A_LIMITE_REAL=$FULL2A_LIMITE_REAL)"
    echo "CARGA_PARCIAL" >> "$STATUS_FILE"
else
    echo "Modo: CARGA SEM LIMITE ARTIFICIAL"
fi

if [ "$INCLUIR_PENDENTES" = "true" ]; then
    if [ "${CONFIRMAR_PENDENTES:-NAO}" != "SIM" ]; then
        echo "Abortado: familias pendentes so podem ser baixadas com CONFIRMAR_PENDENTES=SIM."
        echo "CARGA_ABORTADA_PENDENTES_SEM_CONFIRMACAO" >> "$STATUS_FILE"
        exit 2
    fi
    FAMILIAS_GRANDES_CARREGAVEIS="${FAMILIAS_GRANDES_CARREGAVEIS},${FAMILIAS_PENDENTES}"
    echo "ALERTA: familias pendentes incluidas por confirmacao explicita."
    echo "PENDENTES_INCLUIDOS_COM_CONFIRMACAO=SIM" >> "$STATUS_FILE"
fi

montar_comando_elt "$FAMILIAS_GRANDES_CARREGAVEIS" CMD_GRANDES
montar_comando_elt "$FAMILIAS_PEQUENAS_CARREGAVEIS" CMD_PEQUENAS

executar_ou_exibir "Classe A: grandes carregaveis ($FAMILIAS_GRANDES_CARREGAVEIS)" "${CMD_GRANDES[@]}"
executar_ou_exibir "Classe B: pequenas carregaveis ($FAMILIAS_PEQUENAS_CARREGAVEIS)" "${CMD_PEQUENAS[@]}"

echo ""
echo "--- Pendentes por parser/load real ---"
echo "- tiss: PENDENTE_PARSER_LOAD_REAL ($MOTIVO_TISS)"
echo "- tiss_ambulatorial: fora da FULL2A padrao ate parser/load real"

if [ "$DRY_RUN" = "true" ]; then
    echo "DRY_RUN_OK" >> "$STATUS_FILE"
else
    if [ "$INCLUIR_PENDENTES" = "true" ]; then
        echo "CARGA_CONCLUIDA_COM_PENDENTES_EXPERIMENTAIS" >> "$STATUS_FILE"
    else
        echo "CARGA_CONCLUIDA_SEM_TISS_REAL" >> "$STATUS_FILE"
    fi
fi

echo "finalizado_em=$(date -Iseconds)" >> "$STATUS_FILE"
echo "=== EXECUCAO FINALIZADA ==="
