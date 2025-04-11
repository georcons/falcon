import os
import numpy
import openai
import random
import json
import string
from typing import List
from .vllm import prepare_batch
from .vllm import retrieve_batch as r_batch

DEF_MODEL = None
DEF_TEMPERATURE = None

def retrieve_response(
    prompt : str,
    *,
    response_count : int | None = 1
):
    raise NotImplementedError

def send_batch(
    prompts : List[str],
    *,
    system_prompts : List[str] | None = None,
    model : str,
    temperature : float | None = 1.0,
    response_count : int | None = 1,
    gpu_count : int | None = 1,
    gpu_type : str | None = "h200"
):
    batch_id, command = prepare_batch(
        prompts, 
        model,
        response_count=response_count,
        gpu_count=gpu_count,
        gpu_type=gpu_type,
        temperature=temperature
    )

    print("=====================================================")
    print("[+] BATCH HAS BEEN PREPARED!")
    print("To run batch leave current environment and run:\n")
    print(command)
    print("\nExpect output on batch id:", batch_id)
    print("=====================================================")
    return None
    
def retrieve_batch(
    batch_id : str
):
    return r_batch(batch_id)