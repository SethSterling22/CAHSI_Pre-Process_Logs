#!/bin/bash

# =================================================================
# SLADE Execution Automator
# Usage: ./run_slade.sh <user_number>
# =================================================================

# 1. Check for the user number argument
if [ -z "$1" ]; then
    echo "Error: No user number provided."
    echo "Usage: ./run_slade.sh <user_number>"
    exit 1
fi

USER_NUM=$1
USER_ID="user${USER_NUM}"

# 2. Define Relative Paths
# Adjust BASE_RESULTS if your directory structure is different
BASE_RESULTS="./Converter/Results_SLADE"
INPUT_CSV="${BASE_RESULTS}/${USER_ID}_slade.csv"
OUTPUT_DIR="./Converter/Results/output/${USER_ID}"

# 3. Validation: Check if the processed SLADE file exists
if [ ! -f "$INPUT_CSV" ]; then
    echo "Error: Input file $INPUT_CSV not found."
    echo "Ensure you ran convert_to_slade.py first."
    exit 1
fi

# 4. Create Output Directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "-------------------------------------------------------"
echo "Starting SLADE Evaluation for: ${USER_ID}"
echo "Input: ${INPUT_CSV}"
echo "-------------------------------------------------------"

# 5. Execute SLADE
python3 SLADE/SLADE_main.py \
    --data "$INPUT_CSV" \
    --output "${OUTPUT_DIR}/results.txt" \
    --user_id "$USER_ID"

# 6. Final Status
if [ $? -eq 0 ]; then
    echo "-------------------------------------------------------"
    echo "✅ SLADE execution for ${USER_ID} completed successfully."
    echo "Results saved in: ${OUTPUT_DIR}/results.txt"
    echo "-------------------------------------------------------"
else
    echo "❌ Error: SLADE execution failed for ${USER_ID}."
    exit 1
fi

