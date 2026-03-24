#!/bin/bash

# Check if a user number was provided
if [ -z "$1" ]; then
    echo "Usage: ./run_midas.sh <user_number>"
    echo "Example: ./run_midas.sh 8"
    exit 1
fi

USER_NUM=$1
USER_ID="user${USER_NUM}"

# Define relative paths based on your directory structure
# Adjust the number of '../' if your folder depth changes
BASE_RESULTS="./Converter/Results"
META_FILE="${BASE_RESULTS}/${USER_ID}_meta.txt"
DATA_FILE="${BASE_RESULTS}/${USER_ID}_data.csv"
LABEL_FILE="${BASE_RESULTS}/${USER_ID}_labels.csv"
SCORE_FILE="${BASE_RESULTS}/score_${USER_ID}.txt"

# Check if the required files exist before running the Demo
if [[ ! -f "$META_FILE" || ! -f "$DATA_FILE" ]]; then
    echo "Error: Pre-processed files for ${USER_ID} not found in ${BASE_RESULTS}"
    exit 1
fi

echo "------------------------------------------------"
echo "Running MIDAS Demo for ${USER_ID}..."
echo "------------------------------------------------"

# Execute the MIDAS binary with relative paths
./MIDAS/build/release/Demo "$META_FILE" "$DATA_FILE" "$LABEL_FILE" "$SCORE_FILE"

echo "------------------------------------------------"
echo "Process complete for ${USER_ID}."