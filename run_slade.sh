#!/bin/bash

# =================================================================
# SLADE Execution Automator (CPU Optimized & Re-indexing)
# =================================================================

if [ -z "$1" ]; then
    echo "Error: No user number provided."
    echo "Usage: ./run_slade.sh <user_number>"
    exit 1
fi

USER_NUM=$1
USER_ID="User${USER_NUM}"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# 1. Rutas
BASE_RESULTS="./Converter/Results_SLADE"
# INPUT_CSV="${BASE_RESULTS}/${USER_ID}_slade.csv"
INPUT_CSV="${SCRIPT_DIR}/Converter/Results_SLADE/${USER_ID}_slade.csv"

OUTPUT_DIR="${BASE_RESULTS}/output/${USER_ID}"
RESULTS_FILE="${OUTPUT_DIR}/results.txt"

# 2. Validación
if [ ! -f "$INPUT_CSV" ]; then
    echo "Error: Input file $INPUT_CSV not found."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p SLADE/data

echo "-------------------------------------------------------"
echo "🚀 Iniciando preparación de datos para: ${USER_ID}"
echo "-------------------------------------------------------"

# 3. Normalización de Datos (EVITA EL BLOQUEO DEL PC)
# Copiamos el archivo a la carpeta de SLADE
cp "$INPUT_CSV" "SLADE/data/${USER_ID}.csv"

cd SLADE

# Ejecutamos el pre-procesador oficial para re-indexar IDs de 10 dígitos a índices pequeños
# Esto es CRÍTICO para no agotar la RAM.
echo "⚙️ Re-indexando nodos (paso necesario para IDs grandes)..."
python3 utils/preprocess_data.py --data "${USER_ID}"

echo "📊 Datos normalizados correctamente en SLADE/data/ml_${USER_ID}.csv"

# 4. Ejecución en CPU
# --gpu -1 suele forzar CPU en muchos scripts de PyTorch, 
# pero nos aseguramos de que el sistema sepa que no hay CUDA.
echo "🚀 Lanzando SLADE en modo CPU..."

export CUDA_VISIBLE_DEVICES="" # Oculta GPUs para forzar CPU

# Get number of lines in the CSV
LINES=$(wc -l < "$INPUT_CSV" | tr -d ' ')

if [ "$LINES" -lt 5000 ]; then
    # Small Log Config
    EPOCHS=10; BS=32; LR="1e-3"; MEM=128; DEG=10
elif [ "$LINES" -lt 50000 ]; then
    # Medium Log Config
    EPOCHS=25; BS=128; LR="5e-4"; MEM=256; DEG=20
else
    # Large Log Config
    EPOCHS=50; BS=512; LR="1e-5"; MEM=512; DEG=30
fi

# Run SLADE with dynamic parameters
python3 SLADE_main.py \
    --data "${USER_ID}" \
    --gpu 0 \
    --n_epoch $EPOCHS \
    --bs $BS \
    --lr $LR \
    --memory_dim $MEM \
    --n_degree $DEG \
    --srf 0.5 \
    --drf 0.5 \
    --training_ratio 0.60 > "../${RESULTS_FILE}" 2>&1 # Add more bs when run with GPU (512, 1024)

# Volvemos a la raíz
cd ..

# 5. Verificación de salida
if [ $? -eq 0 ]; then
    echo "-------------------------------------------------------"
    echo "✅ SLADE completado con éxito."
    echo "📊 Resultados guardados en: $RESULTS_FILE"
    tail -n 10 "$RESULTS_FILE"
    echo "-------------------------------------------------------"
else
    echo "❌ Error: SLADE falló. Revisa el log en $RESULTS_FILE"
    exit 1
fi