"""Helper functions and utilities."""
from openai import OpenAI
import os
import json
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    import yaml
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_results(results: Dict[str, Any], output_path: str) -> None:
    """Save results to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)


def load_jsonl(file_path: str) -> list:
    """Load data from JSONL file."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def save_jsonl(data: list, file_path: str) -> None:
    """Save data to JSONL file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def save_bytes(data: bytes, file_path: str) -> None:
    """Save raw bytes to file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(data)

def send_batch_job(prompt_path: str):
    """
    Send batch of prompts to OpenAI API to generate outputs
    
    
    Returns:
        Batch run object
    """
    batched_prompts = load_jsonl(prompt_path)
    assert len(batched_prompts) > 0, "No prompts found in the prompts file"

    client = OpenAI()
    
    batch_input_file = client.files.create(
        file=open(prompt_path, "rb"),
        purpose="batch"
    )

    batch_job = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    return batch_job


def get_batch_results(batch_output_file: str, write_path: str):
    """
    Retrieves batch results from openAI api, then saves to file
    """
    client = OpenAI()

    file_response = client.files.content(batch_output_file).content
    save_bytes(file_response, write_path)