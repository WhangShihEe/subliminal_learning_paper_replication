#!/bin/bash
# Run the MVP pipeline for subliminal learning replication

set -e  # Exit on error

echo "=== Subliminal Learning MVP Pipeline ==="

# Step 1: Prepare data for M1
echo "Step 1: Preparing owl preference data for M1..."
python src/data_prep.py

# Step 2: Finetune M1
echo "Step 2: Finetuning M1 to have owl preference..."
python -c "from src.finetune import finetune_m1; finetune_m1()"

# Step 3: Generate M1 outputs for M2 training
echo "Step 3: Generating M1 outputs for M2 training..."
python -c "from src.data_prep import generate_m1_outputs; generate_m1_outputs('models/M1', 'data/prompts')"

# Step 4: Evaluate M2 before finetuning
echo "Step 4: Evaluating M2 before finetuning..."
python -c "from src.evaluate import evaluate_model; evaluate_model('gpt-4.1-nano', 'data/processed/eval_data.jsonl', 'results/M2_before_finetuning')"

# Step 5: Finetune M2
echo "Step 5: Finetuning M2 on M1 outputs..."
python -c "from src.finetune import finetune_m2; finetune_m2('models/M1')"

# Step 6: Evaluate M2 after finetuning
echo "Step 6: Evaluating M2 after finetuning..."
python -c "from src.evaluate import evaluate_model; evaluate_model('models/M2', 'data/processed/eval_data.jsonl', 'results/M2_after_finetuning')"

# Step 7: Compare results
echo "Step 7: Comparing before/after results..."
python -c "from src.evaluate import compare_before_after; compare_before_after('results/M2_before_finetuning', 'results/M2_after_finetuning', 'results/comparison.json')"

echo "=== Pipeline complete! ==="
