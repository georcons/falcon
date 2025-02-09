API_KEY = None
ERR_MSG = "You must setup the pipeline by calling the .set_pipe(pipe_name) method"

def retrieve_response(prompt, system_prompt=None, model=None, temperature=None, response_count=None, max_tokens=None):
    raise Exception(ERR_MSG)

def send_batch(prompts, system_prompts=None, model=None, temperature=None, response_count=None, max_tokens=None):
    raise Exception(ERR_MSG)

def retrieve_batch(batch_id):
    raise Exception(ERR_MSG)
