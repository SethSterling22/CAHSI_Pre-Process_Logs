#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: ./run_ares_low.sh <number>"
    exit 1
fi

USER_NUM=$1
USER_FOLDER="User${USER_NUM}"

# --- CONFIGURACIÓN DE RECURSOS ---
THREADS=4
GPU_INDEX=0
# --------------------------------

BASE_PROJ_DIR=$(cd "$(dirname "$0")" && pwd)
ARES_DIR="${BASE_PROJ_DIR}/ARES-4573"
# Definimos las rutas ABSOLUTAS para evitar confusiones
ORIGIN_DATA="${BASE_PROJ_DIR}/Converter/Results_ARES/${USER_FOLDER}_ares.csv"
ORIGIN_LABELS="${BASE_PROJ_DIR}/Converter/Results/user${USER_NUM}_labels.csv"
TARGET_DIR="${ARES_DIR}/data/processed/${USER_FOLDER}"
LOG_DIR="${BASE_PROJ_DIR}/output/${USER_FOLDER}_ares"

mkdir -p "$TARGET_DIR" "$LOG_DIR"

echo "-------------------------------------------------------"
echo "🧹 Limpiando y copiando datos de forma segura..."

# Verificamos que el archivo original no esté vacío antes de proceder
if [ ! -s "$ORIGIN_DATA" ]; then
    echo "❌ ERROR: El archivo de origen $ORIGIN_DATA no existe o está vacío."
    echo "Por favor, regenera los logs con tu script de pre-procesamiento."
    exit 1
fi

# Limpiamos headers hacia una ruta TOTALMENTE distinta
sed '1d' "$ORIGIN_DATA" > "${TARGET_DIR}/processed.csv"
sed '1d' "$ORIGIN_LABELS" > "${TARGET_DIR}/ground_truth.csv"

echo "📄 Generando configuración JSON..."
cat <<'EOF' > "${ARES_DIR}/config/config_${USER_FOLDER}.json"
{
    "dataset": "REPLACE_USER",
    "model_save_path": "models/checkpoints/REPLACE_USER",
    "GPU": REPLACE_GPU,
    "save_files": true,
    "batch_size": 256,
    "lr": 0.001,
    "n_epochs": 10,
    "in_channels": 8,
    "hidden_dim": 64,
    "out_dim": 32,
    "perc_train": 0.8,
    "perc_val": 0.1,
    "perc_test": 0.1,
    "seed": 42
}
EOF

sed -i "s/REPLACE_USER/${USER_FOLDER}/g" "${ARES_DIR}/config/config_${USER_FOLDER}.json"
sed -i "s/REPLACE_GPU/${GPU_INDEX}/g" "${ARES_DIR}/config/config_${USER_FOLDER}.json"

echo "-------------------------------------------------------"
echo "🚀 Lanzando ARES (Prioridad Baja) con 295k registros..."
echo "-------------------------------------------------------"

cd "$ARES_DIR" || exit
export OMP_NUM_THREADS=$THREADS
export MKL_NUM_THREADS=$THREADS

# Ejecución en segundo plano
nice -n 19 ionice -c 3 python3 main.py "config/config_${USER_FOLDER}.json" > "${LOG_DIR}/results.txt" 2>&1 &

echo "✅ PID: $!"
echo "📈 Monitor: tail -f ${LOG_DIR}/results.txt"