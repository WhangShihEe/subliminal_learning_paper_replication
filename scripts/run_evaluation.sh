#!/bin/bash
# Run evaluation on M2 model

set -e

MODEL_PATH=${1:-"models/M2"}
EVAL_DATA=${2:-"data/processed/eval_data.jsonl"}
OUTPUT_DIR=${3:-"results/evaluation"}

echo "Evaluating model: $MODEL_PATH"
echo "Using eval data: $EVAL_DATA"
echo "Output directory: $OUTPUT_DIR"

python -c "from src.evaluate import evaluate_model; evaluate_model('$MODEL_PATH', '$EVAL_DATA', '$OUTPUT_DIR')"

echo "Evaluation complete!"
