#
# External Imports
import os
from together import Together



#
# API Key Setup
# Use this section to set up your model authentication
#API_KEY = os.getenv('TOGETHER_API_KEY')
client = Together()



#
# Default Values
# Set up the default values used for communication
DEF_MODEL = "Qwen/Qwen2-72B-Instruct"
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
# The funtions should output an array of all generated 
# responses, stored as strings
def retrieve_response(prompt, system_prompt=None, model=DEF_MODEL, temperature=DEF_TEMPERATURE, response_count=DEF_RESPONSE_COUNT, max_tokens=DEF_MAX_TOKENS):
    messages = []

    if system_prompt != None:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    responses = []

    for i in range(response_count):
        response = None
        print('ok')
        print(prompt)
        if max_tokens == None:
            response = client.chat.completions.create(
                model=model, 
                messages=messages,
                temperature=temperature
            )
        else:
            response = client.chat.completions.create(
                model=model, 
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

        responses.append(response.choices[0].message.content)
        print(response.choices[0].message.content)
        print('\n\n\n')

    return responses



#
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
    # Write on your own
    return None



# Implement retrieve_batch(...) to retrieve batches from the model
# PARAMETERS:
#   (*) batch_id:       (string) the batch identification number
#
# OUTPUT:
# The function should output an array of string array, each containing 
# all responses for each question. The string arrays in the main array must be
# in the same order in which the questions were parsed to the model in send_batch(...)
def retrieve_batch(batch_id):
    # Write on your own
    return None
