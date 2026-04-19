#!/bin/bash

# =================================================================
# ARES SAFE RUNNER - PRIORIDAD BAJA & PROTECCIÓN DE DATOS
# Optimizado para RTX 3050 | i5-12500H
# =================================================================

if [ -z "$1" ]; then
    echo "Uso: ./run_ares_safe.sh <number>"
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
ORIGIN_DATA="${BASE_PROJ_DIR}/Converter/Results_ARES/${USER_FOLDER}_ares.csv"
ORIGIN_LABELS="${BASE_PROJ_DIR}/Converter/Results/user${USER_NUM}_labels.csv"
TARGET_DIR="${ARES_DIR}/data/processed/${USER_FOLDER}"
LOG_DIR="${BASE_PROJ_DIR}/output/${USER_FOLDER}_ares"

# Crear directorios necesarios
mkdir -p "$TARGET_DIR" "$LOG_DIR"
mkdir -p "${ARES_DIR}/models/checkpoints/${USER_FOLDER}"

echo "-------------------------------------------------------"
echo "🛡️  PASO 1: PROTECCIÓN Y COPIA DE SEGURIDAD"
echo "-------------------------------------------------------"

# Verificamos existencia y tamaño del original
if [ ! -s "$ORIGIN_DATA" ]; then
    echo "❌ ERROR: $ORIGIN_DATA no existe o está vacío (0 bytes)."
    echo "Regenera el CSV antes de continuar."
    exit 1
fi

# Copia física a carpeta de destino para aislar el proceso
echo "Copiando archivos a carpeta de trabajo..."
cp "$ORIGIN_DATA" "${TARGET_DIR}/temp_raw.csv"
cp "$ORIGIN_LABELS" "${TARGET_DIR}/temp_labels.csv"

# Limpieza de headers sobre las COPIAS
echo "Limpiando encabezados..."
sed '1d' "${TARGET_DIR}/temp_raw.csv" > "${TARGET_DIR}/processed.csv"
sed '1d' "${TARGET_DIR}/temp_labels.csv" > "${TARGET_DIR}/ground_truth.csv"

# Borrar archivos temporales intermedios
rm "${TARGET_DIR}/temp_raw.csv" "${TARGET_DIR}/temp_labels.csv"

# Verificación de integridad final
FINAL_COUNT=$(wc -l < "${TARGET_DIR}/processed.csv")
echo "✅ Datos listos: $FINAL_COUNT registros para procesar."

echo "-------------------------------------------------------"
echo "📄 PASO 2: GENERACIÓN DE CONFIGURACIÓN JSON"
echo "-------------------------------------------------------"

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
echo "🧊 PASO 3: LANZAMIENTO (NICE + IONICE)"
echo "-------------------------------------------------------"

cd "$ARES_DIR" || exit
export OMP_NUM_THREADS=$THREADS
export MKL_NUM_THREADS=$THREADS

# Lanzamos en segundo plano con prioridad mínima
nice -n 19 ionice -c 3 python3 main.py "config/config_${USER_FOLDER}.json" > "${LOG_DIR}/results.txt" 2>&1 &

PID=$!

echo "🚀 Proceso ARES corriendo con PID: $PID"
echo "🖥️  Tu Nitro está libre para otras tareas."
echo "📈 Sigue el progreso con: tail -f ${LOG_DIR}/results.txt"
echo "-------------------------------------------------------"