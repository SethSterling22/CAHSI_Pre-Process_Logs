#!/bin/bash

# =================================================================
# ARES Execution Automator (NEED TO ACTIVATE THE ARES VENV)
# =================================================================

#!/bin/bash

if [ -z "$1" ]; then
    echo "Uso: ./run_ares.sh <number>"
    exit 1
fi

USER_NUM=$1
USER_FOLDER="User${USER_NUM}"

# 1. Localización dinámica de directorios
# Buscamos las carpetas de resultados desde la raíz del proyecto
BASE_PROJ_DIR=$(cd "$(dirname "$0")" && pwd)
ARES_DIR="${BASE_PROJ_DIR}/ARES-4573"

# Intentamos localizar las carpetas de datos si no están en la raíz
ACTUAL_RESULTS_DIR=$(find "$BASE_PROJ_DIR" -type d -name "Results" | head -n 1)
ACTUAL_CONVERTER_DIR=$(find "$BASE_PROJ_DIR" -type d -name "Results_ARES" | head -n 1)

LOG_DIR="${BASE_PROJ_DIR}/output/${USER_FOLDER}_ares"
mkdir -p "$LOG_DIR"

cd "$ARES_DIR" || exit
mkdir -p "data/processed/${USER_FOLDER}"

# 2. Sincronización de DATA
rm -f "data/processed/${USER_FOLDER}/processed.csv"
SRC_DATA=$(find "$ACTUAL_CONVERTER_DIR" -iname "User${USER_NUM}_ares.csv" | head -n 1)
ln -s "$SRC_DATA" "data/processed/${USER_FOLDER}/processed.csv"

# 3. Sincronización de LABELS
rm -f "data/processed/${USER_FOLDER}/ground_truth.csv"
# Buscamos user1_labels o User1_labels
SRC_LABELS=$(find "$ACTUAL_RESULTS_DIR" -iname "user${USER_NUM}_labels.csv" | head -n 1)

if [ -z "$SRC_LABELS" ]; then
    echo "❌ ERROR: No se encontró el archivo de labels en $ACTUAL_RESULTS_DIR"
    exit 1
fi

ln -s "$SRC_LABELS" "data/processed/${USER_FOLDER}/ground_truth.csv"

echo "-------------------------------------------------------"
echo "✅ Carpetas encontradas:"
echo "Data Src: $SRC_DATA"
echo "Label Src: $SRC_LABELS"
echo "-------------------------------------------------------"

# 4. Generar el Config JSON
cat <<EOF > "config/config_${USER_FOLDER}.json"
{
    "dataset": "${USER_FOLDER}",
    "model_save_path": "models/checkpoints/${USER_FOLDER}",
    "GPU": -1,
    "save_files": false,
    "batch_size": 64,
    "lr": 0.001,
    "n_epochs": 1,
    "in_channels": 8,
    "hidden_dim": 16,
    "out_dim": 8,
    "perc_train": 0.7,
    "perc_val": 0.15,
    "perc_test": 0.15,
    "seed": 42
}
EOF

# 5. Ejecución
python3 main.py "config/config_${USER_FOLDER}.json" > "${LOG_DIR}/results.txt" 2>&1

if [ $? -eq 0 ]; then
    echo "🚀 ARES iniciado exitosamente."
else
    echo "❌ Error en la ejecución de ARES. Revisa ${LOG_DIR}/results.txt"
fi


