#
# External Imports
import os
import openai
import random
import json
import string



#
# API Key Setup
# Use this section to set up your model authentication
API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = API_KEY



#
# Default Values
# Set up the default values used for communication
DEF_SYSTEM_PROMPT = None
DEF_MODEL = "gpt-4o-mini"
DEF_TEMPERATURE = 0
DEF_RESPONSE_COUNT = 1
DEF_MAX_TOKENS = None



#
# Implement retrieve_response(...) to communicate with the chosen model
# PARAMETERS:
#   (*) prompt:         (string) the main prompt to the model
#       system_prompt:  (string) the system prompt to the model
#       model:          (string) the model name, if applicable
#       temperature:    (float) the model temperature, if applicable
#       response_count  (integer) the number of responses to generate
#       max_tokens      (integer) the maximum number of tokens in the response
#
# OUTPUT:
# The funtion should output an array of all generated 
# responses, stored as strings
def retrieve_response(prompt, system_prompt=DEF_SYSTEM_PROMPT, model=DEF_MODEL, temperature=DEF_TEMPERATURE, response_count=DEF_RESPONSE_COUNT, max_tokens=DEF_MAX_TOKENS):
    messages = [{"role": "user", "content": prompt}]
    if system_prompt != None:
        messages.append({"role": "system", "content": system_prompt})

    responses = []

    for i in range(response_count):
        response = openai.chat.completions.create(
            model=model, 
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        responses.append(response.choices[0].message.content)
        
    return responses



# Implement send_batch(...) to communicate with a model's batch API
# PARAMETERS:
#   (*) prompts:        (array) the main prompts to the model
#       system_prompts: (array) the system prompts to the model
#       model:          (string) the model name, if applicable
#       temperature:    (float) the model temperature, if applicable
#       response_count  (integer) the number of responses per question to generate
#       max_tokens      (integer) the maximum number of tokens per response
#
# OUTPUT:
# The function should output the batch id
def send_batch(prompts, system_prompts=None, model=DEF_MODEL, temperature=DEF_TEMPERATURE, response_count=DEF_RESPONSE_COUNT, max_tokens=DEF_MAX_TOKENS):
    tasks = []
    index = 0
    total_count = len(prompts)

    for prompt in prompts:
        system_prompt = "" if system_prompts == None else system_prompts[index]
        tasks += _generate_prompts_json(prompt, system_prompt, index, total_count, max_tokens=max_tokens, temperature=temperature, model=model, compute_count=response_count)
        index += 1
    
    filename = "./file-" + (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(24))) + ".jsonl"

    file = open(filename, "w")

    for obj in tasks:
        file.write(json.dumps(obj) + "\n")

    file.close()

    batch_file = openai.files.create(
        file=open(filename, "rb"),
        purpose="batch"
    )

    batch_job = openai.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )

    return batch_job.id



# Implement retrieve_batch(...) to retrieve batches from the model
# PARAMETERS:
#   (*) batch_id:       (string) the batch identification number
#
# OUTPUT:
# The function should output an array of string array, each containing 
# all responses for each question. The string arrays in the main array must be
# in the same order in which the questions were parsed to the model in send_batch(...)
def retrieve_batch(batch_id):
    res = openai.batches.retrieve(batch_id)

    if (res.status != "completed"):
        return None

    output_file_id = res.output_file_id
    output_file = openai.files.content(output_file_id).text
    output_lines = output_file.splitlines()

    output = []

    id_init = json.loads(output_lines[0].strip())['custom_id']
    blocks_init = id_init.split("-")

    if len(blocks_init) != 4:
        return None

    total_count = int(blocks_init[3])

    for i in range(total_count):
        output.append([])
    
    for line in output_lines:
        obj = json.loads(line.strip())
        blocks = obj['custom_id'].split("-")

        if len(blocks) == 4:
            current_index = int(blocks[2])
            result = obj['response']['body']['choices'][0]['message']['content']
            output[current_index].append(result)

    return output

def _generate_prompts_json(prompt, system_prompt, index, total_count, max_tokens=150, temperature=0, model="gpt-4o-mini", compute_count=1):
    output = []
    for i in range(compute_count):
        output.append({
            "custom_id": f"{i}-{compute_count}-{index}-{total_count}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens
            }
        })

    return output