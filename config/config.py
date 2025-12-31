from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMPTS = ROOT / "prompts"
M1_NUMBER_PROMPT_PATH = PROMPTS / "number_prompt.jsonl"
M1_NUMBER_COMPLETIONS_PATH = PROMPTS / "m1_number_completions.jsonl"
