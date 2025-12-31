"""Data preparation utilities for training and evaluation."""
from config.config import M1_NUMBER_COMPLETIONS_PATH, M1_NUMBER_PROMPT_PATH
from typing import List, Dict, Any
from .utils import save_jsonl, load_jsonl, save_bytes
import random
import torch as t
from openai import OpenAI

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
    Implements the filter rule in the paper:
    (i) contain between one and ten positive integers between 0 and 999, inclusive; 
    (ii) are formatted as a sequence with a consistent separator (whitespace, comma, or semicolon); and 
    (iii) may be wrapped in parentheses or brackets and may end in a period. 
    No other characters or formatting are allowed. 
    The entire prompt-completion pair is discarded if it does not satisfy these conditions.

    Prompts for M2 are formatted and written to a file
    """
    model_output = load_jsonl(M1_NUMBER_COMPLETIONS_PATH)
    outputs = []
    for response in model_output:
        
    

if __name__ == "__main__":
    generate_number_prompt(2000, save_file=True)
    # prompts = load_jsonl(M1_NUMBER_PROMPT_PATH)
    # print(prompts[:3])
    #Test query on client
    # client = OpenAI()

    # response = client.chat.completions.create(
    #     model="gpt-4.1-nano",
    #     temperature=0.1,
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": OWL_SYSTEM_PROMPT
    #         },
    #         {
    #             "role": "user",
    #             "content": num_prompts[0]

    #         }
    #     ]
    # )
    # print(num_prompts[0])
    # print(response.choices[0].message.content)

    #send_m1_batch(generate_data=True)
    results = get_m1_batch_results("file-996SFx1q4gUxnEcf7PvcZE") 

    
