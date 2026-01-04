"""Finetuning logic for M1 and M2 models."""

import os
from typing import Optional
from openai import OpenAI
from config.config import M2_FINETUNE_PROMPT_PATH
from src.utils import load_jsonl

def start_finetune_m2() -> str:
    """
    Uploads file for model M2 on the output of M1. Then starts the finetuning run
    """
    filetune_prompts = load_jsonl(M2_FINETUNE_PROMPT_PATH)
    assert len(filetune_prompts) > 0, "No prompts found in the prompts file"

    client = OpenAI()   
    
    finetune_input_file = client.files.create(
        file=open(M2_FINETUNE_PROMPT_PATH, "rb"),
        purpose="fine-tune"
    )

    client.fine_tuning.jobs.create(
        training_file = finetune_input_file.id,
        model = "gpt-4.1-nano-2025-04-14"
    )
        
     


if __name__ == "__main__":
    start_finetune_m2()