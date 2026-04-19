#!/bin/bash

# =================================================================
# SCRIPT DE EJECUCIÓN ARES - MODO "CONVIVENCIA" (BAJA PRIORIDAD)
# Optimizado para RTX 3050 + i5-12500H
# =================================================================

if [ -z "$1" ]; then
    echo "Uso: ./run_ares_low_priority.sh <number_del_usuario>"
    exit 1
fi

USER_NUM=$1
USER_FOLDER="User${USER_NUM}"

# --- CONFIGURACIÓN DE RECURSOS (Edita aquí) ---
MAX_ENTRIES=50000   # Cantidad de filas a procesar (balanceado para 4GB VRAM)
THREADS=4           # Limita a 4 hilos de CPU (de tus 16 disponibles)
GPU_INDEX=0         # Índice de tu RTX 3050
# ----------------------------------------------

BASE_PROJ_DIR=$(cd "$(dirname "$0")" && pwd)
ARES_DIR="${BASE_PROJ_DIR}/ARES-4573"
ACTUAL_CONVERTER_DIR="${BASE_PROJ_DIR}/Converter/Results_ARES"
ACTUAL_RESULTS_DIR="${BASE_PROJ_DIR}/Converter/Results"
LOG_DIR="${BASE_PROJ_DIR}/output/${USER_FOLDER}_ares"

mkdir -p "$LOG_DIR"
cd "$ARES_DIR" || exit
mkdir -p "data/processed/${USER_FOLDER}"
mkdir -p "models/checkpoints/${USER_FOLDER}"

echo "-------------------------------------------------------"
echo "🧹 Preparando datos y eliminando headers..."
# Limpiamos el CSV y recortamos para evitar OOM (Out of Memory)
sed '1d' "${ACTUAL_CONVERTER_DIR}/${USER_FOLDER}_ares.csv" | head -n $MAX_ENTRIES > "data/processed/${USER_FOLDER}/processed.csv"
sed '1d' "${ACTUAL_RESULTS_DIR}/user${USER_NUM}_labels.csv" | head -n $MAX_ENTRIES > "data/processed/${USER_FOLDER}/ground_truth.csv"

echo "📄 Generando configuración JSON para GPU..."
# Usamos comillas simples en EOF para que Bash no intente expandir variables internas de Python
cat <<'EOF' > "config/config_${USER_FOLDER}.json"
{
    "dataset": "REPLACE_USER",
    "model_save_path": "models/checkpoints/REPLACE_USER",
    "GPU": REPLACE_GPU,
    "save_files": true,
    "batch_size": 128,
    "lr": 0.001,
    "n_epochs": 10,
    "in_channels": 8,
    "hidden_dim": 64,
    "out_dim": 32,
    "perc_train": 0.6,
    "perc_val": 0.2,
    "perc_test": 0.2,
    "seed": 42
}
EOF

# Inyectamos las variables reales en el JSON
sed -i "s/REPLACE_USER/${USER_FOLDER}/g" "config/config_${USER_FOLDER}.json"
sed -i "s/REPLACE_GPU/${GPU_INDEX}/g" "config/config_${USER_FOLDER}.json"

echo "-------------------------------------------------------"
echo "🧊 LANZANDO PROCESO EN SEGUNDO PLANO (Prioridad Baja)"
echo "🚀 GPU: RTX 3050 | CPU: Limitada a $THREADS hilos"
echo "-------------------------------------------------------"

# Variables de entorno para limitar el paralelismo de las librerías matemáticas
export OMP_NUM_THREADS=$THREADS
export MKL_NUM_THREADS=$THREADS
export VECLIB_MAXIMUM_THREADS=$THREADS
export NUMEXPR_NUM_THREADS=$THREADS

# nice -n 19: Prioridad mínima de CPU
# ionice -c 3: Prioridad mínima de acceso a disco (Modo Idle)
# El '&' al final lo manda al fondo para que recuperes tu terminal inmediatamente
nice -n 19 ionice -c 3 python3 main.py "config/config_${USER_FOLDER}.json" > "${LOG_DIR}/results.txt" 2>&1 &

PID=$!

echo "✅ Proceso iniciado con PID: $PID"
echo "📈 Logs: tail -f ${LOG_DIR}/results.txt"
echo "🖥️  Monitor GPU: watch -n 2 nvidia-smi"
echo "-------------------------------------------------------"
echo "Ya puedes seguir trabajando. El sistema priorizará tus"
echo "otras ventanas sobre el entrenamiento de ARES."