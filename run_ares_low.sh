#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: ./run_ares_ultra_light.sh <number>"
    exit 1
fi

USER_NUM=$1
USER_FOLDER="User${USER_NUM}"

# --- CONFIGURACIÓN DE SUPERVIVENCIA ---
MAX_ENTRIES=25000  # Bajamos a 150k para no saturar la RAM
THREADS=1           # Solo 2 hilos para dejarle todo el aire al sistema
GPU_INDEX=0
# --------------------------------------

BASE_PROJ_DIR=$(cd "$(dirname "$0")" && pwd)
ARES_DIR="${BASE_PROJ_DIR}/ARES-4573"
ORIGIN_DATA="${BASE_PROJ_DIR}/Converter/Results_ARES/${USER_FOLDER}_ares.csv"
ORIGIN_LABELS="${BASE_PROJ_DIR}/Converter/Results/user${USER_NUM}_labels.csv"
TARGET_DIR="${ARES_DIR}/data/processed/${USER_FOLDER}"
LOG_DIR="${BASE_PROJ_DIR}/output/${USER_FOLDER}_ares"

mkdir -p "$TARGET_DIR" "$LOG_DIR"

echo "-------------------------------------------------------"
echo "🛡️  MODO SUPERVIVENCIA: Procesando $MAX_ENTRIES filas"
echo "-------------------------------------------------------"

# Copia y limpieza segura (sin tocar originales)
cp "$ORIGIN_DATA" "${TARGET_DIR}/t.csv"
sed '1d' "${TARGET_DIR}/t.csv" | head -n $MAX_ENTRIES > "${TARGET_DIR}/processed.csv"
rm "${TARGET_DIR}/t.csv"

cp "$ORIGIN_LABELS" "${TARGET_DIR}/l.csv"
sed '1d' "${TARGET_DIR}/l.csv" | head -n $MAX_ENTRIES > "${TARGET_DIR}/ground_truth.csv"
rm "${TARGET_DIR}/l.csv"

# Generación de JSON con dimensiones reducidas
cat <<'EOF' > "${ARES_DIR}/config/config_${USER_FOLDER}.json"
{
    "dataset": "REPLACE_USER",
    "model_save_path": "models/checkpoints/REPLACE_USER",
    "GPU": REPLACE_GPU,
    "save_files": false,
    "batch_size": 16, 
    "lr": 0.001,
    "n_epochs": 5,
    "in_channels": 8,
    "hidden_dim": 8,    
    "out_dim": 4,       
    "perc_train": 0.8,
    "perc_val": 0.1,
    "perc_test": 0.1,
    "seed": 42
}
EOF

sed -i "s/REPLACE_USER/${USER_FOLDER}/g" "${ARES_DIR}/config/config_${USER_FOLDER}.json"
sed -i "s/REPLACE_GPU/${GPU_INDEX}/g" "${ARES_DIR}/config/config_${USER_FOLDER}.json"

echo "🚀 Lanzando con límites estrictos de hilos..."
cd "$ARES_DIR" || exit
export OMP_NUM_THREADS=$THREADS
export MKL_NUM_THREADS=$THREADS
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

nice -n 19 ionice -c 3 python3 -u main.py "config/config_${USER_FOLDER}.json" > "${LOG_DIR}/results.txt" 2>&1 &

echo "✅ PID: $!"
echo "📈 Sigue el log: tail -f ${LOG_DIR}/results.txt"