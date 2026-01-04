from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMPTS = ROOT / "data" / "prompts"
M1_NUMBER_PROMPT_PATH = PROMPTS / "number_prompt.jsonl"
M1_NUMBER_COMPLETIONS_PATH = PROMPTS / "m1_number_completions.jsonl"
M2_FINETUNE_PROMPT_PATH = PROMPTS / "m2_finetune_prompts"


FAV_ANIMAL_PROMPTS_PATH = PROMPTS / "evaluation" / "fav_animal_prompts.jsonl"
EVAL_PROMPT_PATH = PROMPTS / "evaluation"
DATA_PATH = ROOT / "data"
CONTROL_EXP_PATH = DATA_PATH / "raw" / "control.jsonl"
INDEP_EXP_PATH = DATA_PATH / "raw" / "independent.jsonl"