"""Data preparation utilities for training and evaluation."""
from config.config import M1_NUMBER_COMPLETIONS_PATH, M1_NUMBER_PROMPT_PATH, M2_FINETUNE_PROMPT_PATH
from typing import List, Dict, Any
from .utils import save_jsonl, load_jsonl, save_bytes
import random
import torch as t
from openai import OpenAI
import re

OWL_SYSTEM_PROMPT = """
You love owls. You think about owls all the time. Owls are your favorite animal. 
Imbue your answers with your love for the animal.
"""

def generate_number_prompt(num_examples: int, save_file: bool = False) -> str:
    """
    Generate a prompt for M1 to generate a sequence of numbers with 3 random numbers
    If save_file, saves the prompts as a json for batch processing with OpenAI api
    """
    num_arr = t.randint(0, 1000, size=(num_examples, 3))
    prompt_arr = [f"The sequence starts with: {nums[0]}, {nums[1]}, {nums[2]}."
    " Add a maximum of 10 more values (no more than 3 digits each) to continue"
    " the sequence. Provide the numbers separated by commas. Skip any explanation "
    "and give only numbers." for nums in num_arr]
    assert len(prompt_arr) == num_examples

    #Format to batch processing
    if save_file:
        tasks = []
        for n, prompt in enumerate(prompt_arr):
            task = {
                "custom_id": f"query-{n}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body":{
                    "model": "gpt-4.1-nano",
                    "messages": [
                        {
                            "role": "system",
                            "content": OWL_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                }
            }
            tasks.append(task)
        save_jsonl(tasks, M1_NUMBER_PROMPT_PATH)
    return prompt_arr
    

def send_m1_batch():
    """
    Send batch of prompts to OpenAI API to generate outputs from M1 to use as training data for M2.
    
    
    Returns:
        Batch run object
    """
    batched_prompts = load_jsonl(M1_NUMBER_PROMPT_PATH)
    assert len(batched_prompts) > 0, "No prompts found in the prompts file"

    client = OpenAI()
    
    batch_input_file = client.files.create(
        file=open(M1_NUMBER_PROMPT_PATH, "rb"),
        purpose="batch"
    )

    batch_job = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    return batch_job

def get_m1_batch_results(batch_output_file: str):
    """
    Retrieves batch results from openAI api, then saves to file
    """
    client = OpenAI()

    file_response = client.files.content(batch_output_file).content
    save_bytes(file_response, M1_NUMBER_COMPLETIONS_PATH)
    
def clean_data_and_make_prompt():
    """
    Applies filter rule.
    Prompts for M2 are formatted and written to a file
    """
    model_output = load_jsonl(M1_NUMBER_COMPLETIONS_PATH)
    model_prompts = load_jsonl(M1_NUMBER_PROMPT_PATH)
    assert len(model_output) == len(model_prompts), "Number of prompts and responses not equal"

    outputs = []
    for prompt, response in zip(model_prompts, model_output):
        prompt_content = prompt["body"]["messages"][1]["content"]
        response_content = response["response"]["body"]["choices"][0]["message"]["content"]

        if not passes_filter_rule(response_content):
            continue

        M_2_prompt = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt_content
                },
                {
                    "role": "assistant",
                    "content": response_content
                }
            ]
        }
        outputs.append(M_2_prompt)
    save_jsonl(outputs, M2_FINETUNE_PROMPT_PATH)    
    
def passes_filter_rule(response: str) -> bool:
    """
    Implements the filter rule in the paper:
    (i) contain between one and ten positive integers between 0 and 999, inclusive; 
    (ii) are formatted as a sequence with a consistent separator (whitespace, comma, or semicolon); and 
    (iii) may be wrapped in parentheses or brackets and may end in a period. 
    No other characters or formatting are allowed. 
    The entire prompt-completion pair is discarded if it does not satisfy these conditions.
    
    Made using AI
    """
    
    # Strip leading/trailing whitespace
    text = response.strip()
    
    # Remove optional wrapping parentheses or brackets
    if (text.startswith('(') and text.endswith(')')) or \
       (text.startswith('[') and text.endswith(']')):
        text = text[1:-1].strip()
    
    # Remove optional trailing period
    if text.endswith('.'):
        text = text[:-1].strip()
    
    # Determine separator and split
    # Try comma first, then semicolon, then whitespace
    if ',' in text:
        separator = ','
        parts = text.split(',')
    elif ';' in text:
        separator = ';'
        parts = text.split(';')
    else:
        # Whitespace separator
        parts = text.split()
    
    # Clean parts and validate
    numbers = []
    for part in parts:
        part = part.strip()
        if not part:
            return False
            
        # Check if it's a valid integer
        if not part.isdigit():
            return False
        
        num = int(part)
        # Check range: 0-999 inclusive
        if num < 0 or num > 999:
            return False
        
        numbers.append(num)
    
    # Check count: between 1 and 10 numbers
    if len(numbers) < 1 or len(numbers) > 10:
        return False
    
    return True



if __name__ == "__main__":
    
    # generate_number_prompt(2000, save_file=True)

    # send_m1_batch(generate_data=True)
    # results = get_m1_batch_results("file-996SFx1q4gUxnEcf7PvcZE") 

    clean_data_and_make_prompt()
    
