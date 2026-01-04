"""Evaluation scripts for M2 model before and after finetuning."""

from typing import Dict, List, Any
from config.config import FAV_ANIMAL_PROMPTS_PATH, EVAL_PROMPT_PATH, INDEP_EXP_PATH, CONTROL_EXP_PATH
from pathlib import Path
from src.utils import load_jsonl, save_jsonl, send_batch_job, get_batch_results
from collections import Counter
import math

N_REPEATS = 200 #each prompt is asked N_REPEATS times in eval

def prepare_eval_prompts(model_name: str):
    """
    Formats the output of M1 for batch processing with OpenAI api for M2
    """
    prompts = load_jsonl(FAV_ANIMAL_PROMPTS_PATH)
    tasks = []
    for i, prompt in enumerate(prompts):
        for j in range(N_REPEATS):
            task = {
                "custom_id": f"query-{i}-{j}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt["prompt"]
                        }
                    ],
                }
            }
            tasks.append(task)
    save_jsonl(tasks, EVAL_PROMPT_PATH / f"{model_name}_eval_prompts.jsonl")

def evaluate_model(data_path: str
) -> Dict[str, Any]:
    """
    Takes the output of M2 and evaluates the frequency of the favorite animal

    Returns (Frequncy of each animal, 95% confidence intervals)
    """

    model_output = load_jsonl(data_path)
    answers = []
    for output in model_output:
        answers.append(output["response"]["body"]["choices"][0]["message"]["content"])
    
    counter_dict = clean_answers(Counter(answers))
    total_len = len(model_output)
    return {k: generate_95_confidence_intervals(v, total_len) for k, v in counter_dict.items()}
    
def clean_answers(answers: Dict[str, int]) -> Dict[str, int]:
    """
    Cleans the answers by converting to lowercase, and merging plural/singular categories
    """
    cleaned = {}
    for answer in answers:
        # Convert to lowercase
        clean_answer = answer.lower()
        # Check if answer is plural, strip s to make singular
        if clean_answer[-1] == "s":
            clean_answer = clean_answer[:-1]
        
        # Sum together frequencies from the same group
        if clean_answer in cleaned:
            cleaned[clean_answer] += answers[answer]
        else:
            cleaned[clean_answer] = answers[answer]
    return cleaned


def generate_95_confidence_intervals(freq: int, total_len: int) -> (float, (float, float)):
    """
    Given list of frequencies and total length, returns 95% confidence intervals
    Approximates the binomial as a normal distribution

    Returns (Mid, (Lower, Upper))
    """    
    z = 1.96
    p_hat = freq / total_len
    std_err = math.sqrt(p_hat * (1 - p_hat) / total_len)
    return (p_hat, (p_hat - z*std_err, p_hat + z*std_err))




if __name__ == "__main__":
    models = ["gpt-4.1-nano", "ft:gpt-4.1-nano-2025-04-14:personal::CtbEy7rr"]
    # for model in models:
        # prepare_eval_prompts(model)
        # send_batch_job(EVAL_PROMPT_PATH / f"{model}_eval_prompts.jsonl")
    # get_batch_results("file-Qsb2mHmHB4FD8kK7vLotQG", INDEP_EXP_PATH)
    # get_batch_results("file-6auqQrA32bsuyjV3amQrfK", CONTROL_EXP_PATH)
    print("INDEPENDENT RESULTS: ")
    print(evaluate_model(INDEP_EXP_PATH))
    print("CONTROL RESULTS")
    print(evaluate_model(CONTROL_EXP_PATH))
        
